import * as util from "../../../../lib/util.js";

export function table_facility_load_reduction(data) {
  let opts = {
    data,
    id: "table-facility-load-reduction",
    title: "Facility Load Reduction Results",
    description: `These results are separated in to wet weather results,
    summer dry weather results, and winter dry weather results.`,
    filename_csv: "load_reduction_results.csv",
    prep_fnx: (dataset) => {
      const base = [
        "node_id",
        // "facility_type"
      ];

      const summary_keys_filter = function (k) {
        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");
        return base.includes(k) || is_load;
      };

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const load_keys_base = all_keys.filter((k) => {
        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");
        let is_wet = !k.includes("dw");
        return is_load && is_wet;
      });

      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(
              ([k, v]) => summary_keys_filter(k)
              // k.includes("_pct") & !k.includes("dry")
            )
          )
        );

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;

      for (let k of load_keys_base.sort()) {
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

export function table_facility_total_load_reduction(data) {
  let opts = {
    data,
    id: "table-facility-total-load-reduction",
    title: "Facility Total Load Reduction Results",
    description: "(calculated as total of results for wet + summer + dry)",
    filename_csv: "total_load_reduction_results.csv",
    prep_fnx: (dataset) => {
      let base = ["node_id"];

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const load_keys_base = all_keys.filter((k) => {
        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");
        let is_wet = !k.includes("dw");
        return is_load && is_wet;
      });

      const summary_key_filter = function (k) {
        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");

        return base.includes(k) || is_load; //|| is_vol; // && is_dry);
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
        for (let k of load_keys_base) {
          let wet = d[k];
          let summer = d[`summer_dw${k}`];
          let winter = d[`winter_dw${k}`];
          d[`total_${k}`] = wet + summer + winter;
          // console.log(k, wet, summer, winter);
        }
      }

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;

      for (let k of load_keys_base.sort()) {
        let keys = summary_keys
          .filter((d) => d.includes(k))
          .filter((d) => d.includes("total"))
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

export function table_facility_wet_weather_load_reduction(data) {
  let opts = {
    data,
    id: "table-facility-wet-weather-load-reduction",
    title: "Facility Wet Weather Load Reduction Results",
    filename_csv: "wet_weather_load_reduction_results.csv",
    prep_fnx: (dataset) => {
      const summary_keys = function (k) {
        let base = [
          "node_id",
          // "facility_type"
        ].includes(k);

        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");
        let is_dry = k.includes("dw");

        return base || (is_load && !is_dry);
      };

      let summary = (dataset || [])
        .filter((d) => d.node_type)
        .filter((d) => d.node_type.includes("facility"))
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => summary_keys(k))
          )
        );
      const data_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];
      return [summary, data_keys];
    },
  };
  return opts;
}

export function table_facility_dry_weather_load_reduction(data) {
  let opts = {
    data,
    id: "table-facility-dry-weather-load-reduction",
    title: "Facility Dry Weather Load Reduction Results",
    description: `Includes summer dry weather, winter dry weather, and total dry
      weather results (calculated as summer + winter)`,
    filename_csv: "dry_weather_load_reduction_results.csv",
    prep_fnx: (dataset) => {
      let base = [
        "node_id",
        // "facility_type"
      ];

      const all_keys = [
        ...new Set(util.flatten(dataset.map((d) => Object.keys(d)))),
      ];

      const load_keys_base = all_keys.filter((k) => {
        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");
        let is_wet = !k.includes("dw");
        return is_load && is_wet;
      });

      const summary_key_filter = function (k) {
        let is_load = k.endsWith("lbs_removed") || k.endsWith("mpn_removed");
        let is_dry = k.includes("dw");

        return base.includes(k) || (is_load && is_dry);
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
        for (let k of load_keys_base) {
          let summer = d[`summer_dw${k}`];
          let winter = d[`winter_dw${k}`];
          d[`total_dw${k}`] = summer + winter;
        }
      }

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      const data_keys = base;
      for (let k of load_keys_base.sort()) {
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
