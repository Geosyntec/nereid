import "./session";
import Component from "./base/component.js";
import { spinner } from "./loading_spinner";
import { modal } from "./modal";
import { tabs } from "./tabs";
import { editor } from "./graph-interface";
import * as util from "../lib/util";
import * as nereidUtil from "../lib/nereid-api";

window.onload = async (event) => {
  await util.getConfigFromUrlQueryParams();
  const app = new Component({
    id: "app",
    children: [tabs, spinner, modal],
    class: "leading-normal tracking-normal container mx-auto",
  });
  app.render();

  // to window
  window.nereid = {
    tabs,
    editor,
    util,
    nereidUtil,
    state: editor.store.state,
  };
  editor.store.dispatch("updateConfig", {});

  window.onresize = () => {
    editor.resize();
  };
};
