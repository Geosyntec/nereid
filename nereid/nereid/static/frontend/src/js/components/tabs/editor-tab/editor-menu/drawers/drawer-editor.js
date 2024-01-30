import { NodeEditorDrawer } from "./drawers";
import { NodeInputUI, SelectedNodeUI } from "./drawer-content-node-inputs.js";
import { LandSurfaceNodeEditorUI } from "./drawer-content-node-land-surface";
import { TreatmentFacilityNodeEditorUI } from "./drawer-content-node-treatment-facility";

const selectedNodeUI = new SelectedNodeUI();
const nodeInputUI = new NodeInputUI();
const landSurfaceEditorUI = new LandSurfaceNodeEditorUI();
const treatmentFacilityNodeEditorUI = new TreatmentFacilityNodeEditorUI();

export const nodeEditorDrawer = new NodeEditorDrawer({
  id: "node-editor-drawer",
  title: "Edit Nodes",
  children: [
    selectedNodeUI,
    nodeInputUI,
    landSurfaceEditorUI,
    treatmentFacilityNodeEditorUI,
  ],
});
