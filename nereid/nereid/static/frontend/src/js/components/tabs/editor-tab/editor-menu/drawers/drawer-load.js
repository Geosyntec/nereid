import { LoadTableDrawer } from "./drawers";
import {
  loadGraphFileUI,
  loadLandSurfaceFileUI,
  loadTreatmentFacilitiesFileUI,
  loadScenarioFileUI,
} from "./drawer-content-load-files.js";

export const loadTableDrawer = new LoadTableDrawer({
  id: "load-table-drawer",
  title: "Load from File",
  children: [
    loadGraphFileUI,
    loadLandSurfaceFileUI,
    loadTreatmentFacilitiesFileUI,
    loadScenarioFileUI,
  ],
});
