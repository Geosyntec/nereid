import { EditorTab } from "./editor-tab";
import { toggles } from "./editor-toggles";
import { editor } from "../../graph-interface";
import { node_info } from "./editor-node-info";
import { editor_tips } from "./editor-tips";
import { editor_menu, drawers } from "./editor-menu";

export const editTab = new EditorTab({
  id: "editor-tab",
  children: [toggles, editor, node_info, editor_tips, editor_menu, drawers],
});
