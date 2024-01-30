import d3 from "../../lib/d3.js";
import * as topojson from "topojson-client";
import store from "../../lib/state.js";
import * as util from "../../lib/util.js";

import Component from "../base/component.js";

export default class StateVectors extends Component {
  constructor(options) {
    super({ store });
    let self = this;
    self.stroke_width = 1;
    self.store.events.subscribe("changedTransform", () => {
      self.path.style("stroke-width", self.stroke_width / self.transform.k);
    });
    self.store.events.subscribe("isShowStatesMode", () => {
      self.path.classed("hidden", self.hidden);
    });
    self.projection = util.get(self, "store.state.projection");
    self.renderer = d3.geoPath(self.projection).digits(15);
    self.url = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json";

    self.vector = options.vector;
    self.path = self.vector
      .append("path")
      .attr("pointer-events", "all")
      .attr("fill", "none")
      .attr("stroke", "green")
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
      .classed("hidden", self.hidden)
      .style("stroke-width", self.stroke_width / self.transform.k);
  }

  get hidden() {
    return !util.get(this, "store.state.show_states");
  }

  get transform() {
    return util.get(this, "store.state.transform");
  }

  async _render() {
    let self = this;
    let topology = await d3.json(self.url);
    let geojson = topojson.feature(topology, topology.objects.states);
    self.geojson = geojson;
    self.store.dispatch("setStateQuery", { state_query: geojson });
    self.path.attr("d", self.renderer(geojson));

    // d3.select("#map svg").on("click.states", (e, d) => {
    //   let [x, y] = d3.pointer(e, d3.select("#map svg").node());
    //   let coords = self.projection.invert([x, y]);
    //   let obj = self.geojson.features.find((d) => d3.geoContains(d, coords));

    //   console.log(x, y, coords, obj, obj?.properties?.name);
    // });

    // self.vector.on("click.states", (e, d) => {
    //   let [x, y] = d3.pointer(e, self.vector.node());
    //   let coords = self.projection.invert([x, y]);
    //   let obj = self.geojson.features.find((d) => d3.geoContains(d, coords));

    //   console.log(x, y, coords, obj, obj?.properties?.name);
    // });
  }
}
