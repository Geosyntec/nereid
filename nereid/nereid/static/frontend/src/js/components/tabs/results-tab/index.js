import { ResultsTab } from "./results-tab";
import * as results from "./result_summary";

const treatment_funcs = [
  // design summary
  results.table_facility_design_summary,

  // volume capture
  results.table_facility_capture,
  results.table_facility_volume_reduction,
  results.table_facility_total_volume_reduction,
  results.table_facility_wet_weather_volume_reduction,
  results.table_facility_dry_weather_volume_reduction,

  // load reduction
  results.table_facility_load_reduction,
  results.table_facility_total_load_reduction,
  results.table_facility_wet_weather_load_reduction,
  results.table_facility_dry_weather_load_reduction,
];

const ls_funcs = [
  results.table_land_surface_summary,
  results.table_land_surface_load_summary,
];

export const treatmentFacilityResultsTab = new ResultsTab({
  id: "treatment-facility-results-tab",
  table_builders: treatment_funcs,
});
export const landSurfaceResultsTab = new ResultsTab({
  id: "land-surface-results-tab",
  table_builders: ls_funcs,
});
