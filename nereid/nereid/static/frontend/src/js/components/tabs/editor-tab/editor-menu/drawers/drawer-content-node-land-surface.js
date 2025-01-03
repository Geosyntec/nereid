import Component from "../../../../base/component.js";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state.js";
import * as util from "../../../../../lib/util.js";
import { editableTable } from "../../../../../lib/editable-table.js";

export class LandSurfaceNodeEditorUI extends Component {
  constructor(options) {
    super({ store });
    let self = this;
  }

  get node_editor_type() {
    return util.get(this, "store.state.node_editor_type");
  }

  get selected_node() {
    let id = util.get(this, "store.state.selected_node_id");
    let n = util.get(this, "store.state.graph.nodes").find((n) => n.id === id);
    return n;
  }

  landSurfaceTableOptions() {
    let self = this;

    let data = [{}];
    if (self.selected_node?.data) {
      data = util.deepCopy(self.selected_node.data);
    } else {
      data = [{ node_id: self.selected_node?.id }];
    }

    return {
      data: data,
      maxHeight: "500px",
      rowContextMenu: [
        {
          label: "<i class='fas fa-check-square'></i> Select Row",
          action: function (e, row) {
            row.select();
          },
        },
        {
          label: "<i class='fas fa-trash'></i> Add Row",
          action: function (e, row) {
            self.table.addRow({ node_id: self.selected_node?.id });
          },
        },
        {
          label: "<i class='fas fa-trash'></i> Delete Row",
          action: function (e, row) {
            if (self.table.getRows().length > 1) {
              row.delete();
            }
          },
        },
      ],
      initialSort: [
        //set the initial sort order of the data
        { column: "surface_key", dir: "asc" },
      ],
      columns: [
        {
          title: "Node Id",
          field: "node_id",
          editor: "input",
          editable: (c) => c.getRow().getPosition() == 1, // only first row is editable
        },
        { title: "Surface Key", field: "surface_key", editor: "input" },
        {
          title: "Area (acres)",
          field: "area_acres",
          hozAlign: "center",
          editor: true,
          width: 90,
        },
        {
          title: "Impervious Area (acres)",
          field: "imp_area_acres",
          hozAlign: "center",
          editor: true,
          width: 90,
        },
      ],
    };
  }

  setCurrentNodeDataToTableData() {
    if (!this.selected_node) {
      alert("no node selected");
      return false;
    }

    let data = util.deepCopy(this.table.getData());
    let node = this.selected_node;
    // console.log(node, data);
    // let unique_node_ids = [...new Set(data.map((d) => d.node_id))];
    // if (unique_node_ids.length > 1) {
    //   alert("when renaming nodes, all node ids must be equal");
    //   return false;
    // }
    let node_id = data[0]?.node_id;

    data.forEach((d) => (d.node_id = node_id));

    node.node_type = this.node_editor_type;
    // console.log(node, data);

    if (node.id !== node_id) {
      node.id = node_id;
      store.dispatch("changedSelectedNode", { selected_node_id: node_id });
    }

    // console.log(node, data);

    node["data"] = data;

    this.store.dispatch("newGraph");
    this.update();
  }

  async buildLandSurfaceTable({ id }) {
    let self = this;

    // const id = "table-facility-capture";
    self.element.select(`#${id}`).remove();
    let ele = self.element
      .append("div")
      .attr("id", id)
      .classed("grid grid-cols-1 grid-rows-auto pt-8", true);

    const table_id = id + "-landsurface-tabulator";

    let undo_redo_buttons_container = ele
      .append("div")
      .classed("flex flex-row p-2 gap-2", true);
    let undo_button = undo_redo_buttons_container
      .append("button")
      .classed("btn btn-gray flex flex-row", true).html(`
      <span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
        </svg>
      </span>
      <span>undo</span>
      `);
    let redo_button = undo_redo_buttons_container
      .append("button")
      .classed("btn btn-gray flex flex-row", true).html(`
      <span>redo</span>
      <span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
        </svg>
      </span>

      `);

    ele.append("div").attr("id", table_id);
    let opt = self.landSurfaceTableOptions();
    self.table = await editableTable(`#${table_id}`, opt);

    undo_button.on("click", () => self.table.undo());
    redo_button.on("click", () => self.table.redo());

    ele
      .append("div")
      .classed("flex flex-row justify-end py-4", true)
      .append("button")
      .classed("btn btn-blue", true)
      .on("click", () => {
        // console.log("ls form clicked apply");
        this.setCurrentNodeDataToTableData.bind(this)();
      })
      .text("Apply");
  }

  async update() {
    let self = this;

    // self.element.select(`#${id}`).remove();
    // let ele = self.element
    //   .append("div")
    //   .attr("id", id)
    //   .classed("grid grid-cols-1 grid-rows-auto pt-8", true);

    if (!(self.node_editor_type === "land_surface")) {
      self.element.classed("hidden", true);
      return;
    }

    self.element.classed("hidden", false);

    // let options = self.landSurfaceTableOptions();

    let id = `${self.parent_id}-content-editor`;

    await self.buildLandSurfaceTable({ id });

    // self.element
    //   .html("")
    //   .append("div")

    //   .attr("id", `${self.parent_id}-content-tabulator`);

    // if (self.element.classed("hidden")) return;

    // self.element
    //   .append("div")
    //   .classed("flex flex-row justify-end py-4", true)
    //   .append("button")
    //   .classed("btn btn-blue", true)
    //   .on("click", () => {
    //     // console.log("ls form clicked apply");
    //     this.setCurrentNodeDataToTableData.bind(this)();
    //   })
    //   .text("Apply");

    // self.table = await editableTable(
    //   `#${self.parent_id}-content-tabulator`,
    //   options
    // );
  }

  _render() {
    let self = this;

    // console.log("rendering selected node", self.parent_id);
    self.element = d3
      .select(`#${self.parent_id}-content`)
      .append("div")
      .classed("mt-4", true)
      .classed("hidden", true);

    self.update();
    self.store.events.subscribe("nodeEditorType", () => self.update());
    self.store.events.subscribe("changedSelectedNode", () => self.update());
    self.store.events.subscribe("changedPanel", () => self.update());
    self.store.events.subscribe("newGraph", () => self.update());
  }
}
