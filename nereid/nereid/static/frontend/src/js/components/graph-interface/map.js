import d3 from "../../lib/d3.js";
import store from "../../lib/state.js";
import { get } from "../../lib/util.js";

import Component from "../base/component.js";

export default class Map extends Component {
  constructor(options) {
    super({ store, id: options.id });
    let self = this;

    self.store.events.subscribe("isMapMode", () => self.toggleMapMode());
    self.store.events.subscribe("changedTransform", (d) => self.zoomed(d));

    self.svg = options.svg;

    self.initialScale = get(self, "store.state.initialScale"); //1 << 18;
    self._k = {};
    self.initialCenter =
      get(self, "store.state.config.project_spatial_data.app.centroid") ||
      get(self, "store.state.initialCenter"); //[-117.16107, 32.711518];
    self.tilesize = 256; //256
    // height = 600,
    // width = 800,

    self._current_point;
    self._zoomed = false;
    // _transform = {},
    self.url = (x, y, z) =>
      // `https://stamen-tiles-${
      //   "abc"[Math.abs(x + y) % 3]
      // }.a.ssl.fastly.net/terrain/${z}/${x}/${y}${
      //   devicePixelRatio > 1 ? "@2x" : ""
      // }.png`;
      `https://${
        "abc"[Math.abs(x + y) % 3]
      }.basemaps.cartocdn.com/rastertiles/voyager/${z}/${x}/${y}${
        devicePixelRatio > 1 ? "@2x" : ""
      }.png`;
    // `https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/${z}/${y}/${x}`;

    self.projection = d3
      .geoMercator()
      .scale(1 / (2 * Math.PI))
      .translate([0, 0]);

    self.store.dispatch("setProjection", { projection: self.projection });

    self.transform = d3.zoomIdentity
      .translate(self.projection([0, 0])[0], self.projection([0, 0])[1])
      .scale(self.projection.scale() * 2 * Math.PI);
    self.store.dispatch("setTransform", { transform: self.transform });

    self.renderer = d3.geoPath(self.projection);

    self.tile = d3
      .tile()
      .extent([
        [0, 0],
        [self.width(), self.height()],
      ])
      .tileSize(self.tilesize);

    self.image_bg = self.svg
      .append("svg:g")
      .classed("bg basemap", true)
      .attr("pointer-events", "none")
      .style("overflow", "hidden")
      .attr("pointer-events", "none")
      .classed("hidden", !self.store.state.map_mode)
      .selectAll("image");

    self.image_fg = self.svg
      .append("svg:g")
      .classed("fg basemap", true)
      .attr("pointer-events", "none")
      .style("overflow", "hidden")
      // .attr("id", "images")
      .classed("hidden", !self.store.state.map_mode)
      .selectAll("image");

    self.image_group = self.svg.selectAll(".basemap");

    self.vector = self.svg
      .append("svg:g")
      .attr("id", "vectors")
      .attr("pointer-events", "none");

    self.zoom = d3
      .zoom()
      .scaleExtent([1 << 6, 1 << 30])
      .extent([
        [0, 0],
        [self.width(), self.height()],
      ])
      // .clickDistance(0)
      .filter(
        () => !self.drag_lock //true //!_current_point
        // !d3.select("svg").classed("no-zoom") && !d3.select("svg").classed("ctrl")
      )
      .on("start", (e) => {})
      .on("zoom", (e) => {
        self.store.dispatch("changedTransform", { transform: e.transform });
      })
      .on("end", (e) => {
        self.store.dispatch("changedZoomTransform", {
          zoomTransform: self.zoom.transform,
        });
      });
  }

  width = () => d3.select(`#${this.id}`).node().getBoundingClientRect().width;
  height = () => d3.select(`#${this.id}`).node().getBoundingClientRect().height;
  // getScale = () => (fixedScale() ? this._k / this.initialScale : 1);

  get drag_lock() {
    return get(this, "store.state.drag_lock");
  }

  toggleMapMode() {
    let self = this;
    self.image_group.classed("hidden", !self.store.state.map_mode);
    console.debug("map mode toggled!");
  }

  resize() {
    let self = this;
    self.tile = d3
      .tile()
      .extent([
        [0, 0],
        [self.width(), self.height()],
      ])
      .tileSize(self.tilesize);

    const tiles = self.tile(self.transform);
    // image_group.classed("hidden", !showMap());
    // if (showMap()) {

    self.image_bg = self.image_bg
      .data(tiles, (d) => d)
      .join("image")
      .attr("xlink:href", (d) => self.url(...d))
      .attr("x", ([x]) => (x + tiles.translate[0]) * tiles.scale - 0.5)
      .attr("y", ([, y]) => (y + tiles.translate[1]) * tiles.scale - 0.5)
      .attr("width", tiles.scale + 1)
      .attr("height", tiles.scale + 1);

    self.image_fg = self.image_fg
      .data(tiles, (d) => d)
      .join("image")
      .attr("xlink:href", (d) => self.url(...d))
      .attr("x", ([x]) => (x + tiles.translate[0]) * tiles.scale)
      .attr("y", ([, y]) => (y + tiles.translate[1]) * tiles.scale)
      .attr("width", tiles.scale)
      .attr("height", tiles.scale);
  }

  zoomed({ transform }) {
    let self = this;

    self.transform = transform;
    self._k = transform.k;
    // console.log(_k);

    self.resize();

    self.vector.attr("transform", transform);
  }

  _render() {
    // console.log(this.width(), this.height(), this.store);
    let self = this;

    self.svg.call(self.zoom).call(
      self.zoom.transform,
      // transform
      d3.zoomIdentity
        .translate(self.width() / 2, self.height() / 2)
        .scale(-self.initialScale)
        .translate(...self.projection(self.initialCenter))
        .scale(-1)
    );
  }
}
