import d3 from "../../lib/d3.js";
import * as util from "../../lib/util.js";
import VectorLayer from "../base/vector-layer.js";

export default class DesignStormVectors extends VectorLayer {
  constructor({ vector }) {
    super({ vector });
    let self = this;

    self.store.events.subscribe("changedTransform", () => {
      self.group
        .selectAll("path")
        .style("stroke-width", self.stroke_width / self.transform.k);
    });

    self.store.events.subscribe("isShowDesignStorm", async () => {
      let geojson = util.get(self, "store.state.design_storm_geojson");
      if (!geojson) {
        await self.load_data();
        return;
      }
      self._draw(geojson);
    });
    self.store.events.subscribe(
      "setDesignStormQuery",
      ({ design_storm_geojson }) => self._draw(design_storm_geojson)
    );
  }

  get hidden() {
    return !util.get(this, "store.state.show_design_storm");
  }

  async load_data() {
    let self = this;
    let cfg = util.get(self.store, "state.config");
    let info = util.deepCopy(cfg?.project_spatial_data?.design_storm);

    await self._load_data(info);

    if (self.geojson) {
      self.store.dispatch("setDesignStormQuery", {
        design_storm_geojson: self.geojson,
      });
    }
  }

  _draw(geojson) {
    if (!geojson) return;
    let self = this;
    self.group.selectAll("path").remove();
    if (self.hidden) return;

    self.colorScale = d3
      .scaleLinear()
      .domain(self.domain)
      .range(["white", "blue"]);

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
      .attr("stroke", "#eee")
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
      .style("stroke-width", self.stroke_width / self.transform.k);
  }

  async _render() {
    let self = this;
    self.store.events.subscribe("updateConfig", self.load_data.bind(self));
  }
}
