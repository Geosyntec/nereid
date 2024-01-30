import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state.js";
import * as util from "../../../../../lib/util.js";

export class SelectedNodeUI extends Component {
  constructor(options) {
    super({ store });
    let self = this;
  }

  get selected_node_id() {
    return util.get(this, "store.state.selected_node_id");
  }

  update() {
    let text = this.selected_node_id
      ? `Node: ${this.selected_node_id.toString()}`
      : `<div class="pt-20">🡄  Select a Node in the Editor Map<div>`;

    this.element.html(text);
  }

  _render() {
    let self = this;

    // console.log("rendering selected node", self.parent_id);
    self.element = d3
      .select(`#${self.parent_id}-content`)
      .append("div")
      .classed("text-lg font-bold pb-2", true);
    self.update();
    self.store.events.subscribe("changedSelectedNode", () => self.update());
  }
}

export class NodeInputUI extends Component {
  constructor(options) {
    super({ store });
    // console.log("init node input");
    let self = this;
    self.store.events.subscribe("changedSelectedNode", () => self.update());
    // self.callback = options.callback;
  }

  get nodes() {
    return util.get(this, "store.state.graph.nodes");
  }

  get selected_node_id() {
    return util.get(this, "store.state.selected_node_id");
  }

  toggleNodeType() {
    let node_type = this.element.select("input:checked").property("value");

    this.store.dispatch("nodeEditorType", {
      node_editor_type: node_type || "none",
    });
  }

  _template() {
    return `
<div id="type-form" class="flex items-center justify-center">

  <!-- Component Start -->
  <form class="grid grid-cols-2 grid-rows-2 gap-2 w-full ">
    <div>
      <input class="hidden" id="radio_1" type="radio" name="radio" value="land_surface">
      <label title="Land Surfaces" class="button-radio-label bg-[#32cd32]" for="radio_1">
        <span>Land Surface</span>
      </label>
    </div>
    <div>
      <input class="hidden" id="radio_2" type="radio" name="radio" value="treatment_facility">
      <label class="button-radio-label bg-[#4682b4]" for="radio_2">
        <span>Treatment Facility</span>
      </label>
    </div>

    <div>
    <!-- <input class="hidden" id="radio_3" type="radio" name="radio" value="treatment_site"> -->
      <label title="Treatment Site (disabled)" class="button-radio-label bg-[#ffa500]" for="radio_3">
        <span>Treatment Site</span>
      </label>
    </div>

    <div>
      <input class="hidden" id="radio_4" type="radio" name="radio" value="none" checked>
      <label class="button-radio-label bg-gray-600" for="radio_4">
        <span>None</span>
      </label>
    </div>
  </form>
  <!-- Component End  -->

</div>`;
  }

  update() {
    let self = this;

    self.element.classed("hidden", self.selected_node_id == null);

    let selected_node = this.nodes.find((n) => n.id === this.selected_node_id);

    self.element
      .select(`input[value=${selected_node?.node_type || "none"}]`)
      .property("checked", true)
      .dispatch("change");

    self.toggleNodeType();
  }

  _render() {
    let self = this;

    // console.log("rendering node input", self.parent_id);
    self.element = d3
      .select(`#${self.parent_id}-content`)
      .append("div")
      .classed("hidden", true);
    self.element.html(self._template());

    self.element
      .selectAll("input")
      .on("change", this.toggleNodeType.bind(this));

    self.update();
  }
}
