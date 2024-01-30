import d3 from "../../lib/d3.js";
import * as topojson from "topojson-client";
import store from "../../lib/state.js";
import { get } from "../../lib/util.js";

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

    self.renderer = d3.geoPath(get(self, "store.state.projection"));
    self.url = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json";

    self.vector = options.vector;
    self.path = self.vector
      .append("path")
      .attr("pointer-events", "none")
      .attr("fill", "none")
      .attr("stroke", "green")
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
      .classed("hidden", self.hidden)
      .style("stroke-width", self.stroke_width / self.transform.k);
  }

  get hidden() {
    return !get(this, "store.state.show_states");
  }

  get transform() {
    return get(this, "store.state.transform");
  }

  async _render() {
    let self = this;
    let topology = await d3.json(self.url);
    self.path.attr(
      "d",
      self.renderer(topojson.feature(topology, topology.objects.states))
    );
  }
}
