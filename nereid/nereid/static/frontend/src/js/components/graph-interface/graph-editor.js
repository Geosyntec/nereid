import Component from "../base/component.js";
import store from "../../lib/state.js";
import * as util from "../../lib/util.js";
import d3 from "../../lib/d3.js";

// import {
//   // pointerToLongLat,
//   distance,
// } from "./util.js";

// import { Graph } from "./graph.js";

export default class GraphEditor extends Component {
  constructor(options) {
    super({ store, id: options.id });
    let self = this;

    // self.store.events.subscribe("isConstNodeArea", () =>
    //   self.toggleConstNodeArea()
    // );
    // self.store.events.subscribe("isAddNodeMode", () =>
    //   self.toggleAddOrMoveNode()
    // );

    self.svg = options.svg;
    self.options = options || {};

    self.default_nodesize = self.options.default_nodesize || 12;

    self.charge = self.options.charge || -300;
    self.edge_distance = self.options.edge_distance || 80;
    self.node_types = self.options.node_types || {};
    self.onNodeSelected =
      typeof self.options.onNodeSelected !== "undefined"
        ? self.options.onNodeSelected
        : function () {};

    self.onNodeUnSelected =
      typeof self.options.onNodeUnSelected !== "undefined"
        ? self.options.onNodeUnSelected
        : function () {};

    //status saves
    self._selected_node_id = null;
    // self._selected_edge = null;
    self._mousedown_edge = null;
    self._mousedown_node = null;
    self._mouseup_node = null;
    self._lastKeyDown = -1;

    self.container = self.svg
      .append("svg:g")
      .classed("graph-editor", true)
      .style("pointer-events", "all");

    // define arrow markers for graph links
    self.container
      .append("svg:defs")
      .append("svg:marker")
      .attr("id", "end-arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 5)
      .attr("markerWidth", 3)
      .attr("markerHeight", 3)
      .attr("orient", "auto")
      .style("fill", "#333")
      .append("svg:path")
      .attr("d", "M0,-5L10,0L0,5");
    // .attr("fill", "#000");

    self.dragLine = self.container
      .append("svg:path")
      .attr("class", "link dragline hidden")
      .attr("d", "M0,0L0,0");

    self.path = self.container.append("svg:g").selectAll("path");
    self.circle = self.container.append("svg:g").selectAll("g");

    self.drag = d3
      .drag()
      // Mac Firefox doesn't distinguish between left/right click when Ctrl is held...
      .filter((event) => event.button === 0 || event.button === 2)
      .on("drag", (event, d) => {
        d.longlat = self.pointToLongLat([event.x, event.y]);
        self.update();
      })
      .on("end", () => self.store.dispatch("stateChange"));

    // events & subscriptions

    d3.select(window)
      .on("mousemove.graph-editor", self.mousemove.bind(self))
      .on("keydown.graph-editor", self.keydown.bind(self))
      .on("keyup.graph-editor", self.keyup.bind(self));

    self.svg
      .on("click.graph-editor", self.mousedown_addNode.bind(self))
      .on("mouseup.graph-editor", self.mouseup.bind(self))
      .on("mouseenter", self.mouseenter.bind(self))
      .on("mouseleave", self.mouseleave.bind(self));
  }
  subscribe() {
    let self = this;
    self.store.events.subscribe("isConstNodeArea", () =>
      self.toggleConstNodeArea()
    );
    self.store.events.subscribe("changedTransform", () => self.update());
    self.store.events.subscribe("editorUpdate", () => {
      self.update();
    });
    self.store.events.subscribe("newGraph", () => {
      self.update();
    });
    self.store.events.subscribe("setRefDataQuery", () => {
      self.update();
    });
    self.store.events.subscribe("setDesignStormQuery", () => {
      self.update();
    });
  }
  get bbox() {
    return this.svg.node().getBoundingClientRect();
  }
  get width() {
    return this.bbox.width;
  }
  get height() {
    return this.bbox.height;
  }
  get transform() {
    return util.get(this, "store.state.transform");
  }
  get projection() {
    return util.get(this, "store.state.projection");
  }
  get editing_mode() {
    return util.get(this, "store.state.graph_edit_mode");
  }
  get graph() {
    return util.get(this, "store.state.graph");
  }

  get_node_by_id(id) {
    return this.graph.nodes.find((n) => n.id === id);
  }

  fixedScale = () => false;
  getScale = () => {
    let self = this;
    return self.fixedScale()
      ? util.get(self, "store.state.transform.k") /
          util.get(self, "store.state.initialScale")
      : 1;
  };
  pointToLongLat(point) {
    let self = this;
    const longlat = self.projection.invert(self.transform.invert(point));

    return longlat;
  }
  longLatToPoint(longlat) {
    let self = this;
    const point = self.transform.apply(self.projection(longlat));
    return point;
  }
  // reprojectLongLat(longlat) {
  //   let self = this;
  //   return self.transform.apply(self.projection(longlat));
  // }
  getLoc = (d) => {
    let self = this;
    return self.longLatToPoint(d.longlat);
    // return window.asPoint ? d.point : self.reprojectLongLat(d.longlat);
  };

  recalculateNodeSize(d) {
    let self = this;
    return (
      Math.max(3, d.size * self.getScale()) *
      (d.id === self._selected_node_id ? 1.3 : 1)
    );

    // let s = self.const_node_area
    //   ? d.size *
    //     (Math.pow(2, self.map.getZoom()) / Math.pow(2, self.map.getMaxZoom()))
    //   : d.size;
    // return s;
  }
  getColor(d) {
    let self = this;
    if (d?.color) return d3.rgb(d.color);
    let node_info = util.get(self.store.state.node_types, d.node_type);
    return d3.rgb(node_info?.color || "lightgrey");
  }

  tick() {
    //update edge position
    let self = this;

    self.path.attr("d", (d) => {
      const deltaX = d.target.x - d.source.x;
      const deltaY = d.target.y - d.source.y;
      const dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      const normX = deltaX / dist;
      const normY = deltaY / dist;
      const sourcePadding = self.recalculateNodeSize(d.source);
      const targetPadding = 5 + self.recalculateNodeSize(d.target);
      // const sourcePadding = d.source.size;
      // const targetPadding = 5 + d.target.size;
      const sourceX = d.source.x + sourcePadding * normX;
      const sourceY = d.source.y + sourcePadding * normY;
      const targetX = d.target.x - targetPadding * normX;
      const targetY = d.target.y - targetPadding * normY;

      if (
        deltaX * (targetX - sourceX) < 0 ||
        deltaY * (targetY - sourceY) < 0
      ) {
        return `M${d.source.x},${d.source.y}L${d.target.x},${d.target.y}`;
      }

      return `M${sourceX},${sourceY}L${targetX},${targetY}`;
    });

    self.circle
      .selectAll(".node")
      // .attr("r", (d) => Math.max(3, d.size * self.getScale()));
      .attr("r", (d) => self.recalculateNodeSize(d) * 0.95);

    self.circle.attr("transform", (d) => `translate(${d.x},${d.y})`);
    // console.log("ran tick");

    // self.redrawMapMarkers();
  }

  getState(coords) {
    let self = this;
    let state_query = util.get(self, "store.state.state_query");
    let state = "undefined";
    let obj;
    if (state_query != null) {
      obj = state_query.features.find((d) => d3.geoContains(d, coords));
      return obj?.properties?.name || "undefined";
    }

    return state;
  }

  getDesignStormDepth(coords) {
    let self = this;
    let state_query = util.get(self, "store.state.design_storm_geojson");
    let state = "undefined";
    let obj;
    if (state_query != null) {
      obj = state_query.features.find((d) => d3.geoContains(d, coords));
      return obj?.properties?.[state_query._field];
    }

    return;
  }

  getRefDataKey(coords) {
    let self = this;
    let state_query = util.get(self, "store.state.ref_data_key_geojson");
    let state = "undefined";
    let obj;
    if (state_query != null) {
      obj = state_query.features.find((d) => d3.geoContains(d, coords));
      return obj?.properties?.[state_query._field];
    }

    return;
  }

  setNodeDefaults(nodes) {
    let self = this;
    nodes.map((d) =>
      d?.size ? d : Object.assign(d, { size: self.default_nodesize })
    );

    nodes.map((d) =>
      d?.longlat
        ? d
        : Object.assign(d, { longlat: self.pointToLongLat([d.x, d.y]) })
    );

    nodes.map((n) => {
      let [x, y] = self.longLatToPoint(n.longlat);
      n.x = x;
      n.y = y;
      return n;
    });

    nodes.map((n) => {
      n.state = self.getState(n.longlat);
      return n;
    });

    nodes.map((n) => {
      if (!n?.node_type?.includes("land_surface")) {
        let design_storm_depth = self.getDesignStormDepth(n.longlat);
        if (design_storm_depth == null) {
          return n;
        }
        n.design_storm_depth_inches =
          +parseFloat(design_storm_depth).toFixed(2);
        if (n?.data) {
          n.data.design_storm_depth_inches = n.design_storm_depth_inches;
        }
      }
      return n;
    });

    nodes.map((n) => {
      if (!n?.node_type?.includes("land_surface")) {
        let ref_data_key = self.getRefDataKey(n.longlat);
        if (ref_data_key == null) {
          return n;
        }
        n.ref_data_key = ref_data_key;
        if (n?.data) {
          n.data.ref_data_key = n.ref_data_key;
        }
      }
      return n;
    });
  }

  update() {
    let self = this,
      nodes;

    nodes = self.graph.nodes;

    self.setNodeDefaults(nodes);

    // console.log({ nodes, edges: self.graph.edges });

    self.path = self.path.data(self.graph.edges);

    // update existing links
    self.path
      .classed("selected", (d) => d === self._selected_edge)
      .style("marker-end", "url(#end-arrow)");

    // remove old links
    self.path.exit().remove();

    // add new links
    self.path = self.path
      .enter()
      .append("svg:path")
      .classed("link", true)
      .classed("selected", (d) => d === self._selected_edge)
      .style("marker-end", "url(#end-arrow)")
      // .style("stroke", (d) => d3.gray(51))

      .on("mousedown", (event, d) => {
        if (event.ctrlKey) return;

        // select link
        self._mousedown_edge = d;
        self._selected_edge =
          self._mousedown_edge === self._selected_edge
            ? null
            : self._mousedown_edge;

        self._selected_node_id = null;
        self.update();
      })
      .merge(self.path);

    // circle (node) group
    // the function arg is crucial here! nodes are known by id, not by index!
    self.circle = self.circle.data(nodes, (d) => JSON.stringify(d));

    // update existing nodes (selected visual states)
    self.circle
      .selectAll(".node")
      // .transition()
      // .attr("class", (d) => "node " + (d.node_type || ""))

      .attr(
        "r",
        (d) => self.recalculateNodeSize(d) //- 15
        // d.size *
        // (Math.pow(2, self.map.getZoom()) / Math.pow(2, self.map.getMaxZoom()))
      )
      .style("fill", (d) => {
        let c = self.getColor(d);
        return d.id === self._selected_node_id ? c.brighter(3) : c;
      })
      .style("stroke", (d) => self.getColor(d).darker().toString());

    // update text
    self.circle.selectAll("text").text((d) => d.id);

    // remove old nodes
    self.circle.exit().remove();

    // add new nodes
    // https://stackoverflow.com/questions/20708442/d3-js-chart-not-updated-with-new-data
    const g = self.circle.enter().append("svg:g");

    g.append("circle")
      .classed("node has-tooltip", true)
      .attr(
        "r",
        (d) => self.recalculateNodeSize(d) //- 15
        // d.size *
        // (Math.pow(2, self.map.getZoom()) / Math.pow(2, self.map.getMaxZoom()))
      )
      .style("fill", (d) => {
        let c = self.getColor(d);
        return d.id === self._selected_node_id ? c.brighter(3) : c;
      })
      .style("stroke", (d) => self.getColor(d).darker().toString())

      // .attr("class", (d) => "node " + (d.node_type || ""))
      // .attr(
      //   "r",
      //   (d) => self.recalculateNodeSize(d) - 15
      //   // d.size *
      //   // (Math.pow(2, self.map.getZoom()) / Math.pow(2, self.map.getMaxZoom()))
      // )
      // // .attr("r", (d) => d.size || self.default_nodesize)
      // .style("fill", (d) => {
      //   let c = self.getColor(d);
      //   return d === self._selected_node ? c.brighter() : c;
      // })
      // .style("stroke", (d) => self.getColor(d).darker().toString())

      .on("mouseover", function (event, d) {
        self._hovered_node = d;
        self.store.dispatch("isNodeHovered", { node_hovered: d.id });

        if (
          !self._selected_node_id &&
          !(util.get(self, "store.state.current_node_data.id") === d.id)
        ) {
          // only change with hover if there's no node currently selected.
          // self.tooltip_show(d);
          // self.store.dispatch("currentNodeData", { current_node_data: d });
          // self.tooltip_move(d);
        }

        if (!self._mousedown_node || d.id === self._mousedown_node.id) return;
        // enlarge target node
        d3.select(event.target).attr("transform", "scale(1.25)");
      })
      .on("mouseout", (event, d) => {
        self._hovered_node = undefined;
        self.store.dispatch("isNodeHovered", { node_hovered: undefined });
        // self.tooltip_hide();
        if (!self._mousedown_node || d.id === self._mousedown_node.id) return;
        // unenlarge target node
        d3.select(event.target).attr("transform", "");
      })
      .on("mousedown", (event, d) => {
        // console.log("fired circle mousedown");
        if (event.shiftKey || event.ctrlKey) return;
        self.store.dispatch("drag_lock", { drag_lock: true });
        // self.map.dragging.disable();

        // select node
        self._mousedown_node = d;

        if (self._mousedown_node.id === self._selected_node_id) {
          self._selected_node_id = null;
          self.onNodeUnSelected(d);
          // store.dispatch("currentNodeData", { current_node_data: undefined });
          self.store.dispatch("changedSelectedNode", {
            selected_node_id: null,
          });
        } else {
          self._selected_node_id = self._mousedown_node.id;
          // self.tooltip_show(d);
          // store.dispatch("currentNodeData", { current_node_data: d });

          store.dispatch("changedSelectedNode", {
            selected_node_id: d.id,
          }); // weird resize observer error here on changed selected node event, maybe due to config panel

          // self.tooltip_move(d);
          self.onNodeSelected(d);
        }
        self._selected_edge = null;

        // reposition drag line

        // self.dragLine
        //   .style("marker-end", "url(#end-arrow)")
        //   .classed("hidden", false)
        //   .attr(
        //     "d",
        //     `M${self._mousedown_node.x},${self._mousedown_node.y}L${self._mousedown_node.x},${self._mousedown_node.y}`
        //   );

        self.update();
      })
      // .on("wheel", (event, d) => {
      //   d3.event.preventDefault();
      //   console.log("scrolling", d.id);
      // })
      .on("mouseup", (event, d) => {
        // needed by FF
        self.dragLine.classed("hidden", true).style("marker-end", "");
        // release drag lock.
        self.store.dispatch("drag_lock", { drag_lock: false });
        // self.map.dragging.enable();
        if (!self._mousedown_node || !self.editing_mode) return;

        // check for drag-to-self
        self._mouseup_node = d;

        if (self._mouseup_node.id === self._mousedown_node.id) {
          self.resetMouseVars();
          return;
        }

        // unenlarge target node
        d3.select(event.target).attr("transform", "");

        // add link to graph (update if exists)
        const source = self._mousedown_node.id;
        const target = self._mouseup_node.id;

        const link = self.graph.edges.find(
          (l) => l.source === source && l.target === target
        );
        if (link) {
          // link[isRight ? "right" : "left"] = true;
        } else {
          let s = self.graph.nodes.find((n) => n.id === source);
          let t = self.graph.nodes.find((n) => n.id === target);
          // self.graph.edges.push({ source, target });
          self.graph.edges.push({ source: s, target: t });
        }

        // select new link
        self._selected_edge = link;
        self._selected_node_id = null;
        self.update();
      });

    // show node IDs
    g.append("text")
      .attr("x", 0)
      .attr("y", "0.3rem")
      .attr(
        "class",
        "id no-select align-middle text-center font-bold text-base pointer-events-none"
      )
      .text((d) => d.id);

    self.circle = g.merge(self.circle);

    self.tick();
    // console.log("ran update");
  }

  zoom_to_group(iters) {
    // console.log("z to g");
    let self = this;
    const bb = self.container.node().getBBox();
    // console.log(bb);
    const [[x0, y0], [x1, y1]] = [
      [bb.x, bb.y],
      [bb.x + bb.width, bb.y + bb.height],
    ];

    if (iters == null) {
      iters = 1;
    }

    let scale = self.transform.k;

    while (iters > 0) {
      iters -= 1;
      scale = Math.min(
        1 << 28,
        scale *
          (0.9 / Math.max((x1 - x0) / self.width, (y1 - y0) / self.height))
      );
    }

    const new_center = [x0 + bb.width / 2, y0 + bb.height / 2];

    let zoom_transform = util.get(self, "store.state.zoomTransform");

    self.svg
      .interrupt()
      .transition()
      .duration(800)
      .call(
        zoom_transform,
        d3.zoomIdentity
          .translate(self.width / 2, self.height / 2)
          .scale(-scale)
          .translate(...self.transform.invert(new_center))
          .scale(-1)
      );
  }

  // window keyboard events

  mouseenter() {
    this.svg.classed("listening-to-keys", true);
  }

  mouseleave() {
    this.svg.classed("listening-to-keys", false);
  }

  keydown(event) {
    let self = this;

    // presses are related to editor pane
    if (!self.svg.classed("listening-to-keys")) return;

    if (event.keyCode === 90) {
      // z
      // self.reset();
    }

    if (event.keyCode === 71) {
      // g
      self.zoom_to_group();
    }

    // presses are related to editor mode
    if (!self.editing_mode) return;

    // dragging support
    if (event.keyCode === 17) {
      self.circle.call(self.drag);
      self.svg.classed("ctrl", true);
      return;
    }

    // presses are related to the selected editor item
    if (!this._selected_node_id && !this._selected_edge) return;

    switch (event.keyCode) {
      case 8: // backspace
      case 46: // delete
        if (this._selected_node_id) {
          this.graph.nodes.splice(
            this.graph.nodes.map((n) => n.id).indexOf(this._selected_node_id),
            1
          );
          this.graph.spliceLinksForNode(this._selected_node_id);
        } else if (this._selected_edge) {
          this.graph.edges.splice(
            this.graph.edges.indexOf(this._selected_edge),
            1
          );
        }
        this._selected_edge = null;
        this._selected_node_id = null;
        self.store.dispatch("changedSelectedNode", {
          selected_node_id: null,
        });
        this.resetMouseVars();

        this.update();
        break;
    }
  }

  keyup(event) {
    let self = this;
    // this._lastKeyDown = -1;
    // d3.select(`#${this.id}`).style("pointer-events", "none");

    // ctrl
    if (event.keyCode === 17) {
      self.circle.on(".drag", null);
      self.svg.classed("ctrl", false);
      // _current_point = undefined;
    }
  }

  // window mouse events

  mousedown_addNode(event) {
    // console.log("fire add node");
    let self = this;
    // because :active only works in WebKit?
    this.svg.classed("active", true);

    // console.log(self._mousedown_node, self._mousedown_edge);

    if (
      event.shiftKey ||
      event.ctrlKey ||
      !self.editing_mode ||
      self._mousedown_node ||
      self._mousedown_edge ||
      self._hovered_node
    ) {
      // console.log("add node cancelled");
      self.resetMouseVars();
      return;
    }

    // console.log("add node");

    // insert new node at point
    const point = d3.pointer(event); //this.container.node());
    let [x, y] = point;
    let coords = self.pointToLongLat([x, y]);

    // console.log("clicked point", point);
    const node = {
      id: util.randomString(5),
      // reflexive: false,
      x: x,
      y: y,
      size: self.default_nodesize,
      longlat: coords,
    };

    node.design_storm_depth_inches = +parseFloat(
      self.getDesignStormDepth(node.longlat)
    ).toFixed(2);

    node.ref_data_key = self.getRefDataKey(node.longlat);

    this.graph.nodes.push(
      node
      // Object.assign(node, self.map.containerPointToLatLng(node))
      // Object.assign(node, self.map.layerPointToLatLng(node))
    );

    self.store.dispatch("changedSelectedNode", {
      selected_node_id: node.id,
    });
    self._selected_node_id = this.graph.nodes.find((n) => n.id === node.id)?.id;
    self.update();
    // self.force.restart();
    // console.log("added", node);
    // this.onNodeSelected(node);
    self.mouseup();
  }

  mouseup() {
    // because :active only works in WebKit?
    this.svg.classed("active", false);

    if (this._mousedown_node) {
      // hide drag line
      this.dragLine.classed("hidden", true).style("marker-end", "");
      return;
    }

    // clear mouse event vars
    this.resetMouseVars();
  }

  mousemove(event) {
    let self = this;
    if (!this._mousedown_node || !this.editing_mode) return;

    let { x, y } = util
      .get(this, "store.state.graph.nodes")
      .find((n) => n.id === this._mousedown_node.id);

    // update drag line
    self.dragLine
      .style("marker-end", "url(#end-arrow)")
      .classed("hidden", false)
      .attr(
        "d",
        `M${self._mousedown_node.x},${self._mousedown_node.y}L${self._mousedown_node.x},${self._mousedown_node.y}`
      );
    const point = d3.pointer(event, this.container.node());
    this.dragLine.attr("d", `M${x},${y}L${point[0]},${point[1]}`);
  }

  resetMouseVars() {
    // console.log("resetting mouse vars");
    this._mousedown_node = null;
    this._mouseup_node = null;
    this._mousedown_edge = null;
  }

  // Rendering

  _render() {
    let self = this;
    self.subscribe();
    self.update();
    self.zoom_to_group();
  }
}
