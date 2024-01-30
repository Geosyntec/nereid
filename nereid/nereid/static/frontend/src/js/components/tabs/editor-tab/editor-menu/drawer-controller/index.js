import {
  findNodeOption,
  nodeConfigOption,
  loadTableOption,
  saveFilesOption,
  clearScenarioOption,
  checkScenarioOption,
  runScenarioOption,
} from "./options";
import EditorMenu from "./editor-menu";

export const editor_menu = new EditorMenu({
  id: "editor-menu",
  children: [
    findNodeOption,
    nodeConfigOption,
    loadTableOption,
    saveFilesOption,
    clearScenarioOption,
    checkScenarioOption,
    runScenarioOption,
  ],
});
