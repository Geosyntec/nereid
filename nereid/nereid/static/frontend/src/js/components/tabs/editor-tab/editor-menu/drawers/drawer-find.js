import { FindNodeDrawer } from "./drawers";
import Component from "../../../../base/component";
import store from "../../../../../lib/state.js";
import * as util from "../../../../../lib/util.js";
import d3 from "../../../../../lib/d3";

class SearchInput extends Component {
  constructor(options) {
    super({ store, id: options.id });
    let self = this;
    self.primary_callback = (data) => {
      identify_node(data.find_node);
    };
    self.primary_button_label = options.primary_button_label || "Find";
  }

  _template_primary_button() {
    if (this.primary_callback == null) return "";
    return `<button
    class="
      rounded-r-lg
      text-xs
      h-10
      font-bold
      py-2
      px-4
      btn-blue
      shadow
      w-20
    "
    type="submit"
    id="${this.id}-primary-button"
  >
    ${this.primary_button_label}
  </button>`;
  }

  _template() {
    return `
      <div id="${this.id}" class="px-2 pb-10">
      <!-- <div class="pb-2"><strong>Search</strong></div> -->

      <div class="">
        <form
          class="
            relative
            flex flex-row
            h-10
            items-center

          "
        >
          <div class="relative w-full flex flex-row items-center">
            <input
              type="text"
              class="absolute
              pl-4
              border
              shadow
              rounded-l-lg
              w-full h-10"
              id="${this.id}-find"
              aria-describedby="${this.id}-find"
              placeholder="Search here..."
              name="find_node"
            />

          </div>
          ${this._template_primary_button()}
        </form>
      </div>
    </div>`;
  }
  _render() {
    let self = this;
    self.element = d3.select(`#${self.parent_id}-content`).append("div");
    self.element.html(self._template());

    let form = self.element.select("form");

    form //
      .attr("method", "get")
      .on("submit", function (event) {
        event.preventDefault();

        form.selectAll("input").property("disabled", false);
        const data = new FormData(event.target);
        const value = util.cleanObject(Object.fromEntries(data.entries()));
        self.primary_callback.bind(self)(value);

        return false;
      });
  }
}

export const findNodeDrawer = new FindNodeDrawer({
  id: "find-node-drawer",
  title: "Find Node",
  children: [new SearchInput({ id: "find-node-ui" })],
  exit_callback: () => {
    let nodes = util.get(store, "state.graph.nodes");
    nodes.map((n) => restore_node(n));
    store.dispatch("foundNodeIds", {});
    store.dispatch("editorUpdate");
  },
});

const highlight_node = (node) => {
  node.color = "orange";
  node.size = 40;
};

const restore_node = (node) => {
  node.color = undefined;
  node.size = undefined;
};

const identify_node = (node_id) => {
  let nodes = util.get(store, "state.graph.nodes");
  let node_candidates = nodes.filter((n) => n.id.includes(node_id));
  nodes.map((n) => restore_node(n));

  let found = [];

  for (let node of node_candidates) {
    if (node) {
      found.push(node);
    }
  }

  if (found.length) {
    for (let node of found) {
      highlight_node(node);
    }
    store.dispatch("foundNodeIds", { found_node_ids: found.map((n) => n.id) });
  }
  store.dispatch("editorUpdate");
};
