import * as util from "../../../../lib/util.js";

export const table_land_surface_summary = (data) => {
  let opts = {
    data,
    id: "table-land-surface-summary",
    title: "Land Surface Summary",
    filename_csv: "land_surface_summary.csv",
    prep_fnx: (dataset) => {
      let data_keys = ["node_id", "area_acres", "ro_coeff", "imp_pct"];
      let summary = (dataset || [])
        .filter((d) => d?.land_surfaces_count > 0)
        .map((d) => Object.fromEntries(Object.entries(d)));

      return [summary, data_keys];
    },
  };
  return opts;
};

export const table_land_surface_load_summary = (data) => {
  let opts = {
    data,
    id: "table-land-surface-load-summary",
    title: "Land Surface Loading Summary",
    filename_csv: "land_surface_load_summary.csv",
    prep_fnx: (dataset) => {
      let data_keys = ["node_id"];
      const summary_key_filter = function (k) {
        let is_load = k.endsWith("_load_lbs") || k.endsWith("_load_mpn");

        return data_keys.includes(k) || is_load;
      };
      let summary = (dataset || [])
        .filter((d) => d?.land_surfaces_count > 0)
        .map((d) =>
          Object.fromEntries(
            Object.entries(d).filter(([k, v]) => summary_key_filter(k))
          )
        );

      const summary_keys = [
        ...new Set(util.flatten(summary.map((d) => Object.keys(d)))),
      ];

      console.debug("landsurface load summary:", summary);

      return [summary, summary_keys];
    },
  };
  return opts;
};
