import { Drawers } from "./drawers";
import { findNodeDrawer } from "./drawer-find";
import { nodeEditorDrawer } from "./drawer-editor";
import { loadTableDrawer } from "./drawer-load";
import { saveFilesDrawer } from "./drawer-save";

export const drawers = new Drawers({
  children: [
    findNodeDrawer,
    nodeEditorDrawer,
    loadTableDrawer,
    saveFilesDrawer,
  ],
});
