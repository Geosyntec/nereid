import d3 from "../../lib/d3.js";
import * as topojson from "topojson-client";
import store from "../../lib/state.js";
import { get } from "../../lib/util.js";

import Component from "../base/component.js";
import { pointerToLongLat, distance } from "./util.js";

export default class Points extends Component {
  constructor(options) {
    return;
    super({ store, id: options.id });
    let self = this;
    self.svg = options.svg;

    self.store.events.subscribe("changedTransform", (d) => self.update_cir());

    self.data = [
      {
        id: 0,
        longlat: get(self, "store.state.initialCenter"),
        size: 50, // pi * radius ** 2
        point: [self.width() / 2, self.height() / 2],
      },
    ];
    self.delaunay = self.updateDelaunay();
    self.delauneySearchRadius = 5;

    self.circle_group = self.svg
      .append("svg:g")
      .attr("id", "circles")
      .classed("points", true);

    self.cir = self.circle_group.selectAll("circle");
    self._current_point;

    self.pointDragHandler = d3
      .drag()
      // Mac Firefox doesn't distinguish between left/right click when Ctrl is held...
      .filter((event) => event.button === 0 || event.button === 2)
      .on("start", (event, d) => null)
      .on("drag", (event, d) => {
        // console.log("dragging");

        // this drag handler is for moving points, so we use the local event rather than the
        d.longlat = pointerToLongLat(self.projection, self.transform, [
          event.x,
          event.y,
        ]);
        self.update_cir();
        self.circle_group.style("opacity", 0.3);
      })
      .on("end", (event, d) => {
        // console.log("drag end");

        self.delaunay = self.updateDelaunay();
        self._current_point = undefined;
        // console.log(d.id, d.longlat);
        self.circle_group.style("opacity", 1);
      });

    // self.svg
    //   .on("click", (e) => {
    //     const longlat = pointerToLongLat(
    //       self.projection,
    //       self.transform,
    //       d3.pointer(e)
    //     );
    //     console.log(longlat);
    //     this.addPoint(longlat);
    //     this._current_point = undefined;
    //   })
    //   .on("mousemove", (event) => self.mousemoved(event));

    d3.select(window)
      .on("keydown.points", self.keydown.bind(self))
      .on("keyup.points", self.keyup.bind(self))
      .on("mousemove.points", () => {})
      .on("mouseup.points", (event) => {
        self._current_point = undefined;
      });
  }
  get transform() {
    return get(this, "store.state.transform");
  }

  get projection() {
    return get(this, "store.state.projection");
  }

  // width = () => d3.select(`#${this.id}`).node().getBoundingClientRect().width;
  width = () => this.svg.node().getBoundingClientRect().width;
  // height = () => d3.select(`#${this.id}`).node().getBoundingClientRect().height;
  height = () => this.svg.node().getBoundingClientRect().height;

  fixedScale = () => false;
  reprojectLongLat(longlat) {
    let self = this;
    return self.transform.apply(self.projection(longlat));
  }
  getLoc = (d) => {
    let self = this;
    return window.asPoint ? d.point : self.reprojectLongLat(d.longlat);
  };
  updateDelaunay = () => {
    let self = this;
    return d3.Delaunay.from(
      self.data,
      (d) => d.longlat[0],
      (d) => d.longlat[1]
      // (d) => getLoc(d)[0],
      // (d) => getLoc(d)[1]
    );
  };

  // let radius = 5;

  find = (mx, my) => {
    let self = this;
    // console.log(self.delaunay);
    const idx = self.delaunay.find(mx, my);
    if (isNaN(idx) || idx == null) return null;
    // console.log(idx);

    const datum = self.data[idx],
      // [_mx, _my] = projection([mx, my]),
      // [px, py] = projection(datum.longlat);

      [_mx, _my] = self.reprojectLongLat([mx, my]),
      [px, py] = self.reprojectLongLat(datum.longlat);
    // [px, py] = getLoc(datum);

    const d = distance(px, py, _mx, _my);
    // console.log(d);
    return d < self.delauneySearchRadius + datum.size * self.getScale()
      ? datum
      : null;
  };

  // let found = null;

  addPoint = (longlat) => {
    console.log("enter add point");

    let self = this;
    if (!get(self, "store.state.add_node_mode")) {
      return;
    }

    let data = self.data;
    if (
      self.svg.classed("no-zoom") ||
      self._current_point
      // ||
      // event.defaultPrevented
      // false
    )
      return;
    // event.preventDefault();
    console.log("adding Point");

    let id = data.length > 0 ? data[data.length - 1].id + 1 : 0;
    let point = [self.width() / 2 + id * 40, self.height() / 2 + id * 40];

    data.push({
      id,
      size: 20,
      longlat,
      point,
    });

    self.delaunay = self.updateDelaunay();

    self.update_cir();
  };

  getScale = () => {
    let self = this;
    return self.fixedScale()
      ? get(self, "store.state.transform.k") /
          get(self, "store.state.initialScale")
      : 1;
  };

  update_cir() {
    let self = this;
    self.cir = self.circle_group
      .selectAll("circle")
      .data(self.data)
      // .join("circle")
      .join(
        (enter) =>
          enter
            .append("circle")
            .classed("points", true)
            .attr("r", (d) => Math.max(3, d.size * self.getScale()))
            // .attr("r", (d) => s(d))
            // .attr("r", (d) => 50)

            // .attr("cy", (d) => projection(d.longlat)[1])
            // .attr("cx", (d) => projection(d.longlat)[0]);
            // .attr("cy", (d) => reprojectLongLat(d.longlat)[1])
            // .attr("cx", (d) => reprojectLongLat(d.longlat)[0]);

            .attr("cy", (d) => self.getLoc(d)[1])
            .attr("cx", (d) => self.getLoc(d)[0]),
        (update) =>
          update.call((update) => {
            // let t = circle_group
            //   .transition()
            //   .duration(pointTransitionDuration());
            update
              // .interrupt()
              // .transition(t)
              .attr("r", (d) => Math.max(3, d.size * self.getScale()))
              // .attr("r", (d) => 50)
              // .attr("r", (d) => s(d))
              .attr("cy", (d) => self.getLoc(d)[1])
              .attr("cx", (d) => self.getLoc(d)[0]);
          })
      )

      // .on("mouseenter", (e, d) => (_current_point = d))
      .on("mousedown", (e, d) => {
        self._current_point = d;
        // svg.classed("no-zoom", true);
        // console.log(_current_point);
        // e.preventDefault();
      });
    // .on("mouseup", () => (_current_point = undefined))

    // .on("mouseleave", () => svg.classed("no-zoom", false))
  }

  reset() {
    let self = this;
    let scale = get(self, "store.state.initialScale");
    let center = get(self, "store.state.initialCenter");
    console.log("reset");
    let zoom_transform = get(self, "store.state.zoomTransform");

    self.svg
      .interrupt()
      .transition()
      .duration(2100)
      .call(
        // zoom.transform,
        zoom_transform,
        d3.zoomIdentity
          .translate(self.width() / 2, self.height() / 2)
          .scale(-scale)
          .translate(...self.projection(center))
          .scale(-1)
      );
  }

  zoom_to_group() {
    console.log("z to g");
    let self = this;
    const bb = self.circle_group.node().getBBox();
    const [[x0, y0], [x1, y1]] = [
      [bb.x, bb.y],
      [bb.x + bb.width, bb.y + bb.height],
    ];

    const scale = Math.min(
      1 << 28,
      self.transform.k *
        (0.9 / Math.max((x1 - x0) / self.width(), (y1 - y0) / self.height()))
    );

    const new_center = [x0 + bb.width / 2, y0 + bb.height / 2];

    let zoom_transform = get(self, "store.state.zoomTransform");

    self.svg
      .interrupt()
      .transition()
      .duration(750)
      .call(
        // zoom.transform,
        zoom_transform,
        d3.zoomIdentity
          .translate(self.width() / 2, self.height() / 2)
          .scale(-scale)
          .translate(...self.transform.invert(new_center))
          .scale(-1)
      );
  }

  keydown(event) {
    let self = this;
    // console.log(event.keyCode);
    // ctrl
    if (event.keyCode === 17) {
      self.cir.call(self.pointDragHandler);
      self.svg.classed("ctrl", true);
      return;
    }

    if (event.keyCode === 90) {
      // z
      self.reset();
    }

    if (event.keyCode === 71) {
      // g
      self.zoom_to_group();
    }
  }

  keyup(event) {
    let self = this;
    // this._lastKeyDown = -1;
    // d3.select(`#${this.id}`).style("pointer-events", "none");

    // ctrl
    if (event.keyCode === 17) {
      self.cir.on(".drag", null);
      self.svg.classed("ctrl", false);
      // _current_point = undefined;
    }
  }

  mousemoved(event) {
    let self = this;
    const [mx, my] = pointerToLongLat(
      self.projection,
      self.transform,
      d3.pointer(event)
    );
    let found = self.find(mx, my);

    self.cir.classed(
      "fill-current text-green-600 opacity-80",
      (d) => found && d.id === found.id
    );
  }

  _render() {
    this.update_cir();
  }
}
