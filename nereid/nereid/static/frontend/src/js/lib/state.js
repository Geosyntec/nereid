import Store from "./store.js";

const state = {
  DEBUG: false,
  current_tab: "editor-tab",
  config: {},
  scenario_name: "New Scenario",
  nereid_host: "",
  nereid_api_latest: "/api/v1",
  nereid_state: "state",
  nereid_region: "region",
  facility_types: [],
  facility_type_map: {},
  initialScale: 1 << 20,
  initialCenter: [-116.9337, 32.74337],
  staged_changes: {},
  default_nodesize: 20,
  max_graph_size: 100,
  map_mode: true,
  show_states: true,
  graph_edit_mode: true,
  show_info_tooltip: true,
  treatment_facility_fields: {
    state: {
      region: {
        ignored: [
          "is_online",
          "offline_diversion_rate_cfs",
          "eliminate_all_dry_weather_flow_override",
        ],
        disabled: ["facility_type"],
      },
    },
    ca: {
      cosd: {
        ignored: [
          "is_online",
          "offline_diversion_rate_cfs",
          "eliminate_all_dry_weather_flow_override",
        ],
        disabled: [
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
        ],
      },
      soc: {
        ignored: [
          "is_online",
          "offline_diversion_rate_cfs",
          "eliminate_all_dry_weather_flow_override",
        ],
        disabled: ["facility_type"],
      },
    },
  },
  node_types: {
    land_surface: {
      title: "Land Surface",
      color: "limegreen",
    },
    treatment_facility: {
      title: "Treatment Facility",
      color: "steelblue",
    },
    treatment_site: {
      title: "Treatment Site",
      color: "orangered",
      disabled: true,
    },
    none: {
      title: "None",
      color: "dimgrey",
    },
  },
  default_graph: {
    nodes: [
      {
        id: "0",
        node_type: "treatment_facility",
      },
      {
        id: "1",
        node_type: "land_surface",
      },
    ],
    edges: [{ source: "1", target: "0" }],
  },
};

export default new Store({
  // actions,
  // mutations,
  state,
});
