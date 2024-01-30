import d3 from "../../lib/d3.js";
// import * as topojson from "topojson-client";
// import * as api from "../../lib/nereid-api";
import * as util from "../../lib/util.js";
import VectorLayer from "../base/vector-layer.js";

export default class RefDataVectors extends VectorLayer {
  constructor({ vector }) {
    super({ vector });
    let self = this;
    self.stroke_width = 1;
    self.store.events.subscribe("changedTransform", () => {
      self.group
        .selectAll("path")
        .style("stroke-width", self.stroke_width / self.transform.k);
    });

    self.store.events.subscribe("isShowRainZones", async () => {
      let geojson = util.get(self, "store.state.ref_data_key_geojson");
      if (!geojson) {
        await self.load_data();
        return;
      }
      self._draw(geojson);
    });
    self.store.events.subscribe("setRefDataQuery", ({ ref_data_key_geojson }) =>
      self._draw(ref_data_key_geojson)
    );
  }

  get hidden() {
    return !util.get(this, "store.state.show_rain_zone");
  }

  async load_data() {
    let self = this;
    let cfg = util.get(self.store, "state.config");
    let info = util.deepCopy(cfg?.project_spatial_data?.ref_data_key);

    await self._load_data(info);

    if (self.geojson) {
      self.store.dispatch("setRefDataQuery", {
        ref_data_key_geojson: self.geojson,
      });
    }
  }

  _draw(geojson) {
    if (!geojson) return;
    let self = this;
    self.group.selectAll("path").remove();
    if (self.hidden) return;

    self.colorScale = d3
      .scaleOrdinal()
      .domain(self.domain)
      .range(d3.schemeSet3);

    self.group
      .selectAll("path")
      .data(geojson.features)
      .enter()
      .append("path")
      .attr("d", self.renderer)
      .attr("pointer-events", "all")
      .attr("fill", (d) => {
        return self.colorScale(d.properties[geojson._field]);
      })
      .attr("stroke", d3.gray(0.2))
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
      .style("stroke-width", self.stroke_width / self.transform.k);
  }

  async _render() {
    let self = this;
    self.store.events.subscribe("updateConfig", self.load_data.bind(self));
  }
}
