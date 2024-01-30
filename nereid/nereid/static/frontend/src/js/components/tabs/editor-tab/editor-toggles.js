import { getTruthy } from "../../../lib/util.js";
import { ToggleBase } from "../../base/toggle.js";
import Component from "../../base/component.js";
import store from "../../../lib/state.js";

const scale = "scale-75";

const toggleMapMode = new ToggleBase({
  id: "map-edit-toggle",
  text: "Show BaseMap",
  isActive: getTruthy(store, "state.map_mode"),
  scale: scale,
  callback: function () {
    let m = !getTruthy(this, "store.state.map_mode");
    this.toggle.select("input[type=checkbox]").property("checked", !!m);
    this.store.dispatch("isMapMode", { map_mode: m });
  },
});

const toggleAddNodeMode = new ToggleBase({
  id: "graph-edit-toggle",
  text: "Edit Graph",
  isActive: getTruthy(store, "state.graph_edit_mode"),
  scale: scale,
  callback: function () {
    let m = !getTruthy(this, "store.state.graph_edit_mode");
    this.toggle.select("input[type=checkbox]").property("checked", !!m);
    this.store.dispatch("isGraphEditMode", { graph_edit_mode: m });
  },
});

const toggleShowStates = new ToggleBase({
  id: "states-vector-toggle",
  text: "Show States",
  isActive: getTruthy(store, "state.show_states"),
  scale: scale,
  callback: function () {
    let m = !getTruthy(this, "store.state.show_states");
    this.toggle.select("input[type=checkbox]").property("checked", !!m);
    this.store.dispatch("isShowStatesMode", { show_states: m });
  },
});

const toggleShowDesignStorm = new ToggleBase({
  id: "design-storm-vector-toggle",
  text: "Show Design Storm",
  isActive: getTruthy(store, "state.show_design_storm"),
  scale: scale,
  callback: function () {
    let m = !getTruthy(this, "store.state.show_design_storm");
    this.toggle.select("input[type=checkbox]").property("checked", !!m);
    this.store.dispatch("isShowDesignStorm", { show_design_storm: m });
  },
});

const toggleShowRainZone = new ToggleBase({
  id: "rain-zone-vector-toggle",
  text: "Show Rain Zones",
  isActive: getTruthy(store, "state.show_rain_zone"),
  scale: scale,
  callback: function () {
    let m = !getTruthy(this, "store.state.show_rain_zone");
    this.toggle.select("input[type=checkbox]").property("checked", !!m);
    this.store.dispatch("isShowRainZones", { show_rain_zone: m });
  },
});

const toggleShowInfoTooltip = new ToggleBase({
  id: "into-tooltip-toggle",
  text: "Show Node Info",
  isActive: getTruthy(store, "state.show_info_tooltip"),
  scale: scale,
  callback: function () {
    let m = !getTruthy(this, "store.state.show_info_tooltip");
    this.toggle.select("input[type=checkbox]").property("checked", !!m);
    this.store.dispatch("isShowInfoTooltip", { show_info_tooltip: m });
  },
});

export const toggles = new Component({
  id: "toggle-container",
  children: [
    toggleMapMode,
    toggleShowStates,
    toggleShowDesignStorm,
    toggleShowRainZone,
    toggleAddNodeMode,
    toggleShowInfoTooltip,
  ],
});

// toggles.render();
