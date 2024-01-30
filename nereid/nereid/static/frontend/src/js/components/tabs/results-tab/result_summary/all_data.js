import * as util from "../../../../lib/util.js";

export function table_all_data(data) {
  let opts = {
    data,
    id: "table-all-data",
    title: "Raw Results",
    description: `Raw results do not include the calculated sub totals (e.g., wet + dry).
    These data are the data source from which the calculated values are based.`,
    filename_csv: "raw_results.csv",
    prep_fnx: (dataset) => [
      dataset,
      [...new Set(util.flatten(dataset.map((d) => Object.keys(d))))],
    ],
  };
  return opts;
}
