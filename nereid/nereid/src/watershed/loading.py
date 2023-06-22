from typing import Any, Callable, Dict, Mapping, Tuple

from nereid.core.utils import safe_divide


def compute_pollutant_load_reduction(
    data: Dict[str, Any],
    effluent_function_map: Mapping[Tuple[str, str], Callable],
    tmnt_facility_type: str,
    conc_unit: str,
    poc_long: str,
    load_col: str,
    conc_col: str,
    vol_col: str,
    load_to_conc_factor: float,
    conc_to_load_factor: float,
    inflow_load: float,
    influent_conc: float,
) -> Dict[str, Any]:
    """This function takes an irritating number of parameters, but helps to make the following
    recipe for calculating the loads given the volume and the concentration much more
    reusable, if verbose.

    This function is called by:
        .dry_weather_loading.compute_dry_weather_load_reduction
        .treatment_site_capture.compute_site_wet_weather_load_reduction
        .treatment_site_capture.compute_site_dry_weather_load_reduction
        .wet_weather_loading.compute_wet_weather_load_reduction

    Parameters
    ----------
    data : dict
        information about the current node, especially treatment performance (if any), and
        incoming flow volume and concentraiton
    effluent_function_map : mapping
        This mapping uses a facility type and a pollutant as the keys to retrieve a function
        that returns effluent concentration as output when given influent concentration as input.
        This is needed for both wet weather and dry weather.
        Reference: `nereid.src.tmnt_performance.tmnt.effluent_conc`
        Reference: `nereid.src.tmnt_performance.tasks.effluent_function_map`
    tmnt_facility_type : string
        string matching one of the facility types in the reference data file which defines the
        influent -> effluent transformation curves.
        Reference: config.yml::project_reference_data::tmnt_performance_table
    ** : strings and floats
        named and documented in function definition.

    """

    tmnt_fxn = effluent_function_map.get((tmnt_facility_type, poc_long), None)

    if tmnt_fxn is None:

        def tmnt_fxn(inf_conc, inf_unit):
            return inf_conc

        data["node_warnings"].append(
            f"WARNING: treatment function not found for ({tmnt_facility_type}, {poc_long})"
        )

    effluent_conc = tmnt_fxn(inf_conc=influent_conc, inf_unit=conc_unit)
    data[f"{conc_col}_treated_effluent"] = effluent_conc

    mass_from_bypassed = (
        data[f"{vol_col}_bypassed"] * influent_conc * conc_to_load_factor
    )
    data[f"{load_col}_released_from_bypassed"] = mass_from_bypassed

    mass_from_treated = data[f"{vol_col}_treated"] * effluent_conc * conc_to_load_factor
    data[f"{load_col}_released_from_treated"] = mass_from_treated

    # make sure treatment nodes are not 'sources' of load due to floating point precision
    load_discharged = min(inflow_load, mass_from_bypassed + mass_from_treated)
    data[f"{load_col}_discharged"] = load_discharged

    load_removed = inflow_load - load_discharged
    data[f"{load_col}_removed"] = load_removed

    # Use this value for reporting cumulative load removal upstream and including current node.
    data[f"{load_col}_total_removed"] = load_removed + data.get(
        f"{load_col}_removed_upstream", 0.0
    )

    discharge_conc = load_to_conc_factor * safe_divide(
        load_discharged, data[f"{vol_col}_discharged"]
    )
    data[f"{conc_col}_effluent"] = discharge_conc

    load_reduced_by_retention = (
        data[f"{vol_col}_retained"] * influent_conc * conc_to_load_factor
    )

    load_reduced_by_treatment = (
        data[f"{vol_col}_treated"] * influent_conc * conc_to_load_factor
        - mass_from_treated
    )

    mass_balance = inflow_load - (
        load_reduced_by_retention
        + load_reduced_by_treatment
        + mass_from_treated
        + mass_from_bypassed
    )

    if safe_divide(abs(mass_balance), inflow_load) > 0.01:  # pragma: no cover
        data["node_errors"].append(
            f"ERROR: pollutant mass balance error for {load_col}"
        )

    # Use this value for reporting total load discharged from current node, accounting
    # for all upstream inputs and reductions.
    load = data.get(load_col, 0.0)
    data[f"{load_col}_total_discharged"] = load + data[f"{load_col}_discharged"]

    return data
