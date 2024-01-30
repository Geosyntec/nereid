import Component from "../../base/component.js";
import store from "../../../lib/state.js";
import d3 from "../../../lib/d3.js";
import * as util from "../../../lib/util.js";

export class EditorTab extends Component {
  constructor(options) {
    super({ store, id: options.id, children: options.children });
    this.store.events.subscribe(
      "updateScenarioName",
      this._update_scenario_name.bind(this)
    );
  }

  get scenario_name() {
    return util.get(this.store, "state.scenario_name");
  }

  _update_scenario_name() {
    let self = this;
    d3.select(`#${self.id}`).select("#scenario-name").text(self.scenario_name);
    return;
  }

  _template() {
    return `
    <div class="flex justify-center text-lg font-bold p-4">
      Scenario:&nbsp
      <span id="scenario-name" contenteditable="true" class="border-b-2 border-black">
        ${this.scenario_name}
      </span>
    </div>
    <div class="relative flex flex-row w-screen">
      <div class="p-2 w-[200px]">
        <div id="toggle-container" class="flex flex-col"></div>
      </div>
      <div class="flex flex-col">
        <div id="map" class="has-tooltip w-[800px] h-[500px]"></div>

      </div>
      <div id="editor-menu"></div>
    </div>
    <div id="editor-info" class="grid grid-cols-2 gap-2 pl-12 py-2"></div>
    `;
  }
  _render() {
    let self = this;
    let element = d3
      .select(`#${self.id}`)
      .classed("flex flex-col justify-center max-w-[1000px]", true)
      .html(self._template());

    element.select("#scenario-name").on("input", () => {
      let scenario_name = element.select("#scenario-name").text().trim();
      self.store.dispatch("changeScenarioName", { scenario_name });
    });
  }
}
