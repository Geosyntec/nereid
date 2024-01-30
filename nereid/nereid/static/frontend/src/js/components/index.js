import "./session";
import { spinner } from "./loading_spinner";
import { modal } from "./modal";
import { tabs } from "./tabs";
import { editor } from "./graph-interface";
import * as util from "../lib/util";
import * as nereidUtil from "../lib/nereid-api";

async function init() {
  await util.getConfigFromUrlQueryParams();
  spinner.render();
  tabs.render();
  modal.render();

  // to window
  window.nereid = {
    tabs,
    editor,
    util,
    nereidUtil,
    state: editor.store.state,
  };
  editor.store.dispatch("updateConfig", {});
}

init();
// util.getConfigFromUrlQueryParams().then(() => {
//   spinner.render();
//   tabs.render();
//   modal.render();

//   // to window
//   import("./graph-interface").then(({ editor }) => {
//     window.nereid = {
//       tabs,
//       editor,
//       util,
//       nereidUtil,
//       state: editor.store.state,
//     };
//     editor.store.dispatch("updateConfig", {});
//   });
// });
