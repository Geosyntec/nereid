import * as api from "../../../../../lib/nereid-api";
import * as util from "../../../../../lib/util";
import EditorMenuOption from "./editor-option";
import { Graph } from "../../../../graph-interface/graph.js";

export const nodeConfigOption = new EditorMenuOption({
  id: "node_editor",
  title: "Configuration",
  icon: `
  <!-- Heroicon name: adjustments -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="h-8 w-8"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
    />
  </svg>`,
  callback: function () {
    this.store.dispatch("changedPanel", { active_panel: "node-editor-panel" });
  },
});

export const loadTableOption = new EditorMenuOption({
  id: "load_table",
  title: "Load from File",
  icon: `
  <!-- Heroicon name: document-add -->
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="h-8 w-8"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
    />
  </svg>`,
  callback: function () {
    this.store.dispatch("changedPanel", { active_panel: "load-table-panel" });
  },
});

export const saveFilesOption = new EditorMenuOption({
  id: "save_files",
  title: "Save Files",
  icon: `
  <!-- Heroicon name: save -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
  </svg>
`,
  callback: function () {
    this.store.dispatch("changedPanel", {
      active_panel: "save-files-panel",
    });
  },
});

export const clearScenarioOption = new EditorMenuOption({
  id: "clear_scenario",
  title: "Clear Scenario",
  icon: `
<div class="sm:pt-10 text-red-600 hover:text-gray-300">

  <!-- Heroicon name: x-circle -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
</div>
`,
  callback: function () {
    if (confirm("Are you sure you want to clear all data?")) {
      let _ = new Graph([], []);
    }
  },
});

export const checkScenarioOption = new EditorMenuOption({
  id: "check_scenario",
  title: "Verify Inputs",
  icon: `
<div class="sm:pt-10 text-blue-600 hover:text-gray-300">

  <!-- Heroicon name: check -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
  </svg>
</div>
`,
  callback: async function () {
    Promise.all([api.validateTreatmentFacilities(), api.validateNetwork()])
      .then((results) => {
        let len_all = results.length;
        const errors = results.filter(
          (e) => e.alert_type.toLowerCase() == "error"
        );
        if (errors.length > 0) {
          let opt = errors[0];
          opt.msg = `<div>${errors.map((e) => e.msg).join("</br>")}</div>`;

          this.store.dispatch("raiseModal", { modal_content: opt });
          return;
        }

        const successes = results.filter(
          (e) => e.alert_type.toLowerCase() == "success"
        );
        if (successes.length === results.length) {
          let opt = {
            title: "Validation Successful",
            msg: "",
            alert_type: "success",
          };

          this.store.dispatch("raiseModal", { modal_content: opt });
          return;
        }
      })
      .catch((e) => {
        let opt = {
          title: "Validation Failed",
          msg: `<pre>${JSON.stringify(e, undefined, 2)}</pre>`,
          alert_type: "error",
        };

        this.store.dispatch("raiseModal", { modal_content: opt });
      });
  },
});

export const runScenarioOption = new EditorMenuOption({
  id: "run_scenario",
  title: "Run Scenario",
  icon: `
<div class="sm:pt-10 text-green-600 hover:text-gray-300">

  <!-- Heroicon name: play -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
</div>
`,
  callback: async function () {
    let rsp = await api.solveWatershed();
    if (rsp?.status?.toLowerCase() === "success") {
      let results = util.get(rsp, "data.results") || [];
      let leaf_results = util.get(rsp, "data.leaf_results") || [];
      this.store.dispatch("newResults", {
        results: results.concat(leaf_results),
      });
    }

    // console.log(rsp);
  },
});

export const findNodeOption = new EditorMenuOption({
  id: "find_node",
  title: "Find",
  icon: `
  <!-- Heroicon name: search -->
  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
`,
  callback: function () {
    this.store.dispatch("changedPanel", {
      active_panel: "find-node-panel",
    });
  },
});
