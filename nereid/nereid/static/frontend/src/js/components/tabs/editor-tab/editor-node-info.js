import Component from "../../base/component.js";
import { filter, get } from "../../../lib/util.js";
import store from "../../../lib/state.js";

class NodeInfoTooltip extends Component {
  constructor(options) {
    super({ store });

    let self = this;
    self.parent_id = options.parent_id;
    self.id = options.id || "";
  }

  get current_node_data() {
    let id =
      get(this, "store.state.selected_node_id") ||
      get(this, "store.state.node_hovered");
    if (!id) return;
    return get(this, "store.state.graph.nodes").find((n) => n.id === id);
  }

  get show_info_tooltip() {
    return get(this, "store.state.show_info_tooltip");
    // && get(this, "store.state.node_hovered")
  }

  tooltip_move(event) {
    let tt_width = this.element.node().getBoundingClientRect().width;
    let px = null;
    let py = null;
    if (event.type == "touchstart") {
      px = event.touches[0].pageX;
      py = event.touches[0].pageY;
    } else {
      px = event.pageX;
      py = event.pageY;
    }

    let anchorPt = Math.max(
      0,
      window.innerWidth - px < tt_width ? px - tt_width : px
    );

    this.element.style("left", anchorPt + "px").style("top", py - 28 + "px");
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
    let d = self.current_node_data;
    // if (!d) return;
    let ele = self.element;

    // console.log("show tt: ", self.show_info_tooltip);

    if (!self.show_info_tooltip || !d) {
      self.hide();
      return;
    }
    self.show();
    // console.log("update tt contents");

    // ele.interrupt().transition().style("opacity", 1).style("height", "auto");

    ele.select(".info-tooltip-header").html(`<h5>Node ID:&nbsp${d.id}</h5>`);

    let table_html = `
        <tr>
          <td>Node Type:</td>
          <td>${d.node_type || "No Data"}</td>
        </tr>
      `;

    ele.select(".info-tooltip-content table").html(table_html);

    let private_keys = Object.keys(d).filter((key) => key.charAt(0) === "_");
    // console.log(private_keys);
    let pp_obj = filter(d, [], private_keys);

    // let datastring = `<pre>${JSON.stringify(d.data, undefined, 2)}</pre>`;
    let datastring = `<pre>${JSON.stringify(pp_obj, undefined, 2)}</pre>`;
    ele.select(".info-tooltip-json").html(datastring);
  }

  _render() {
    let self = this;

    // console.log("rendering tooltip", self.parent_id);

    let parent = d3.select(`#${self.parent_id}`); //.classed("has-tooltip", true);
    self.element = parent
      .append("div")
      .attr("id", self.id || "")
      .classed(
        "transition-opacity opacity-0 tooltip rounded shadow-lg p-1 bg-gray-50",
        true
      );

    let tooltip = self.element.html("");

    tooltip = tooltip.append("div").classed("info-tooltip p-2", true);

    tooltip
      .append("div")
      .classed("info-tooltip-header mt-2 uppercase text-lg font-bold", true);

    tooltip
      .append("div")
      .classed("info-tooltip-content text-sm", true)
      .append("table");

    tooltip
      .select(".info-tooltip-content")
      .append("div")
      .classed("info-tooltip-json", true);
    tooltip.append("div").classed("info-tooltip-footer", true);

    self.store.events.subscribe("stateChange", () => this.update_contents());

    // parent.on("mousemove.node-info-tooltip", (event) =>
    //   self.tooltip_move(event)
    // );
  }
}

export const node_info = new NodeInfoTooltip({
  parent_id: "editor-info",
  id: "node-info-tooltip",
});
