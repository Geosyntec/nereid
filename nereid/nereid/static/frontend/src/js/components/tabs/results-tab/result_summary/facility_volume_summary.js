import * as util from "../../../../lib/util.js";

export const table_facility_design_summary = (data) => {
  let opts = {
    data,
    id: "table-facility-design-summary",
    title: "Facility design Summary",
    filename_csv: "facility_design_summary.csv",
    prep_fnx: (dataset) => {
      const data_keys = [
        "node_id",
        "facility_type",
        "valid_model",
        "design_intensity_inhr",
        "design_volume_cuft_cumul",
      ];
      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => data_keys.includes(k))
          )
        );

      return [summary, data_keys];
    },
  };
  return opts;
};

export const table_facility_capture = (data) => {
  let opts = {
    data,
    id: "table-facility-wet-weather-capture",
    title: "Facility Wet Weather Volume Capture Results",
    filename_csv: "wet_weather_volume_capture_results.csv",
    prep_fnx: (dataset) => {
      const data_keys = [
        "node_id",
        "facility_type",
        "valid_model",
        "captured_pct",
        "treated_pct",
        "retained_pct",
        "bypassed_pct",
        "peak_flow_mitigated_pct",
      ];
      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => data_keys.includes(k))
          )
        );

      return [summary, data_keys];
    },
  };
  return opts;
};

export function table_facility_volume_reduction(data) {
  let opts = {
    data,
    id: "table-facility-volume-reduction",
    title: "Facility Volume Reduction Results",
    // description: "",
    filename_csv: "volume_reduction_results.csv",
    prep_fnx: (dataset) => {
      let base = ["node_id"];

      const flow_types = [
        "inflow",
        "treated",
        "retained",
        "captured",
        "bypassed",
      ];

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const volume_keys_base = all_keys.filter((k) => {
        let is_dry_result = flow_types.some((t) =>
          k.endsWith(`dry_weather_flow_cuft_${t}`)
        );
        let is_wet_result = flow_types.some((t) =>
          k.endsWith(`runoff_volume_cuft_${t}`)
        );
        return is_dry_result || is_wet_result;
      });

      // console.log(volume_keys_base);

      const summary_key_filter = function (k) {
        return base.includes(k) || volume_keys_base.includes(k);
      };

      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => summary_key_filter(k))
          )
        );

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;

      for (let k of flow_types) {
        let keys = summary_keys
          .filter((d) => d.includes(k))
          .sort((a, b) => {
            // if (a.includes("total")) return 1;
            if (a.includes("winter")) return 1;
            if (a.includes("summer")) return 1;
            return -1;
          });
        data_keys.push(...keys);
      }

      return [summary, data_keys];
    },
  };
  return opts;
}

export function table_facility_wet_weather_volume_reduction(data) {
  let opts = {
    data,
    id: "table-facility-wet-weather-volume-reduction",
    title: "Facility Wet Weather Volume Reduction Results",
    filename_csv: "wet_weather_volume_reduction_results.csv",
    prep_fnx: (dataset) => {
      let base = ["node_id"];

      const flow_types = [
        "inflow",
        "treated",
        "retained",
        "captured",
        "bypassed",
      ];

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const volume_keys_base = all_keys.filter((k) => {
        let is_dry_result = flow_types.some((t) =>
          k.endsWith(`dry_weather_flow_cuft_${t}`)
        );
        let is_wet_result = flow_types.some((t) =>
          k.endsWith(`runoff_volume_cuft_${t}`)
        );
        return is_wet_result;
      });

      const summary_key_filter = function (k) {
        return base.includes(k) || volume_keys_base.includes(k);
      };

      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => summary_key_filter(k))
          )
        );

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;

      for (let k of flow_types) {
        let keys = summary_keys.filter((d) => d.includes(k));
        data_keys.push(...keys);
      }

      return [summary, data_keys];
    },
  };
  return opts;
}

export function table_facility_dry_weather_volume_reduction(data) {
  let opts = {
    data,
    id: "table-facility-dry-weather-volume-reduction",
    title: "Facility Dry Weather Volume Reduction Results",
    description: "(calculated as total of summer + winter)",
    filename_csv: "dry_weather_volume_reduction_results.csv",
    prep_fnx: (dataset) => {
      let base = ["node_id"];

      const flow_types = [
        "inflow",
        "treated",
        "retained",
        "captured",
        "bypassed",
      ];

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const volume_keys_base = all_keys.filter((k) => {
        let is_dry_result = flow_types.some((t) =>
          k.endsWith(`dry_weather_flow_cuft_${t}`)
        );
        let is_wet_result = flow_types.some((t) =>
          k.endsWith(`runoff_volume_cuft_${t}`)
        );
        return is_dry_result; //|| is_wet_result;
      });

      // console.log(volume_keys_base);

      const summary_key_filter = function (k) {
        return base.includes(k) || volume_keys_base.includes(k);
      };

      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => summary_key_filter(k))
          )
        );

      for (let d of summary) {
        for (let k of flow_types) {
          // let wet = d[`runoff_volume_cuft_${k}`];
          let summer = d[`summer_dry_weather_flow_cuft_${k}`];
          let winter = d[`winter_dry_weather_flow_cuft_${k}`];
          d[`total_dry_weather_volume_cuft_${k}`] = summer + winter;
        }
      }

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;

      for (let k of flow_types) {
        let keys = summary_keys
          .filter((d) => d.includes(k))
          .sort((a, b) => {
            if (a.includes("total")) return 1;
            if (a.includes("winter")) return 1;
            if (a.includes("summer")) return 1;
            return -1;
          });
        data_keys.push(...keys);
      }

      return [summary, data_keys];
    },
  };
  return opts;
}

export function table_facility_total_volume_reduction(data) {
  let opts = {
    data,
    id: "table-facility-total-volume-reduction",
    title: "Facility Total Volume Reduction Results",
    description: "(calculated as total of results for wet + summer + winter)",
    filename_csv: "total_volume_reduction_results.csv",
    prep_fnx: (dataset) => {
      let base = ["node_id"];

      const flow_types = [
        "inflow",
        "treated",
        "retained",
        "captured",
        "bypassed",
      ];

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const volume_keys_base = all_keys.filter((k) => {
        let is_dry_result = flow_types.some((t) =>
          k.endsWith(`dry_weather_flow_cuft_${t}`)
        );
        let is_wet_result = flow_types.some((t) =>
          k.endsWith(`runoff_volume_cuft_${t}`)
        );
        return is_dry_result || is_wet_result;
      });

      // console.log(volume_keys_base);

      const summary_key_filter = function (k) {
        return base.includes(k) || volume_keys_base.includes(k);
      };

      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => summary_key_filter(k))
          )
        );

      for (let d of summary) {
        for (let k of flow_types) {
          let wet = d[`runoff_volume_cuft_${k}`];
          let summer = d[`summer_dry_weather_flow_cuft_${k}`];
          let winter = d[`winter_dry_weather_flow_cuft_${k}`];
          d[`total_volume_cuft_${k}`] = wet + summer + winter;
        }
      }

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;

      for (let k of flow_types) {
        let keys = summary_keys
          .filter((d) => d.includes(k))
          .filter((d) => d.includes("total"));
        // .sort((a, b) => {
        //   if (a.includes("total")) return 1;
        //   if (a.includes("winter")) return 1;
        //   if (a.includes("summer")) return 1;
        //   return -1;
        // });
        data_keys.push(...keys);
      }

      return [summary, data_keys];
    },
  };
  return opts;
}
