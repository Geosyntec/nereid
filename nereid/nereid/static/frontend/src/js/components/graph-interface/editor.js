import d3 from "../../lib/d3";
import store from "../../lib/state";
import Component from "../base/component";

import Map from "./map";
import StateVectors from "./vectors-states_clickable";
import DesignStormVectors from "./vectors-design_storm";
import RefDataVectors from "./vectors-ref_data_key";
import GraphEditor from "./graph-editor";

export default class Editor extends Component {
  constructor() {
    super({ store });
  }

  _render() {
    let self = this;
    self.svg = d3
      .select(`#map`)
      .append("svg")
      .attr("viewBox", [
        0,
        0,
        d3.select(`#map`).node().getBoundingClientRect().width,
        d3.select(`#map`).node().getBoundingClientRect().height,
      ]);

    self.map = new Map({ id: "map", svg: self.svg });
    const vector = self.map.vector;

    self.states = new StateVectors({ vector });
    self.designStorm = new DesignStormVectors({ vector });
    self.refData = new RefDataVectors({ vector });

    self.graphEditor = new GraphEditor({ svg: self.svg });

    self.map.render();
    self.states.render();
    self.designStorm.render();
    self.refData.render();
    self.graphEditor.render();
  }
}
