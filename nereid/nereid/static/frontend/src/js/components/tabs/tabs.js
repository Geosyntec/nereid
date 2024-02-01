import Component from "../base/component.js";
import store from "../../lib/state.js";
import d3 from "../../lib/d3.js";
import { TabSystem } from "./tab_system.js";

export class Tabs extends Component {
  constructor({ children }) {
    super({ store, children });
    this.classname = "main-tab-group-namespace";
  }
  _template() {
    return `
    <!-- nav tabs -->
    <div
      class="
        ${this.classname}
        flex
        mt-3
        border-b border-gray-300
        relative
        flex-row
      "
    >
      <div data-target="editor-tab" class="relative tab active">
        Editor
        <div class="absolute tab-slider"></div>
      </div>
      <div data-target="how-to-tab" class="tab">How To</div>
      <div data-target="treatment-facility-results-tab" class="tab">Treatment Results</div>
      <div data-target="land-surface-results-tab" class="tab">Land Surface Results</div>
      <a class="tab" href="./logout">Logout</a>
    </div>

    <!-- end nav tabs -->

    <!-- tab content -->

    <div class="${this.classname} h-screen">
      <div id="how-to-tab" class="tab-content"></div>
      <div id="treatment-facility-results-tab" class="tab-content"></div>
      <div id="land-surface-results-tab" class="tab-content"></div>
      <div id="editor-tab" class="tab-content"></div>
    </div>

    <!-- end tab content -->
    `;
  }
  _render() {
    let self = this;
    let element = d3
      .select(`#${this.parent_id}`)
      .append("div")
      // .classed("min-w-[700px]", true)
      .html(self._template());
    const tabSystem = new TabSystem(`.${this.classname}`);
    tabSystem.init();
  }
}
