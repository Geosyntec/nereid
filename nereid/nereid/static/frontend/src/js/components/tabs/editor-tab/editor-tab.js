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
    <div class="flex flex-row justify-center text-lg font-bold p-4">
      Scenario:&nbsp
      <span id="scenario-name" contenteditable="true" class="border-b-2 border-black bg-gray-100 px-2">
        ${this.scenario_name}
      </span>
    </div>

    <div class="flex flex-row h-screen max-h-[650px]">
      <div class="flex flex-col sm:w-full min-w-0 max-w-[175px] ">
        <div id="toggle-container"></div>
      </div>
      <div class="relative w-full ">
        <div id="map" class="has-tooltip h-full max-w-screen"></div>
        <div id="editor-menu"></div>
      </div>

    </div>

    <div id="editor-info" class="grid grid-cols-2 gap-2 pl-12 py-2"></div>

    `;
  }
  _render() {
    let self = this;
    let element = d3
      .select(`#${self.id}`)
      .classed("flex flex-col ", true)
      .html(self._template());

    element.select("#scenario-name").on("input", () => {
      let scenario_name = element.select("#scenario-name").text().trim();
      self.store.dispatch("changeScenarioName", { scenario_name });
    });
  }
}
