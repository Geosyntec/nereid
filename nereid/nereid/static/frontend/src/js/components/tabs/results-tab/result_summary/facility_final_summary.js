export const table_facility_report_summary = (data) => {
  let opts = {
    data,
    id: "table-facility-report-summary",
    title: "Facility report Summary",
    filename_csv: "facility_report_summary.csv",
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
