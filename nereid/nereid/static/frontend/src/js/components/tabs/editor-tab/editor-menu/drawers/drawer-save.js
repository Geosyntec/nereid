import { SaveFilesDrawer } from "./drawers";
import { SaveScenarioUI } from "./drawer-content-save-scenario";
import { SaveTmntFacilityUI } from "./drawer-content-save-treatment-facility";

const saveScenarioUI = new SaveScenarioUI({ id: "save-scenario" });
const saveTmntFacilityUI = new SaveTmntFacilityUI({ id: "save-tmnt-facility" });

export const saveFilesDrawer = new SaveFilesDrawer({
  id: "save-files-drawer",
  title: "Save to File",
  children: [saveScenarioUI, saveTmntFacilityUI],
});
