import * as util from "./util.js";
import store from "./state.js";

const land_surfaces = () =>
  util.flatten(
    (util.get(store, "state.graph.nodes") || [])
      .filter((d) => d?.node_type === "land_surface" && d?.data)
      .map((d) => d?.data)
  );

const treatment_facilities = () =>
  util.flatten(
    (util.get(store, "state.graph.nodes") || [])
      .filter((d) => d?.node_type === "treatment_facility" && d?.data)
      .map((d) => d?.data)
  );

const treatment_sites = () =>
  util.flatten(
    (util.get(store, "state.graph.nodes") || [])
      .filter((d) => d?.node_type === "treatment_site" && d?.data)
      .map((d) => d?.data)
  );

const graph = () => {
  let edges = (util.get(store, "state.graph.edges") || []).map((d) => {
    return {
      source: d.source.id.toString(),
      target: d.target.id.toString(),
    };
  });

  return { edges: edges, directed: true, multigraph: true };
};

const watershed = () => {
  return {
    graph: graph(),
    land_surfaces: land_surfaces() || [],
    treatment_facilities: treatment_facilities() || [],
    treatment_sites: treatment_sites() || [],
  };
};

const nereid = {
  // getHost: async () => {
  //   let rsp;
  //   try {
  //     rsp = await util.getJsonResponse("/get_env");
  //     if (rsp.status === 200) {
  //       let { nereid_host } = rsp;
  //       // console.log("host?", nereid_host);
  //       return nereid_host;
  //     }
  //   } catch (e) {
  //     console.error(e);
  //   }
  //   // console.log("default localhost:9999");
  //   return ".";
  // },

  getOpenApi: async (host) => {
    let rsp;
    try {
      rsp = await util.getJsonResponse(`${host}/openapi.json`);
      return rsp;
    } catch (err) {
      console.error(err); // TypeError: failed to fetch
      return __openapi;
    }
  },

  getConfig: async (host, state, region) => {
    let rsp;
    try {
      rsp = await util.getJsonResponse(
        `${host}/config?state=${state}&region=${region}`
      );

      if (rsp?.detail?.toLowerCase()?.includes("no config")) {
        console.warn(`no config for ${state} ${region}`);
        return __config;
      }
      return rsp;
    } catch (err) {
      console.error(err); // TypeError: failed to fetch
      return __config;
    }
  },

  getReferenceData: async (host, api, state, region, filename) => {
    let rsp;
    try {
      rsp = await util.getJsonResponse(
        `${host}${api}/reference_data_file?state=${state}&region=${region}&filename=${filename}`
      );

      return rsp;
    } catch (err) {
      console.error(err); // TypeError: failed to fetch
    }
  },

  postValidateNetwork: async (host, api, state, region, data) => {
    let route = `${host}${api}/network/validate?state=${state}&region=${region}`;
    let rsp;
    try {
      rsp = await util.postJsonResponse(route, data);
      if (rsp?.data?.isvalid) {
        return {
          title: "Validation Succeeded",
          msg: "Success",
          alert_type: "success",
        };
        // return true;
      }
      return {
        title: "Validation Errors",
        msg: `<pre>${JSON.stringify(rsp?.data, undefined, 2)}</pre>`,
        alert_type: "error",
      };
    } catch (e) {
      return {
        title: "Validation Error",
        msg: `<pre>${JSON.stringify(e, undefined, 2)}</pre>`,
        alert_type: "error",
      };

      // store.dispatch("raiseModal", { modal_content: opt });
    }

    // store.dispatch("raiseModal", { modal_content: opt });
    // return false;
  },

  postValidateTreatmentFacilities: async (host, api, state, region, data) => {
    let route = `${host}${api}/treatment_facility/validate?state=${state}&region=${region}`;
    let rsp;
    try {
      rsp = await util.postJsonResponse(route, data);

      let errors = [];
      for (let bmp of rsp?.data?.treatment_facilities) {
        bmp?.errors ? errors.push(bmp?.errors.replace(/\n/g, " ")) : null;
      }

      for (let error of rsp?.data?.errors) {
        if (error.toLowerCase().substring(0, 6).includes("error")) {
          errors.push(error);
        }
      }

      if (errors.length == 0) {
        return {
          title: "Validation Succeeded",
          msg: "",
          alert_type: "success",
        };
        // return true;
      }

      return {
        title: "Validation Errors",
        msg: `<pre>${JSON.stringify(errors, undefined, 2)}</pre>`,
        alert_type: "error",
      };
    } catch (e) {
      return {
        title: "Validation Error",
        msg: `<pre>${JSON.stringify(e, undefined, 2)}</pre>`,
        alert_type: "error",
      };

      // store.dispatch("raiseModal", { modal_content: opt });
    }

    // store.dispatch("raiseModal", { modal_content: opt });
    // return false;
  },

  postSolveWatershed: async (host, api, state, region, data) => {
    let route = `${host}${api}/watershed/solve?state=${state}&region=${region}`;
    let rsp;
    try {
      rsp = await util.postJsonResponse(route, data);
      if (rsp?.data?.errors?.length == 0) {
        return rsp;
      }
    } catch (e) {
      console.error(e);
    }
    console.error(rsp, rsp?.data?.errors);
    return rsp;
  },
};

export const getReferenceData = async (filename) => {
  let { nereid_host, nereid_api_latest, nereid_state, nereid_region } =
    util.get(store, "state");
  let rsp;

  try {
    rsp = await nereid.getReferenceData(
      nereid_host,
      nereid_api_latest,
      nereid_state,
      nereid_region,
      filename
    );
  } catch (err) {
    console.error(err);
  }
  return rsp;
};

export const validateNetwork = async () => {
  let data = graph();
  let { nereid_host, nereid_api_latest, nereid_state, nereid_region } =
    util.get(store, "state");
  let rsp;

  try {
    rsp = await nereid.postValidateNetwork(
      nereid_host,
      nereid_api_latest,
      nereid_state,
      nereid_region,
      data
    );
  } catch (err) {
    console.error(err);
  }
  return rsp;
};

export const validateTreatmentFacilities = async () => {
  let data = { treatment_facilities: treatment_facilities() };
  let { nereid_host, nereid_api_latest, nereid_state, nereid_region } =
    util.get(store, "state");
  let rsp;

  try {
    rsp = await nereid.postValidateTreatmentFacilities(
      nereid_host,
      nereid_api_latest,
      nereid_state,
      nereid_region,
      data
    );
  } catch (err) {
    console.error(err);
  }
  return rsp;
};

export const solveWatershed = async () => {
  let data = watershed();
  let { nereid_host, nereid_api_latest, nereid_state, nereid_region } =
    util.get(store, "state");
  let rsp;

  try {
    rsp = await nereid.postSolveWatershed(
      nereid_host,
      nereid_api_latest,
      nereid_state,
      nereid_region,
      data
    );
  } catch (err) {
    console.error(err);
  }
  return rsp;
};

function replace_refs(obj, schema) {
  for (let k in obj) {
    if (typeof obj[k] == "object" && obj[k] !== null) {
      replace_refs(obj[k], schema);
    } else if (k == "$ref") {
      let refname = obj[k].split("/").slice(-1).pop();
      if (refname) {
        delete obj.$ref;
        obj = Object.assign(obj, schema[refname]);
      }
    }
  }
}

export const getConfig = async ({
  nereid_host,
  nereid_state,
  nereid_region,
}) => {
  // console.log(nereid_host, nereid_state, nereid_region);
  if (!nereid_host) {
    nereid_host = window.location.origin; //await nereid.getHost();
  }

  const openapi = await nereid.getOpenApi(nereid_host);

  const config = await nereid.getConfig(
    nereid_host,
    nereid_state,
    nereid_region
  );

  const schema = util.deepCopy(openapi["components"]["schemas"]);
  for (let c in schema) {
    replace_refs(schema[c], schema);
  }

  const facility_objs =
    config["api_recognize"]["treatment_facility"]["facility_type"];

  const facility_type_map = {};
  for (const [k, v] of Object.entries(facility_objs)) {
    facility_type_map[k] = v["validator"];
  }

  const facility_alias_map = {};
  for (const [k, v] of Object.entries(facility_objs)) {
    if (v?.alias) {
      for (let a of v?.alias) {
        facility_alias_map[a] = k;
      }
    } else {
      facility_alias_map[k] = k;
    }
  }

  const facility_label_map = {};
  for (const [k, v] of Object.entries(facility_objs)) {
    facility_label_map[v?.label || k] = k;
  }

  const facility_types = Object.keys(facility_label_map);

  return {
    nereid_host,
    nereid_state,
    nereid_region,
    config,
    openapi,
    schema,
    facility_types,
    facility_type_map,
    facility_alias_map,
    facility_label_map,
  };
};

const __config = {
  default_data_directory: "default_data",
  project_data_directory: "project_data",
  version: "0.4.3",
  author: "Austin Orr",
  contact: "aorr@geosyntec.com",
  state: "state",
  region: "region",
  test: true,
  pint_unit_registry: [
    "MPN = count = mpn",
    "_100ml = 100 * milliliter = _100mL",
  ],
  api_recognize: {
    land_surfaces: {
      preprocess: [
        {
          expand_fields: [
            {
              field: "surface_key",
              sep: "-",
              new_column_names: ["subbasin", "land_use", "soil", "slope"],
            },
          ],
        },
        {
          collapse_fields: [
            {
              new_column_name: "fuzzy_key",
              sep: "-",
              fields: ["land_use"],
            },
          ],
        },
        {
          joins: [
            {
              other: "land_surface_table",
              how: "left",
              left_on: "surface_key",
              right_on: "surface_id",
              validate: "many_to_one",
              indicator: true,
              fuzzy_on: ["fuzzy_key"],
            },
            {
              other: "land_surface_emc_table",
              how: "left",
              left_on: "land_use",
              right_on: "land_use",
              validate: "many_to_one",
              indicator: true,
            },
            {
              other: "dry_weather_land_surface_emc_table",
              how: "left",
              left_on: "land_use",
              right_on: "land_use",
              validate: "many_to_one",
              indicator: true,
            },
            {
              other: "met_table",
              how: "left",
              left_on: "subbasin",
              right_on: "subbasin",
              validate: "many_to_one",
              indicator: true,
            },
            {
              other: "dry_weather_flow_table",
              how: "left",
              left_on: "rain_gauge",
              right_on: "rain_gauge",
              validate: "many_to_one",
              indicator: true,
            },
          ],
        },
        {
          remaps: [
            {
              left: "soil",
              right: "imp_pct",
              how: "addend",
              mapping: {
                water: 100,
              },
            },
            {
              left: "land_use",
              right: "is_developed",
              how: "left",
              fillna: false,
              mapping: {
                COMM: true,
                EDU: true,
                IND: true,
                UTIL: true,
                RESSFH: true,
                RESSFL: true,
                RESMF: true,
                TRFWY: true,
                TRANS: true,
                TROTH: true,
              },
            },
          ],
        },
      ],
    },
    treatment_facility: {
      preprocess: [
        {
          joins: [
            {
              other: "met_table",
              how: "left",
              left_on: "ref_data_key",
              right_on: "subbasin",
              validate: "many_to_one",
              indicator: true,
            },
          ],
        },
        {
          remaps: [
            {
              left: "hsg",
              right: "inf_rate_inhr",
              how: "left",
              fillna: 0.000001,
              mapping: {
                a: 2.5,
                b: 0.8,
                c: 0.24,
                d: 0.024,
                lined: 0.000001,
              },
            },
          ],
        },
      ],
      facility_type: {
        no_treatment: {
          validator: "NTFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "¯\\_(ツ)_/¯",
        },
        dry_extended_detention: {
          validator: "RetAndTmntFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Detention Basin",
        },
        infiltration: {
          validator: "RetentionFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "¯\\_(ツ)_/¯",
        },
        bioretention: {
          validator: "BioInfFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Biofiltration",
        },
        biofiltration: {
          validator: "TmntFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Biofiltration",
        },
        wet_detention: {
          validator: "PermPoolFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Wet Pond",
        },
        sand_filter: {
          validator: "TmntFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Sand Filter",
        },
        swale: {
          validator: "FlowAndRetFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Vegetated Swale",
        },
        hydrodynamic_separator: {
          validator: "FlowFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Hydrodynamic Separator",
        },
        dry_well: {
          validator: "DryWellFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "¯\\_(ツ)_/¯",
        },
        cistern: {
          validator: "CisternFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "¯\\_(ツ)_/¯",
        },
        dry_weather_diversion: {
          validator: "DryWeatherDiversionLowFlowFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "¯\\_(ツ)_/¯",
        },
        dry_weather_treatment: {
          validator: "DryWeatherTreatmentLowFlowFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "Sand Filter",
        },
        low_flow_facility: {
          validator: "LowFlowFacility",
          validation_fallback: "NTFacility",
          tmnt_performance_facility_type: "¯\\_(ツ)_/¯",
        },
      },
    },
  },
  project_reference_data: {
    dry_weather_flow_table: {
      file: "dry_weather_flow.json",
      seasons: {
        winter: ["oct", "nov", "dec", "jan", "feb", "mar"],
        summer: ["apr", "may", "jun", "jul", "aug", "sep"],
      },
    },
    met_table: {
      file: "met_data.json",
      volume_nomo: {
        x_col: "size_fraction",
        t_col: "ddt_hr",
        y_col: "capture_fraction",
      },
      flow_nomo: {
        x_col: "intensity_inhr",
        t_col: "tc_minutes",
        y_col: "performance_frac",
      },
      preprocess: [
        {
          remaps: [
            {
              left: "rain_gauge",
              right: "volume_nomograph",
              how: "left",
              mapping: {
                "100_LAGUNABEACH": "nomographs/100_LAGUNABEACH_volume_nomo.csv",
                "1130_LAGUNA_AUDUBON":
                  "nomographs/1130_LAGUNA_AUDUBON_volume_nomo.csv",
              },
            },
            {
              left: "rain_gauge",
              right: "flow_nomograph",
              how: "left",
              mapping: {
                "100_LAGUNABEACH": "nomographs/100_LAGUNABEACH_flow_nomo.csv",
                "1130_LAGUNA_AUDUBON":
                  "nomographs/1130_LAGUNA_AUDUBON_flow_nomo.csv",
              },
            },
          ],
        },
      ],
    },
    dry_weather_tmnt_performance_table: {
      file: "dry_weather_bmp_params.json",
      facility_column: "facility_type",
      pollutant_column: "pollutant",
      preprocess: [
        {
          remaps: [
            {
              left: "unit",
              right: "--",
              how: "replace",
              mapping: {
                "MPN/100mL": "MPN/_100ml",
                "MPN/100 mL": "MPN/_100ml",
              },
            },
          ],
        },
      ],
    },
    tmnt_performance_table: {
      file: "bmp_params.json",
      facility_column: "facility_type",
      pollutant_column: "pollutant",
      preprocess: [
        {
          remaps: [
            {
              left: "unit",
              right: "--",
              how: "replace",
              mapping: {
                "MPN/100mL": "MPN/_100ml",
                "MPN/100 mL": "MPN/_100ml",
              },
            },
          ],
        },
      ],
    },
    land_surface_table: {
      file: "land_surface_data.json",
    },
    land_surface_emc_table: {
      file: "land_surface_emc.json",
      parameters: [
        {
          long_name: "Total Suspended Solids",
          short_name: "TSS",
          concentration_unit: "mg/L",
          load_unit: "lbs",
        },
        {
          long_name: "Total Copper",
          short_name: "TCu",
          concentration_unit: "ug/L",
          load_unit: "lbs",
        },
        {
          long_name: "Fecal Coliform",
          short_name: "FC",
          concentration_unit: "MPN/_100mL",
          load_unit: "mpn",
        },
      ],
    },
    dry_weather_land_surface_emc_table: {
      file: "dry_weather_land_surface_emc.json",
      parameters: [
        {
          long_name: "Dry Weather Total Suspended Solids",
          short_name: "dwTSS",
          concentration_unit: "mg/L",
          load_unit: "lbs",
        },
        {
          long_name: "Dry Weather Total Copper",
          short_name: "dwTCu",
          concentration_unit: "ug/L",
          load_unit: "lbs",
        },
        {
          long_name: "Dry Weather Fecal Coliform",
          short_name: "dwFC",
          concentration_unit: "MPN/_100mL",
          load_unit: "mpn",
        },
      ],
    },
  },
  data_path: "nereid/data/default_data/state/region",
};

const __openapi = {
  openapi: "3.0.2",
  info: { title: "nereid", version: "0.4.3" },
  paths: {
    "/api/v1/network/validate": {
      post: {
        tags: ["network", "validate"],
        summary: "Validate Network",
        operationId: "validate_network_api_v1_network_validate_post",
        requestBody: {
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/Graph" },
              example: {
                directed: true,
                nodes: [{ id: "A" }, { id: "B" }],
                edges: [{ source: "A", target: "B" }],
              },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/NetworkValidationResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/validate/{task_id}": {
      get: {
        tags: ["network", "validate"],
        summary: "Get Validate Network Result",
        operationId:
          "get_validate_network_result_api_v1_network_validate__task_id__get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/NetworkValidationResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/subgraph": {
      post: {
        tags: ["network", "subgraph"],
        summary: "Subgraph Network",
        operationId: "subgraph_network_api_v1_network_subgraph_post",
        requestBody: {
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/SubgraphRequest" },
              example: {
                graph: {
                  directed: true,
                  edges: [
                    { source: "3", target: "1" },
                    { source: "5", target: "3" },
                    { source: "7", target: "1" },
                    { source: "9", target: "1" },
                    { source: "11", target: "1" },
                    { source: "13", target: "3" },
                    { source: "15", target: "9" },
                    { source: "17", target: "7" },
                    { source: "19", target: "17" },
                    { source: "21", target: "15" },
                    { source: "23", target: "1" },
                    { source: "25", target: "5" },
                    { source: "27", target: "11" },
                    { source: "29", target: "7" },
                    { source: "31", target: "11" },
                    { source: "33", target: "25" },
                    { source: "35", target: "23" },
                    { source: "4", target: "2" },
                    { source: "6", target: "2" },
                    { source: "8", target: "6" },
                    { source: "10", target: "2" },
                    { source: "12", target: "2" },
                    { source: "14", target: "2" },
                    { source: "16", target: "12" },
                    { source: "18", target: "12" },
                    { source: "20", target: "8" },
                    { source: "22", target: "6" },
                    { source: "24", target: "12" },
                  ],
                },
                nodes: [{ id: "3" }, { id: "29" }, { id: "18" }],
              },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/SubgraphResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/subgraph/{task_id}": {
      get: {
        tags: ["network", "subgraph"],
        summary: "Get Subgraph Network Result",
        operationId:
          "get_subgraph_network_result_api_v1_network_subgraph__task_id__get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/SubgraphResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/subgraph/{task_id}/img": {
      get: {
        tags: ["network", "visualize"],
        summary: "Get Subgraph Network As Img",
        operationId:
          "get_subgraph_network_as_img_api_v1_network_subgraph__task_id__img_get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
          {
            required: false,
            schema: { title: "Media Type", type: "string", default: "svg" },
            name: "media_type",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Npi", type: "number", default: 4.0 },
            name: "npi",
            in: "query",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/SubgraphResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/solution_sequence": {
      post: {
        tags: ["network", "sequence"],
        summary: "Network Solution Sequence",
        operationId:
          "network_solution_sequence_api_v1_network_solution_sequence_post",
        parameters: [
          {
            required: false,
            schema: { title: "Min Branch Size", type: "integer", default: 4 },
            name: "min_branch_size",
            in: "query",
          },
        ],
        requestBody: {
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/Graph" },
              example: {
                directed: true,
                edges: [
                  { source: "3", target: "1" },
                  { source: "5", target: "3" },
                  { source: "7", target: "1" },
                  { source: "9", target: "1" },
                  { source: "11", target: "1" },
                  { source: "13", target: "3" },
                  { source: "15", target: "9" },
                  { source: "17", target: "7" },
                  { source: "19", target: "17" },
                  { source: "21", target: "15" },
                  { source: "23", target: "1" },
                  { source: "25", target: "5" },
                  { source: "27", target: "11" },
                  { source: "29", target: "7" },
                  { source: "31", target: "11" },
                  { source: "33", target: "25" },
                  { source: "35", target: "23" },
                  { source: "4", target: "2" },
                  { source: "6", target: "2" },
                  { source: "8", target: "6" },
                  { source: "10", target: "2" },
                  { source: "12", target: "2" },
                  { source: "14", target: "2" },
                  { source: "16", target: "12" },
                  { source: "18", target: "12" },
                  { source: "20", target: "8" },
                  { source: "22", target: "6" },
                  { source: "24", target: "12" },
                ],
              },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/SolutionSequenceResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/solution_sequence/{task_id}": {
      get: {
        tags: ["network", "sequence"],
        summary: "Get Network Solution Sequence",
        operationId:
          "get_network_solution_sequence_api_v1_network_solution_sequence__task_id__get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/SolutionSequenceResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/network/solution_sequence/{task_id}/img": {
      get: {
        tags: ["network", "sequence", "visualize"],
        summary: "Get Network Solution Sequence As Img",
        operationId:
          "get_network_solution_sequence_as_img_api_v1_network_solution_sequence__task_id__img_get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
          {
            required: false,
            schema: { title: "Media Type", type: "string", default: "svg" },
            name: "media_type",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Npi", type: "number", default: 4.0 },
            name: "npi",
            in: "query",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/SolutionSequenceResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/reference_data": {
      get: {
        tags: ["reference_data"],
        summary: "Get Reference Data Json",
        operationId: "get_reference_data_json_api_v1_reference_data_get",
        parameters: [
          {
            required: false,
            schema: { title: "Filename", type: "string", default: "" },
            name: "filename",
            in: "query",
          },
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/ReferenceDataResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/reference_data/nomograph": {
      get: {
        tags: ["reference_data"],
        summary: "Get Nomograph",
        operationId: "get_nomograph_api_v1_reference_data_nomograph_get",
        parameters: [
          {
            required: false,
            schema: { title: "Filename", type: "string", default: "" },
            name: "filename",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Type", type: "string" },
            name: "type",
            in: "query",
          },
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: { "application/json": { schema: {} } },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/reference_data/{table}": {
      get: {
        tags: ["reference_data"],
        summary: "Get Reference Data Table",
        operationId:
          "get_reference_data_table_api_v1_reference_data__table__get",
        parameters: [
          {
            required: true,
            schema: { title: "Table", type: "string" },
            name: "table",
            in: "path",
          },
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: { "application/json": { schema: {} } },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/land_surface/loading": {
      post: {
        tags: ["land_surface", "loading"],
        summary: "Calculate Loading",
        operationId: "calculate_loading_api_v1_land_surface_loading_post",
        parameters: [
          {
            required: false,
            schema: { title: "Details", type: "boolean", default: false },
            name: "details",
            in: "query",
          },
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        requestBody: {
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/LandSurfaces" },
              example: {
                land_surfaces: [
                  {
                    node_id: "1",
                    surface_key: "10101100-RESMF-A-5",
                    area_acres: 1.834347898661638,
                    imp_area_acres: 1.430224547955745,
                  },
                  {
                    node_id: "0",
                    surface_key: "10101100-OSDEV-A-0",
                    area_acres: 4.458327528535912,
                    imp_area_acres: 0.4457209193544626,
                  },
                  {
                    node_id: "0",
                    surface_key: "10101000-IND-A-10",
                    area_acres: 3.337086111390218,
                    imp_area_acres: 0.47675887386582366,
                  },
                  {
                    node_id: "0",
                    surface_key: "10101100-COMM-C-0",
                    area_acres: 0.5641157902710026,
                    imp_area_acres: 0.40729090799199347,
                  },
                  {
                    node_id: "1",
                    surface_key: "10101200-TRANS-C-5",
                    area_acres: 0.007787658410143283,
                    imp_area_acres: 0.007727004694355631,
                  },
                ],
              },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/LandSurfaceResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/land_surface/loading/{task_id}": {
      get: {
        tags: ["land_surface", "loading"],
        summary: "Get Land Surface Loading Result",
        operationId:
          "get_land_surface_loading_result_api_v1_land_surface_loading__task_id__get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/LandSurfaceResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/treatment_facility/validate": {
      post: {
        tags: ["treatment_facility", "validate"],
        summary: "Initialize Treatment Facility Parameters",
        operationId:
          "initialize_treatment_facility_parameters_api_v1_treatment_facility_validate_post",
        parameters: [
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        requestBody: {
          content: {
            "application/json": {
              schema: {
                title: "Treatment Facilities",
                anyOf: [
                  { $ref: "#/components/schemas/TreatmentFacilities" },
                  { $ref: "#/components/schemas/TreatmentFacilitiesStrict" },
                ],
              },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/TreatmentFacilitiesResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/treatment_facility/validate/{task_id}": {
      get: {
        tags: ["treatment_facility", "validate"],
        summary: "Get Treatment Facility Parameters",
        operationId:
          "get_treatment_facility_parameters_api_v1_treatment_facility_validate__task_id__get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/TreatmentFacilitiesResponse",
                },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/treatment_site/validate": {
      post: {
        tags: ["treatment_site", "validate"],
        summary: "Initialize Treatment Site",
        operationId:
          "initialize_treatment_site_api_v1_treatment_site_validate_post",
        parameters: [
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        requestBody: {
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/TreatmentSites" },
              example: {
                treatment_sites: [
                  {
                    node_id: "WQMP-1a-tmnt",
                    facility_type: "bioretention",
                    area_pct: 75,
                    captured_pct: 80,
                    retained_pct: 10,
                  },
                  {
                    node_id: "WQMP-1a-tmnt",
                    facility_type: "nt",
                    area_pct: 25,
                    captured_pct: 0,
                    retained_pct: 0,
                  },
                  {
                    node_id: "WQMP-1b-tmnt",
                    facility_type: "bioretention",
                    area_pct: 75,
                    captured_pct: 50,
                    retained_pct: 10,
                  },
                  {
                    node_id: "WQMP-1b-tmnt",
                    facility_type: "nt",
                    area_pct: 25,
                    captured_pct: 0,
                    retained_pct: 0,
                  },
                ],
              },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/TreatmentSiteResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/watershed/solve": {
      post: {
        tags: ["watershed", "main"],
        summary: "Post Solve Watershed",
        operationId: "post_solve_watershed_api_v1_watershed_solve_post",
        parameters: [
          {
            required: false,
            schema: { title: "State", type: "string", default: "state" },
            name: "state",
            in: "query",
          },
          {
            required: false,
            schema: { title: "Region", type: "string", default: "region" },
            name: "region",
            in: "query",
          },
        ],
        requestBody: {
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/Watershed" },
            },
          },
          required: true,
        },
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/WatershedResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
    "/api/v1/watershed/solve/{task_id}": {
      get: {
        tags: ["watershed", "main"],
        summary: "Get Watershed Result",
        operationId:
          "get_watershed_result_api_v1_watershed_solve__task_id__get",
        parameters: [
          {
            required: true,
            schema: { title: "Task Id", type: "string" },
            name: "task_id",
            in: "path",
          },
        ],
        responses: {
          200: {
            description: "Successful Response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/WatershedResponse" },
              },
            },
          },
          422: {
            description: "Validation Error",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/HTTPValidationError" },
              },
            },
          },
        },
      },
    },
  },
  components: {
    schemas: {
      BioInfFacility: {
        title: "BioInfFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "total_volume_cuft",
          "retention_volume_cuft",
          "area_sqft",
          "media_filtration_rate_inhr",
          "hsg",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          total_volume_cuft: { title: "Total Volume Cuft", type: "number" },
          retention_volume_cuft: {
            title: "Retention Volume Cuft",
            type: "number",
          },
          area_sqft: { title: "Area Sqft", type: "number" },
          media_filtration_rate_inhr: {
            title: "Media Filtration Rate Inhr",
            type: "number",
          },
          hsg: { title: "Hsg", type: "string" },
        },
      },
      CisternFacility: {
        title: "CisternFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "total_volume_cuft",
          "winter_demand_cfs",
          "summer_demand_cfs",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          total_volume_cuft: { title: "Total Volume Cuft", type: "number" },
          winter_demand_cfs: { title: "Winter Demand Cfs", type: "number" },
          summer_demand_cfs: { title: "Summer Demand Cfs", type: "number" },
        },
      },
      DryWeatherDiversionLowFlowFacility: {
        title: "DryWeatherDiversionLowFlowFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          treatment_rate_cfs: { title: "Treatment Rate Cfs", type: "number" },
          design_capacity_cfs: { title: "Design Capacity Cfs", type: "number" },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          months_operational: {
            title: "Months Operational",
            pattern: "summer$|winter$|both$",
            type: "string",
            default: "both",
          },
        },
      },
      DryWeatherTreatmentLowFlowFacility: {
        title: "DryWeatherTreatmentLowFlowFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          treatment_rate_cfs: { title: "Treatment Rate Cfs", type: "number" },
          design_capacity_cfs: { title: "Design Capacity Cfs", type: "number" },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          months_operational: {
            title: "Months Operational",
            pattern: "summer$|winter$|both$",
            type: "string",
            default: "both",
          },
        },
      },
      DryWellFacility: {
        title: "DryWellFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "total_volume_cuft",
          "treatment_rate_cfs",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          total_volume_cuft: { title: "Total Volume Cuft", type: "number" },
          treatment_rate_cfs: { title: "Treatment Rate Cfs", type: "number" },
        },
      },
      Edge: {
        title: "Edge",
        required: ["source", "target"],
        type: "object",
        properties: {
          source: { title: "Source", type: "string" },
          target: { title: "Target", type: "string" },
          metadata: { title: "Metadata", type: "object", default: {} },
        },
      },
      FlowAndRetFacility: {
        title: "FlowAndRetFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "treatment_rate_cfs",
          "area_sqft",
          "depth_ft",
          "hsg",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          treatment_rate_cfs: { title: "Treatment Rate Cfs", type: "number" },
          area_sqft: { title: "Area Sqft", type: "number" },
          depth_ft: { title: "Depth Ft", type: "number" },
          hsg: { title: "Hsg", type: "string" },
        },
      },
      FlowFacility: {
        title: "FlowFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "treatment_rate_cfs",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          treatment_rate_cfs: { title: "Treatment Rate Cfs", type: "number" },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
        },
      },
      Graph: {
        title: "Graph",
        required: ["edges"],
        type: "object",
        properties: {
          edges: {
            title: "Edges",
            type: "array",
            items: { $ref: "#/components/schemas/Edge" },
          },
          nodes: {
            title: "Nodes",
            type: "array",
            items: { $ref: "#/components/schemas/Node" },
          },
          directed: { title: "Directed", type: "boolean", default: true },
          multigraph: { title: "Multigraph", type: "boolean", default: true },
          type: { title: "Type", type: "string" },
          label: { title: "Label", type: "string" },
          metadata: { title: "Metadata", type: "object" },
        },
      },
      HTTPValidationError: {
        title: "HTTPValidationError",
        type: "object",
        properties: {
          detail: {
            title: "Detail",
            type: "array",
            items: { $ref: "#/components/schemas/ValidationError" },
          },
        },
      },
      LandSurface: {
        title: "LandSurface",
        required: ["node_id", "surface_key", "area_acres", "imp_area_acres"],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          surface_key: {
            title: "Surface Key",
            type: "string",
            example: "104506-RESSFH-B-5",
          },
          area_acres: { title: "Area Acres", type: "number" },
          imp_area_acres: { title: "Imp Area Acres", type: "number" },
        },
      },
      LandSurfaceDetails: {
        title: "LandSurfaceDetails",
        required: [
          "node_id",
          "surface_key",
          "area_acres",
          "imp_area_acres",
          "surface_id",
          "perv_ro_depth_inches",
          "imp_ro_depth_inches",
          "perv_ro_coeff",
          "imp_ro_coeff",
          "perv_area_acres",
          "imp_area_sqft",
          "perv_area_sqft",
          "imp_ro_depth_feet",
          "perv_ro_depth_feet",
          "imp_ro_volume_cuft",
          "perv_ro_volume_cuft",
          "runoff_volume_cuft",
          "imp_eff_area_acres",
          "perv_eff_area_acres",
          "eff_area_acres",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          surface_key: { title: "Surface Key", type: "string" },
          area_acres: { title: "Area Acres", type: "number" },
          imp_area_acres: { title: "Imp Area Acres", type: "number" },
          surface_id: { title: "Surface Id", type: "string" },
          perv_ro_depth_inches: {
            title: "Perv Ro Depth Inches",
            type: "number",
          },
          imp_ro_depth_inches: { title: "Imp Ro Depth Inches", type: "number" },
          perv_ro_coeff: { title: "Perv Ro Coeff", type: "number" },
          imp_ro_coeff: { title: "Imp Ro Coeff", type: "number" },
          perv_area_acres: { title: "Perv Area Acres", type: "number" },
          imp_area_sqft: { title: "Imp Area Sqft", type: "number" },
          perv_area_sqft: { title: "Perv Area Sqft", type: "number" },
          imp_ro_depth_feet: { title: "Imp Ro Depth Feet", type: "number" },
          perv_ro_depth_feet: { title: "Perv Ro Depth Feet", type: "number" },
          imp_ro_volume_cuft: { title: "Imp Ro Volume Cuft", type: "number" },
          perv_ro_volume_cuft: { title: "Perv Ro Volume Cuft", type: "number" },
          runoff_volume_cuft: { title: "Runoff Volume Cuft", type: "number" },
          imp_eff_area_acres: { title: "Imp Eff Area Acres", type: "number" },
          perv_eff_area_acres: { title: "Perv Eff Area Acres", type: "number" },
          eff_area_acres: { title: "Eff Area Acres", type: "number" },
        },
      },
      LandSurfaceResponse: {
        title: "LandSurfaceResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/LandSurfaceResults" },
        },
      },
      LandSurfaceResults: {
        title: "LandSurfaceResults",
        required: ["summary"],
        type: "object",
        properties: {
          summary: {
            title: "Summary",
            type: "array",
            items: { $ref: "#/components/schemas/LandSurfaceSummary" },
          },
          details: {
            title: "Details",
            type: "array",
            items: { $ref: "#/components/schemas/LandSurfaceDetails" },
          },
          errors: { title: "Errors", type: "array", items: { type: "string" } },
        },
      },
      LandSurfaceSummary: {
        title: "LandSurfaceSummary",
        required: [
          "node_id",
          "area_acres",
          "imp_area_acres",
          "perv_area_acres",
          "imp_ro_volume_cuft",
          "perv_ro_volume_cuft",
          "runoff_volume_cuft",
          "eff_area_acres",
          "land_surfaces_count",
          "imp_pct",
          "ro_coeff",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          area_acres: { title: "Area Acres", type: "number" },
          imp_area_acres: { title: "Imp Area Acres", type: "number" },
          perv_area_acres: { title: "Perv Area Acres", type: "number" },
          imp_ro_volume_cuft: { title: "Imp Ro Volume Cuft", type: "number" },
          perv_ro_volume_cuft: { title: "Perv Ro Volume Cuft", type: "number" },
          runoff_volume_cuft: { title: "Runoff Volume Cuft", type: "number" },
          eff_area_acres: { title: "Eff Area Acres", type: "number" },
          land_surfaces_count: { title: "Land Surfaces Count", type: "number" },
          imp_pct: { title: "Imp Pct", type: "number" },
          ro_coeff: { title: "Ro Coeff", type: "number" },
        },
      },
      LandSurfaces: {
        title: "LandSurfaces",
        required: ["land_surfaces"],
        type: "object",
        properties: {
          land_surfaces: {
            title: "Land Surfaces",
            type: "array",
            items: { $ref: "#/components/schemas/LandSurface" },
          },
        },
      },
      LowFlowFacility: {
        title: "LowFlowFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          treatment_rate_cfs: { title: "Treatment Rate Cfs", type: "number" },
          design_capacity_cfs: { title: "Design Capacity Cfs", type: "number" },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          months_operational: {
            title: "Months Operational",
            pattern: "summer$|winter$|both$",
            type: "string",
            default: "both",
          },
        },
      },
      NTFacility: {
        title: "NTFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
        },
      },
      NetworkValidation: {
        title: "NetworkValidation",
        required: ["isvalid"],
        type: "object",
        properties: {
          isvalid: { title: "Isvalid", type: "boolean" },
          node_cycles: {
            title: "Node Cycles",
            type: "array",
            items: { type: "array", items: { type: "string" } },
          },
          edge_cycles: {
            title: "Edge Cycles",
            type: "array",
            items: { type: "array", items: { type: "string" } },
          },
          multiple_out_edges: {
            title: "Multiple Out Edges",
            type: "array",
            items: { type: "array", items: { type: "string" } },
          },
          duplicate_edges: {
            title: "Duplicate Edges",
            type: "array",
            items: { type: "array", items: { type: "string" } },
          },
        },
      },
      NetworkValidationResponse: {
        title: "NetworkValidationResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/NetworkValidation" },
        },
      },
      Node: {
        title: "Node",
        type: "object",
        properties: {
          id: { title: "Id", type: "string" },
          metadata: { title: "Metadata", type: "object", default: {} },
        },
      },
      Nodes: {
        title: "Nodes",
        required: ["nodes"],
        type: "object",
        properties: {
          nodes: {
            title: "Nodes",
            type: "array",
            items: { $ref: "#/components/schemas/Node" },
          },
        },
      },
      ParallelSeriesSequence: {
        title: "ParallelSeriesSequence",
        required: ["parallel"],
        type: "object",
        properties: {
          parallel: {
            title: "Parallel",
            type: "array",
            items: { $ref: "#/components/schemas/SeriesSequence" },
          },
        },
      },
      PermPoolFacility: {
        title: "PermPoolFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "pool_volume_cuft",
          "pool_drawdown_time_hr",
          "treatment_volume_cuft",
          "treatment_drawdown_time_hr",
          "winter_demand_cfs",
          "summer_demand_cfs",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          pool_volume_cuft: { title: "Pool Volume Cuft", type: "number" },
          pool_drawdown_time_hr: {
            title: "Pool Drawdown Time Hr",
            type: "number",
          },
          treatment_volume_cuft: {
            title: "Treatment Volume Cuft",
            type: "number",
          },
          treatment_drawdown_time_hr: {
            title: "Treatment Drawdown Time Hr",
            type: "number",
          },
          winter_demand_cfs: { title: "Winter Demand Cfs", type: "number" },
          summer_demand_cfs: { title: "Summer Demand Cfs", type: "number" },
        },
      },
      PreviousResult: {
        title: "PreviousResult",
        required: ["node_id"],
        type: "object",
        properties: { node_id: { title: "Node Id", type: "string" } },
      },
      ReferenceData: {
        title: "ReferenceData",
        required: ["state", "region", "file"],
        type: "object",
        properties: {
          state: { title: "State", type: "string" },
          region: { title: "Region", type: "string" },
          file: { title: "File", type: "string" },
          filedata: { title: "Filedata" },
        },
      },
      ReferenceDataResponse: {
        title: "ReferenceDataResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/ReferenceData" },
        },
      },
      Result: {
        title: "Result",
        required: ["node_id"],
        type: "object",
        properties: { node_id: { title: "Node Id", type: "string" } },
      },
      RetAndTmntFacility: {
        title: "RetAndTmntFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "total_volume_cuft",
          "retention_volume_cuft",
          "area_sqft",
          "treatment_drawdown_time_hr",
          "hsg",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          total_volume_cuft: { title: "Total Volume Cuft", type: "number" },
          retention_volume_cuft: {
            title: "Retention Volume Cuft",
            type: "number",
          },
          area_sqft: { title: "Area Sqft", type: "number" },
          treatment_drawdown_time_hr: {
            title: "Treatment Drawdown Time Hr",
            type: "number",
          },
          hsg: { title: "Hsg", type: "string" },
        },
      },
      RetentionFacility: {
        title: "RetentionFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "total_volume_cuft",
          "area_sqft",
          "inf_rate_inhr",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          total_volume_cuft: { title: "Total Volume Cuft", type: "number" },
          area_sqft: { title: "Area Sqft", type: "number" },
          inf_rate_inhr: { title: "Inf Rate Inhr", type: "number" },
        },
      },
      SeriesSequence: {
        title: "SeriesSequence",
        required: ["series"],
        type: "object",
        properties: {
          series: {
            title: "Series",
            type: "array",
            items: { $ref: "#/components/schemas/Nodes" },
          },
        },
      },
      SolutionSequence: {
        title: "SolutionSequence",
        required: ["solution_sequence"],
        type: "object",
        properties: {
          solution_sequence: {
            $ref: "#/components/schemas/ParallelSeriesSequence",
          },
        },
      },
      SolutionSequenceResponse: {
        title: "SolutionSequenceResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/SolutionSequence" },
        },
      },
      SubgraphNodes: {
        title: "SubgraphNodes",
        required: ["subgraph_nodes"],
        type: "object",
        properties: {
          subgraph_nodes: {
            title: "Subgraph Nodes",
            type: "array",
            items: { $ref: "#/components/schemas/Nodes" },
          },
        },
      },
      SubgraphRequest: {
        title: "SubgraphRequest",
        required: ["graph", "nodes"],
        type: "object",
        properties: {
          graph: { $ref: "#/components/schemas/Graph" },
          nodes: {
            title: "Nodes",
            type: "array",
            items: { $ref: "#/components/schemas/Node" },
          },
        },
      },
      SubgraphResponse: {
        title: "SubgraphResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/SubgraphNodes" },
        },
      },
      TmntFacility: {
        title: "TmntFacility",
        required: [
          "node_id",
          "facility_type",
          "ref_data_key",
          "design_storm_depth_inches",
          "total_volume_cuft",
          "area_sqft",
          "media_filtration_rate_inhr",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          ref_data_key: { title: "Ref Data Key", type: "string" },
          design_storm_depth_inches: {
            title: "Design Storm Depth Inches",
            exclusiveMinimum: 0.0,
            type: "number",
          },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
          is_online: { title: "Is Online", type: "boolean", default: true },
          tributary_area_tc_min: {
            title: "Tributary Area Tc Min",
            maximum: 60.0,
            type: "number",
            default: 5.0,
          },
          offline_diversion_rate_cfs: {
            title: "Offline Diversion Rate Cfs",
            type: "number",
          },
          total_volume_cuft: { title: "Total Volume Cuft", type: "number" },
          area_sqft: { title: "Area Sqft", type: "number" },
          media_filtration_rate_inhr: {
            title: "Media Filtration Rate Inhr",
            type: "number",
          },
        },
      },
      TreatmentFacilities: {
        title: "TreatmentFacilities",
        required: ["treatment_facilities"],
        type: "object",
        properties: {
          treatment_facilities: {
            title: "Treatment Facilities",
            type: "array",
            items: { type: "object" },
          },
          errors: { title: "Errors", type: "array", items: { type: "string" } },
        },
        example: {
          treatment_facilities: [
            {
              node_id: "1",
              facility_type: "no_treatment",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.45,
            },
            {
              node_id: "1",
              facility_type: "dry_extended_detention",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.05,
              is_online: true,
              tributary_area_tc_min: 30,
              total_volume_cuft: 5500,
              retention_volume_cuft: 4400,
              area_sqft: 1600,
              treatment_drawdown_time_hr: 72,
              hsg: "d",
              offline_diversion_rate_cfs: 2.9,
              eliminate_all_dry_weather_flow_override: false,
            },
            {
              node_id: "1",
              facility_type: "infiltration",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.88,
              is_online: true,
              tributary_area_tc_min: 25,
              total_volume_cuft: 6200,
              area_sqft: 2000,
              inf_rate_inhr: 3.5,
              offline_diversion_rate_cfs: 5,
              eliminate_all_dry_weather_flow_override: false,
            },
            {
              node_id: "1",
              facility_type: "bioretention",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.85,
              is_online: true,
              tributary_area_tc_min: 15,
              total_volume_cuft: 5800,
              retention_volume_cuft: 3500,
              area_sqft: 1300,
              media_filtration_rate_inhr: 12,
              hsg: "a",
              offline_diversion_rate_cfs: 6,
              eliminate_all_dry_weather_flow_override: false,
            },
            {
              node_id: "1",
              facility_type: "biofiltration",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.95,
              is_online: true,
              tributary_area_tc_min: 40,
              total_volume_cuft: 4400,
              area_sqft: 1200,
              media_filtration_rate_inhr: 15,
              offline_diversion_rate_cfs: 6,
              eliminate_all_dry_weather_flow_override: false,
            },
            {
              node_id: "1",
              facility_type: "wet_detention",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.78,
              is_online: true,
              tributary_area_tc_min: 45,
              pool_volume_cuft: 5550,
              pool_drawdown_time_hr: 720,
              treatment_volume_cuft: 2500,
              treatment_drawdown_time_hr: 12,
              winter_demand_cfs: 0.05,
              summer_demand_cfs: 0.88,
              offline_diversion_rate_cfs: 4,
              eliminate_all_dry_weather_flow_override: false,
            },
            {
              node_id: "1",
              facility_type: "sand_filter",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.78,
              total_volume_cuft: 5000,
              area_sqft: 2700,
              media_filtration_rate_inhr: 12,
              is_online: true,
              offline_diversion_rate_cfs: 2.1,
              eliminate_all_dry_weather_flow_override: false,
              tributary_area_tc_min: 20,
            },
            {
              node_id: "1",
              facility_type: "swale",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.0,
              treatment_rate_cfs: 0.55,
              area_sqft: 15600,
              depth_ft: 1.5,
              hsg: "b",
              is_online: true,
              offline_diversion_rate_cfs: 0.5,
              eliminate_all_dry_weather_flow_override: false,
              tributary_area_tc_min: 25,
            },
            {
              node_id: "1",
              facility_type: "hydrodynamic_separator",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.12,
              treatment_rate_cfs: 0.2,
              eliminate_all_dry_weather_flow_override: false,
              tributary_area_tc_min: 50,
              is_online: true,
            },
            {
              node_id: "1",
              facility_type: "dry_well",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.85,
              total_volume_cuft: 800,
              treatment_rate_cfs: 0.5,
              is_online: true,
              offline_diversion_rate_cfs: 0.5,
              eliminate_all_dry_weather_flow_override: false,
              tributary_area_tc_min: 5,
            },
            {
              node_id: "1",
              facility_type: "cistern",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.3,
              total_volume_cuft: 5500,
              winter_demand_cfs: 0.05,
              summer_demand_cfs: 0.25,
              is_online: true,
              offline_diversion_rate_cfs: 0.5,
              eliminate_all_dry_weather_flow_override: false,
              tributary_area_tc_min: 55,
            },
            {
              node_id: "1",
              facility_type: "dry_weather_diversion",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.43,
              design_capacity_cfs: 3.5,
              months_operational: "summer",
              tributary_area_tc_min: 30,
              treatment_rate_cfs: 2.92,
              eliminate_all_dry_weather_flow_override: false,
              is_online: true,
            },
            {
              node_id: "1",
              facility_type: "dry_weather_treatment",
              ref_data_key: "10101200",
              design_storm_depth_inches: 1.32,
              design_capacity_cfs: 6.1,
              months_operational: "summer",
              tributary_area_tc_min: 10,
              treatment_rate_cfs: 3.5,
              eliminate_all_dry_weather_flow_override: false,
              is_online: true,
            },
            {
              node_id: "1",
              facility_type: "low_flow_facility",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.91,
              design_capacity_cfs: 5.1,
              months_operational: "summer",
              tributary_area_tc_min: 20,
              treatment_rate_cfs: 5.0,
              eliminate_all_dry_weather_flow_override: false,
              is_online: true,
            },
          ],
        },
      },
      TreatmentFacilitiesResponse: {
        title: "TreatmentFacilitiesResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/TreatmentFacilities" },
        },
      },
      TreatmentFacilitiesStrict: {
        title: "TreatmentFacilitiesStrict",
        required: ["treatment_facilities"],
        type: "object",
        properties: {
          treatment_facilities: {
            title: "Treatment Facilities",
            type: "array",
            items: {
              anyOf: [
                { $ref: "#/components/schemas/PermPoolFacility" },
                { $ref: "#/components/schemas/RetAndTmntFacility" },
                { $ref: "#/components/schemas/BioInfFacility" },
                { $ref: "#/components/schemas/FlowAndRetFacility" },
                { $ref: "#/components/schemas/RetentionFacility" },
                { $ref: "#/components/schemas/TmntFacility" },
                { $ref: "#/components/schemas/CisternFacility" },
                { $ref: "#/components/schemas/DryWellFacility" },
                {
                  $ref: "#/components/schemas/DryWeatherTreatmentLowFlowFacility",
                },
                {
                  $ref: "#/components/schemas/DryWeatherDiversionLowFlowFacility",
                },
                { $ref: "#/components/schemas/LowFlowFacility" },
                { $ref: "#/components/schemas/FlowFacility" },
                { $ref: "#/components/schemas/NTFacility" },
              ],
            },
          },
          errors: { title: "Errors", type: "array", items: { type: "string" } },
        },
      },
      TreatmentSite: {
        title: "TreatmentSite",
        required: [
          "node_id",
          "facility_type",
          "area_pct",
          "captured_pct",
          "retained_pct",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          area_pct: { title: "Area Pct", type: "number" },
          captured_pct: { title: "Captured Pct", type: "number" },
          retained_pct: { title: "Retained Pct", type: "number" },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
        },
      },
      TreatmentSiteGroup: {
        title: "TreatmentSiteGroup",
        required: ["node_id", "node_type", "treatment_facilities"],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          node_type: { title: "Node Type", type: "string" },
          treatment_facilities: {
            title: "Treatment Facilities",
            type: "array",
            items: { $ref: "#/components/schemas/TreatmentSiteGroupBase" },
          },
          errors: { title: "Errors", type: "array", items: { type: "string" } },
        },
      },
      TreatmentSiteGroupBase: {
        title: "TreatmentSiteGroupBase",
        required: [
          "node_id",
          "facility_type",
          "area_pct",
          "captured_pct",
          "retained_pct",
        ],
        type: "object",
        properties: {
          node_id: { title: "Node Id", type: "string" },
          facility_type: { title: "Facility Type", type: "string" },
          area_pct: { title: "Area Pct", type: "number" },
          captured_pct: { title: "Captured Pct", type: "number" },
          retained_pct: { title: "Retained Pct", type: "number" },
          eliminate_all_dry_weather_flow_override: {
            title: "Eliminate All Dry Weather Flow Override",
            type: "boolean",
            default: false,
          },
        },
      },
      TreatmentSiteGroups: {
        title: "TreatmentSiteGroups",
        required: ["treatment_sites"],
        type: "object",
        properties: {
          treatment_sites: {
            title: "Treatment Sites",
            type: "array",
            items: { $ref: "#/components/schemas/TreatmentSiteGroup" },
          },
        },
      },
      TreatmentSiteResponse: {
        title: "TreatmentSiteResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/TreatmentSiteGroups" },
        },
      },
      TreatmentSites: {
        title: "TreatmentSites",
        required: ["treatment_sites"],
        type: "object",
        properties: {
          treatment_sites: {
            title: "Treatment Sites",
            type: "array",
            items: { $ref: "#/components/schemas/TreatmentSite" },
          },
        },
      },
      ValidationError: {
        title: "ValidationError",
        required: ["loc", "msg", "type"],
        type: "object",
        properties: {
          loc: { title: "Location", type: "array", items: { type: "string" } },
          msg: { title: "Message", type: "string" },
          type: { title: "Error Type", type: "string" },
        },
      },
      Watershed: {
        title: "Watershed",
        required: ["graph", "land_surfaces"],
        type: "object",
        properties: {
          graph: { $ref: "#/components/schemas/Graph" },
          land_surfaces: {
            title: "Land Surfaces",
            type: "array",
            items: { $ref: "#/components/schemas/LandSurface" },
          },
          treatment_facilities: {
            title: "Treatment Facilities",
            anyOf: [
              { type: "array", items: { type: "object" } },
              {
                type: "array",
                items: {
                  anyOf: [
                    { $ref: "#/components/schemas/PermPoolFacility" },
                    { $ref: "#/components/schemas/RetAndTmntFacility" },
                    { $ref: "#/components/schemas/BioInfFacility" },
                    { $ref: "#/components/schemas/FlowAndRetFacility" },
                    { $ref: "#/components/schemas/RetentionFacility" },
                    { $ref: "#/components/schemas/TmntFacility" },
                    { $ref: "#/components/schemas/CisternFacility" },
                    { $ref: "#/components/schemas/DryWellFacility" },
                    {
                      $ref: "#/components/schemas/DryWeatherTreatmentLowFlowFacility",
                    },
                    {
                      $ref: "#/components/schemas/DryWeatherDiversionLowFlowFacility",
                    },
                    { $ref: "#/components/schemas/LowFlowFacility" },
                    { $ref: "#/components/schemas/FlowFacility" },
                    { $ref: "#/components/schemas/NTFacility" },
                  ],
                },
              },
            ],
          },
          treatment_sites: {
            title: "Treatment Sites",
            type: "array",
            items: { $ref: "#/components/schemas/TreatmentSite" },
          },
          previous_results: {
            title: "Previous Results",
            type: "array",
            items: { $ref: "#/components/schemas/PreviousResult" },
          },
        },
        example: {
          graph: {
            directed: true,
            multigraph: false,
            graph: {},
            nodes: [
              { metadata: {}, id: "0" },
              { metadata: {}, id: "1" },
              { metadata: {}, id: "2" },
              { metadata: {}, id: "3" },
              { metadata: {}, id: "4" },
              { metadata: {}, id: "5" },
              { metadata: {}, id: "6" },
            ],
            edges: [
              { metadata: {}, source: "1", target: "0" },
              { metadata: {}, source: "2", target: "1" },
              { metadata: {}, source: "3", target: "2" },
              { metadata: {}, source: "4", target: "2" },
              { metadata: {}, source: "5", target: "2" },
              { metadata: {}, source: "6", target: "1" },
            ],
          },
          treatment_facilities: [
            {
              node_id: "0",
              facility_type: "sand_filter",
              ref_data_key: "10101200",
              design_storm_depth_inches: 0.85,
              total_volume_cuft: 335,
              area_sqft: 1532,
              media_filtration_rate_inhr: 22.5,
              constructor: "treatment_facility_constructor",
              tributary_area_tc_min: 30,
              is_online: true,
            },
            {
              node_id: "2",
              facility_type: "bioretention",
              ref_data_key: "10101000",
              design_storm_depth_inches: 0.85,
              total_volume_cuft: 382,
              retention_volume_cuft: 333,
              area_sqft: 2658,
              media_filtration_rate_inhr: 14.6,
              hsg: "a",
              constructor: "bioinfiltration_facility_constructor",
              tributary_area_tc_min: 55,
              is_online: true,
            },
          ],
          treatment_sites: [
            {
              facility_type: "wet_detention",
              node_id: "1",
              area_pct: 6,
              captured_pct: 57,
              retained_pct: 38,
            },
            {
              facility_type: "cistern",
              node_id: "1",
              area_pct: 80,
              captured_pct: 74,
              retained_pct: 49,
            },
            {
              facility_type: "swale",
              node_id: "1",
              area_pct: 0,
              captured_pct: 61,
              retained_pct: 44,
            },
            {
              facility_type: "dry_weather_diversion",
              node_id: "1",
              area_pct: 12,
              captured_pct: 80,
              retained_pct: 56,
            },
            {
              facility_type: "dry_extended_detention",
              node_id: "1",
              area_pct: 1,
              captured_pct: 40,
              retained_pct: 0,
            },
            {
              facility_type: "infiltration",
              node_id: "1",
              area_pct: 1,
              captured_pct: 73,
              retained_pct: 59,
            },
          ],
          land_surfaces: [
            {
              node_id: "3",
              surface_key: "10101000-RESSFH-rock-5",
              area_acres: 0.3984569310124453,
              imp_area_acres: 0.009673489252693119,
            },
            {
              node_id: "3",
              surface_key: "10101100-RESSFH-D-0",
              area_acres: 8.065001059380828,
              imp_area_acres: 2.16741977121951,
            },
            {
              node_id: "3",
              surface_key: "10101100-EDU-D-5",
              area_acres: 2.5839358997133957,
              imp_area_acres: 2.55343628659585,
            },
            {
              node_id: "3",
              surface_key: "10101100-UTIL-A-5",
              area_acres: 4.312089428850966,
              imp_area_acres: 4.131205425493061,
            },
            {
              node_id: "3",
              surface_key: "10101200-RESSFL-D-5",
              area_acres: 3.9337442224446297,
              imp_area_acres: 0.7661658366327859,
            },
            {
              node_id: "4",
              surface_key: "10101200-COMM-A-0",
              area_acres: 0.28767325522239817,
              imp_area_acres: 0.08026707777353169,
            },
            {
              node_id: "4",
              surface_key: "10101200-TRANS-rock-10",
              area_acres: 6.9571538459344495,
              imp_area_acres: 1.2273914932176564,
            },
            {
              node_id: "4",
              surface_key: "10101200-OSLOW-rock-0",
              area_acres: 2.403387703304852,
              imp_area_acres: 0.9959985713261311,
            },
            {
              node_id: "4",
              surface_key: "10101200-OSWET-D-5",
              area_acres: 2.79314881649118,
              imp_area_acres: 0.15499820430359323,
            },
            {
              node_id: "4",
              surface_key: "10101100-OSFOR-D-5",
              area_acres: 2.905930886150414,
              imp_area_acres: 1.4925738336538064,
            },
            {
              node_id: "4",
              surface_key: "10101000-TRANS-A-5",
              area_acres: 9.350620373618705,
              imp_area_acres: 5.232513213963891,
            },
            {
              node_id: "4",
              surface_key: "10101200-COMM-C-0",
              area_acres: 2.1979646924219196,
              imp_area_acres: 0.2053466380605771,
            },
            {
              node_id: "4",
              surface_key: "10101000-OSWET-D-0",
              area_acres: 9.316054897695937,
              imp_area_acres: 8.379096506045641,
            },
            {
              node_id: "4",
              surface_key: "10101200-TRFWY-A-0",
              area_acres: 1.4272661923917718,
              imp_area_acres: 1.2613822514526472,
            },
            {
              node_id: "4",
              surface_key: "10101200-OSDEV-C-10",
              area_acres: 4.221871721446085,
              imp_area_acres: 0.4549400198109034,
            },
            {
              node_id: "4",
              surface_key: "10101100-RESSFH-C-0",
              area_acres: 0.26360615441130775,
              imp_area_acres: 0.13605449920172205,
            },
            {
              node_id: "4",
              surface_key: "10101000-OSDEV-D-5",
              area_acres: 7.289650539203478,
              imp_area_acres: 6.077668638347337,
            },
            {
              node_id: "5",
              surface_key: "10101000-IND-A-10",
              area_acres: 4.930498275495615,
              imp_area_acres: 4.450757471699112,
            },
            {
              node_id: "5",
              surface_key: "10101200-OSLOW-rock-0",
              area_acres: 7.814106399568224,
              imp_area_acres: 1.078526163782842,
            },
            {
              node_id: "5",
              surface_key: "10101200-RESSFL-D-5",
              area_acres: 6.185417372804003,
              imp_area_acres: 5.76250105686173,
            },
            {
              node_id: "5",
              surface_key: "10101200-OSIRR-water-10",
              area_acres: 0.36715726648133273,
              imp_area_acres: 0.23531606583046188,
            },
            {
              node_id: "5",
              surface_key: "10101200-RESMF-D-5",
              area_acres: 5.3935429017017515,
              imp_area_acres: 3.810512599072686,
            },
            {
              node_id: "5",
              surface_key: "10101100-RESSFH-A-5",
              area_acres: 2.3620796715469004,
              imp_area_acres: 1.870944109794398,
            },
            {
              node_id: "5",
              surface_key: "10101200-WATER-A-10",
              area_acres: 5.506805596166197,
              imp_area_acres: 2.0512411750860533,
            },
            {
              node_id: "5",
              surface_key: "10101200-TRFWY-A-5",
              area_acres: 2.2549267594382885,
              imp_area_acres: 0.059337765905655114,
            },
            {
              node_id: "5",
              surface_key: "10101200-EDU-A-5",
              area_acres: 6.945443095820329,
              imp_area_acres: 2.426366435613679,
            },
            {
              node_id: "5",
              surface_key: "10101100-IND-D-0",
              area_acres: 3.8291536983619254,
              imp_area_acres: 2.4237194475207304,
            },
            {
              node_id: "5",
              surface_key: "10101000-RESSFH-D-10",
              area_acres: 4.720854566650611,
              imp_area_acres: 1.9563886575871627,
            },
            {
              node_id: "5",
              surface_key: "10101000-EDU-C-10",
              area_acres: 1.7804423698966843,
              imp_area_acres: 0.3371318723066817,
            },
            {
              node_id: "6",
              surface_key: "10101200-TRANS-D-0",
              area_acres: 2.2754330855140923,
              imp_area_acres: 1.0211331313414405,
            },
            {
              node_id: "6",
              surface_key: "10101100-OSLOW-D-5",
              area_acres: 6.214500618686376,
              imp_area_acres: 0.6340460489422389,
            },
            {
              node_id: "6",
              surface_key: "10101100-UTIL-A-10",
              area_acres: 2.555615240745477,
              imp_area_acres: 2.131208949421928,
            },
            {
              node_id: "6",
              surface_key: "10101000-RESSFH-A-5",
              area_acres: 8.175748802007071,
              imp_area_acres: 1.8980919101830314,
            },
            {
              node_id: "6",
              surface_key: "10101200-RESSFH-A-0",
              area_acres: 3.860268456910725,
              imp_area_acres: 1.9184629017741963,
            },
            {
              node_id: "6",
              surface_key: "10101200-OSDEV-C-5",
              area_acres: 0.5748050245941472,
              imp_area_acres: 0.1411875823737466,
            },
            {
              node_id: "6",
              surface_key: "10101000-RESSFH-D-0",
              area_acres: 7.945535238259879,
              imp_area_acres: 0.6302494865328522,
            },
            {
              node_id: "6",
              surface_key: "10101000-RESMF-D-0",
              area_acres: 6.915337959629758,
              imp_area_acres: 3.162694892687792,
            },
            {
              node_id: "6",
              surface_key: "10101000-IND-A-5",
              area_acres: 5.262089934922299,
              imp_area_acres: 0.012019588367122497,
            },
            {
              node_id: "6",
              surface_key: "10101200-EDU-D-10",
              area_acres: 9.142141560695912,
              imp_area_acres: 8.229015560695975,
            },
            {
              node_id: "6",
              surface_key: "10101200-OSAGIR-A-10",
              area_acres: 1.1171651349206269,
              imp_area_acres: 0.5990037582520297,
            },
            {
              node_id: "6",
              surface_key: "10101100-OSAGIR-C-0",
              area_acres: 3.304545692925136,
              imp_area_acres: 0.36222350149989435,
            },
            {
              node_id: "6",
              surface_key: "10101000-RESSFH-D-0",
              area_acres: 9.63416946726306,
              imp_area_acres: 7.1542071673930625,
            },
            {
              node_id: "6",
              surface_key: "10101100-OSLOW-D-0",
              area_acres: 4.8579106327541695,
              imp_area_acres: 0.25541389152635474,
            },
            {
              node_id: "6",
              surface_key: "10101200-OSDEV-C-5",
              area_acres: 6.798391444820259,
              imp_area_acres: 2.2112485428708193,
            },
            {
              node_id: "6",
              surface_key: "10101000-RESSFH-D-10",
              area_acres: 3.4948300942486963,
              imp_area_acres: 3.233078107164885,
            },
            {
              node_id: "6",
              surface_key: "10101000-OSAGIR-A-10",
              area_acres: 3.6289953644281625,
              imp_area_acres: 0.38263683466075843,
            },
            {
              node_id: "6",
              surface_key: "10101100-OSDEV-D-0",
              area_acres: 5.376760581619445,
              imp_area_acres: 4.5257872671756365,
            },
          ],
        },
      },
      WatershedResponse: {
        title: "WatershedResponse",
        type: "object",
        properties: {
          status: { title: "Status", type: "string", default: "SUCCESS" },
          task_id: { title: "Task Id", type: "string" },
          result_route: { title: "Result Route", type: "string" },
          data: { $ref: "#/components/schemas/WatershedResults" },
        },
      },
      WatershedResults: {
        title: "WatershedResults",
        type: "object",
        properties: {
          results: {
            title: "Results",
            type: "array",
            items: { $ref: "#/components/schemas/Result" },
          },
          leaf_results: {
            title: "Leaf Results",
            type: "array",
            items: { $ref: "#/components/schemas/Result" },
          },
          previous_results_keys: {
            title: "Previous Results Keys",
            type: "array",
            items: { type: "string" },
          },
          errors: { title: "Errors", type: "array", items: { type: "string" } },
          warnings: {
            title: "Warnings",
            type: "array",
            items: { type: "string" },
          },
        },
      },
    },
  },
};
