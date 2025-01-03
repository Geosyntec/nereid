import Component from "../../base/component.js";
import { get } from "../../../lib/util.js";
import store from "../../../lib/state.js";
import d3 from "../../../lib/d3";

class EditorTips extends Component {
  constructor(options) {
    super({ store });

    let self = this;
    self.parent_id = options.parent_id;
    self.id = options.id || "";
  }

  // get current_node_data() {
  //   let id =
  //     get(this, "store.state.selected_node_id") ||
  //     get(this, "store.state.node_hovered");
  //   if (!id) return;
  //   return get(this, "store.state.graph.nodes").find((n) => n.id === id);
  // }

  get show_tips() {
    return get(this, "store.state.graph_edit_mode");
  }

  hide() {
    // console.log("hiding tt");
    let ele = this.element;
    ele.classed("opacity-100 h-auto", false);
    ele.classed("opacity-0 h-0", true);
  }

  show() {
    let ele = this.element;
    ele.classed("opacity-100 h-auto", true);
    ele.classed("opacity-0 h-0", false);
  }

  update_contents() {
    let self = this;
    if (!self.show_tips) {
      self.hide();
      return;
    }
    self.show();
  }

  _template() {
    return `
    <div>
    <strong>Edit Graph</strong> is Active
    <br />
    <br />
    <em>Click</em> in the open space to <strong>add a node</strong>.

    <br />
    <em>Drag</em> from one node to another to <strong>add an edge</strong>

    <br />
    <em>Click</em> a node or an edge to <strong>select</strong> it.

    <br />
    <em>Press Ctrl & Drag</em> a node to <strong>move</strong> the graph node layout.
    Dragging will pin the node to the location.

    <br />
    <em>Press Delete</em> to <strong>remove the selected node or edge</strong>.
    This is possible only when the mouse is within the map editor.

    <br />
    <em>Press G</em> to <strong>zoom</strong> the map to the graph extents.

    </div>
    `;
  }

  _render() {
    let self = this;

    // console.log("rendering tips", self.parent_id);

    let parent = d3.select(`#${self.parent_id}`); //.classed("has-tooltip", true);
    self.element = parent
      .append("div")
      .attr("id", self.id || "")
      .classed("transition-opacity opacity-0 p-2 h-auto text-justify", true)
      .html(self._template());

    // let tooltip = self.element.html("");

    // tooltip = tooltip.append("div").classed("info-tooltip p-2", true);

    // tooltip
    //   .append("div")
    //   .classed("info-tooltip-header mt-2 uppercase text-lg font-bold", true);

    // tooltip
    //   .append("div")
    //   .classed("info-tooltip-content text-sm", true)
    //   .append("table");

    // tooltip
    //   .select(".info-tooltip-content")
    //   .append("div")
    //   .classed("info-tooltip-json", true);
    // tooltip.append("div").classed("info-tooltip-footer", true);

    this.update_contents();

    self.store.events.subscribe("isGraphEditMode", () =>
      this.update_contents()
    );

    // parent.on("mousemove.node-info-tooltip", (event) =>
    //   self.tooltip_move(event)
    // );
  }
}

export const editor_tips = new EditorTips({
  parent_id: "editor-info",
  id: "editor-tips",
});
