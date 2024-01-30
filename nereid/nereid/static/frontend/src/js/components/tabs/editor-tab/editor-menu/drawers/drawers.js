import Component from "../../../../base/component";
import { DrawerBase } from "../../../../base/drawer";
import d3 from "../../../../../lib/d3.js";
import store from "../../../../../lib/state";

export class FindNodeDrawer extends DrawerBase {
  constructor(options) {
    super(options);
    let self = this;

    self.store.events.subscribe("changedPanel", ({ active_panel }) =>
      active_panel === "find-node-panel" ? self.enter() : null
    );
  }
}

export class NodeEditorDrawer extends DrawerBase {
  constructor({ id, title, children }) {
    super({ store, id, title, children });
    let self = this;

    self.store.events.subscribe("changedPanel", ({ active_panel }) =>
      active_panel === "node-editor-panel" ? self.enter() : null
    );
  }
}

export class LoadTableDrawer extends DrawerBase {
  constructor({ id, title, children }) {
    super({ store, id, title, children });
    let self = this;

    self.store.events.subscribe("changedPanel", ({ active_panel }) =>
      active_panel === "load-table-panel" ? self.enter() : null
    );
  }
}

export class SaveFilesDrawer extends DrawerBase {
  constructor({ id, title, children }) {
    super({ store, id, title, children });
    let self = this;

    self.store.events.subscribe("changedPanel", ({ active_panel }) =>
      active_panel === "save-files-panel" ? self.enter() : null
    );
  }
}

export class Drawers extends Component {
  constructor({ children }) {
    super({ store, children });
  }
  _template() {
    return `
    <div id="find-node-drawer"></div>
    <div id="node-editor-drawer"></div>
    <div id="load-table-drawer"></div>
    <div id="save-files-drawer"></div>
    `;
  }
  _render() {
    d3.select("body").append("div").html(this._template());
  }
}
