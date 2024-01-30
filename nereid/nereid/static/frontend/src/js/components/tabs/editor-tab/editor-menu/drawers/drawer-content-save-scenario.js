import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import * as util from "../../../../../lib/util.js";
import store from "../../../../../lib/state.js";
import { saveAs } from "file-saver";

export class SaveScenarioUI extends Component {
  constructor(options) {
    super({ store, id: options.id });
  }

  get scenario_name() {
    return util.get(this.store, "state.scenario_name");
  }

  get scenario() {
    return {
      name: this.scenario_name,
      graph: util.get(this, "store.state.graph"),
    };
  }

  saveScenarioBlob() {
    let json_file = {
      filename:
        (this.scenario.name.replaceAll(" ", "_") || "scenario") + ".json",
      json: JSON.stringify(this.scenario, undefined, 2),
    };

    let blob = new Blob([json_file.json], {
      type: "text/plain;charset=utf-8",
    });
    saveAs(blob, json_file.filename);
  }

  dumpScenario() {
    let contents = `<pre>${JSON.stringify(this.scenario, undefined, 2)}</pre>`;

    this.element.select("#dump-scenario-text").html(contents);
  }

  clearScenario() {
    this.element.select("#dump-scenario-text").html("");
  }

  _template() {
    return `
<div>
  <div class="flex flex-row w-full p-4 justify-between items-center"><strong>Save Scenario to File (json)</strong>
      <button
        id="save-scenario"
        class="btn btn-blue"
      >
        Save
      </button>
  </div>
  <div  class="flex flex-row w-full p-4 justify-between items-center gap-2">
    <strong>Print Scenario for Review (json)</strong>
      <button
        id="dump-scenario"
        class="btn btn-gray py-0.5 px-1"
      >
        Print
      </button>
      <button
        id="clear-scenario"
        class="btn btn-gray py-0.5 px-1"
      >
        Clear
      </button>
  </div>
  <div id="dump-scenario-text"></div>
</div>

  `;
  }

  _render() {
    let self = this;
    self.element = d3
      .select(`#${self.parent_id}-content`)
      .append("div")
      .attr("id", self.id);
    self.element.html(self._template());

    self.button = self.element.select("#save-scenario");
    self.button.on("click", self.saveScenarioBlob.bind(self));

    self.button = self.element.select("#dump-scenario");
    self.button.on("click", self.dumpScenario.bind(self));

    self.button = self.element.select("#clear-scenario");
    self.button.on("click", self.clearScenario.bind(self));
  }
}
