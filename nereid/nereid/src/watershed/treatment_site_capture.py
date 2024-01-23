from itertools import product
from typing import Any, Callable

from nereid.core.utils import safe_divide
from nereid.src.watershed.loading import compute_pollutant_load_reduction
from nereid.src.watershed.simple_facility_capture import (
    compute_simple_facility_volume_capture,
)


def solve_treatment_site(
    data: dict[str, Any],
    *,
    wet_weather_parameters: list[dict[str, Any]],
    dry_weather_parameters: list[dict[str, Any]],
    wet_weather_facility_performance_map: dict[tuple[str, str], Callable],
    dry_weather_facility_performance_map: dict[tuple[str, str], Callable],
) -> dict[str, Any]:
    """This function computes the volume reduction/capture performance and the
    load reduction for each individual facility of a treatment site. Treatment sites
    are a list of facility types on the site, and for each the user has specified
    the % site area treated, % inflow volume captured, and % inflow volume retained
    by the facility. This function solves each facility individually, and then aggregates
    the suite of facilities into a single 'node' of volume and load transformed by the
    site activities.

    This function is only called by `.solve_watershed.solve_node`
    This function must be called after all of the following have been called:
        `.dry_weather_loading.accumulate_dry_weather_loading`
        `.wet_weather_loading.accumulate_wet_weather_loading`


    Parameters
    ----------
    *_parameters: list of dicts
        this contains information aabout each parameter, like long_name, short_name and
        conversion factor information. see the *land_surface_emc_tables in the config file.
        these dicts are pre-processed to cache some helpful unit conversions too prior to
        being passed to this function.
        This is needed for both wet weather and dry weather.
        Reference: `nereid.src.wq_parameters.init_wq_parameters`

    *_facility_performance_map : mapping
        this mapping uses a facility type and a pollutant as the keys to retrieve a function
        that returns effluent concentration as output when given influent concentration as input.
        This is needed for both wet weather and dry weather.
        Reference: `nereid.src.tmnt_performance.tmnt.effluent_conc`
        Reference: `nereid.src.tmnt_performance.tasks.effluent_function_map`

    """

    compute_site_volume_capture(data)
    compute_site_wet_weather_load_reduction(
        data, wet_weather_parameters, wet_weather_facility_performance_map
    )
    if all(map(len, [dry_weather_parameters, dry_weather_facility_performance_map])):
        compute_site_dry_weather_load_reduction(
            data,
            dry_weather_parameters,  # type: ignore
            dry_weather_facility_performance_map,  # type: ignore
        )

    return data


def compute_site_volume_capture(data):
    _compute_site_volume_capture(data, "runoff_volume_cuft")
    for attr in ["captured", "treated", "retained", "bypassed"]:
        data[f"{attr}_pct"] = data[f"runoff_volume_cuft_{attr}_pct"]

    seasons = ["summer", "winter"]
    vol_cols = [f"{s}_dry_weather_flow_cuft" for s in seasons] + [
        f"{s}_dry_weather_flow_cuft_psecond" for s in seasons
    ]

    for vol_col in vol_cols:
        _compute_site_volume_capture(data, vol_col)

    return data


def _compute_site_volume_capture(data: dict[str, Any], vol_col: str) -> dict[str, Any]:
    site_inflow_volume = data.get(f"{vol_col}_inflow", 0)
    facilities = data.get("treatment_facilities", [])

    for facility_data in facilities:
        site_fraction = facility_data["area_pct"] / 100
        facility_data[f"{vol_col}_inflow"] = site_inflow_volume * site_fraction

        facility_data = compute_simple_facility_volume_capture(
            facility_data, vol_col=vol_col
        )

        for attr in ["captured", "treated", "retained", "bypassed"]:
            data[f"{vol_col}_{attr}"] = (
                data.get(f"{vol_col}_{attr}", 0) + facility_data[f"{vol_col}_{attr}"]
            )

    data[f"{vol_col}_discharged"] = site_inflow_volume - data.get(
        f"{vol_col}_retained", 0
    )

    # for symmetry with non-treatment nodes.
    data[f"{vol_col}_total_discharged"] = (
        data.get(vol_col, 0) + data[f"{vol_col}_discharged"]
    )

    for attr in ["captured", "treated", "retained", "bypassed"]:
        partial_volume = data.get(f"{vol_col}_{attr}", 0)
        data[f"{vol_col}_{attr}_pct"] = 100 * safe_divide(
            partial_volume, site_inflow_volume
        )

    data[f"{vol_col}_total_retained"] = data.get(f"{vol_col}_retained", 0.0) + data.get(
        f"{vol_col}_retained_upstream", 0.0
    )

    return data


def compute_site_wet_weather_load_reduction(
    data: dict[str, Any],
    wet_weather_parameters: list[dict[str, Any]],
    wet_weather_facility_performance_map: dict[tuple[str, str], Callable],
) -> dict[str, Any]:
    facilities = data.get("treatment_facilities", [])
    vol_col = "runoff_volume_cuft"

    for facility_data in facilities:
        tmnt_facility_type = facility_data.get(
            "tmnt_performance_facility_type", r"¯\_(ツ)_/¯"
        )

        for param in wet_weather_parameters:
            conc_unit = param["concentration_unit"]
            poc_long = param["long_name"]

            load_col = param["load_col"]
            conc_col = param["conc_col"]

            load_to_conc_factor = param["load_to_conc_factor"]
            conc_to_load_factor = param["conc_to_load_factor"]

            conc_to_load_factor = param["conc_to_load_factor"]

            influent_conc = facility_data[f"{conc_col}_influent"] = data[
                f"{conc_col}_influent"
            ]
            inflow_load = facility_data[f"{load_col}_inflow"] = (
                facility_data[f"{vol_col}_inflow"] * influent_conc * conc_to_load_factor
            )

            compute_pollutant_load_reduction(
                facility_data,
                wet_weather_facility_performance_map,
                tmnt_facility_type,
                conc_unit,
                poc_long,
                load_col,
                conc_col,
                vol_col,
                load_to_conc_factor,
                conc_to_load_factor,
                inflow_load,
                influent_conc,
            )

    # combine individual facilities into a total value to report for the node.
    for param in wet_weather_parameters:
        load_col = param["load_col"]
        conc_col = param["conc_col"]
        load_to_conc_factor = param["load_to_conc_factor"]

        # accumulate loads reduced on the whole wqmp site
        data[f"{load_col}_discharged"] = sum(
            [
                facility_data.get(f"{load_col}_discharged", 0)
                for facility_data in facilities
            ]
        )

        data[f"{load_col}_removed"] = sum(
            [
                facility_data.get(f"{load_col}_removed", 0)
                for facility_data in facilities
            ]
        )

        data[f"{load_col}_total_removed"] = data[f"{load_col}_removed"] + data.get(
            f"{load_col}_removed_upstream", 0.0
        )

        discharge_conc = (
            safe_divide(data[f"{load_col}_discharged"], data[f"{vol_col}_discharged"])
            * load_to_conc_factor
        )
        data[f"{conc_col}_effluent"] = discharge_conc

        # for symmetry with non-treatment nodes, though it's the same as '_discharge'.
        data[f"{load_col}_total_discharged"] = (
            data[load_col] + data[f"{load_col}_discharged"]
        )

    return data


def compute_site_dry_weather_load_reduction(
    data: dict[str, Any],
    dry_weather_parameters: list[dict[str, Any]],
    dry_weather_facility_performance_map: dict[tuple[str, str], Callable],
) -> dict[str, Any]:
    facilities = data.get("treatment_facilities", [])
    seasons = ["summer", "winter"]

    for facility_data in facilities:
        tmnt_facility_type = facility_data.get(
            "tmnt_performance_facility_type", r"¯\_(ツ)_/¯"
        )

        for season, param in product(seasons, dry_weather_parameters):
            vol_col = f"{season}_dry_weather_flow_cuft"

            conc_unit = param["concentration_unit"]
            poc_long = param["long_name"]

            load_col = season + "_" + param["load_col"]
            conc_col = season + "_" + param["conc_col"]

            load_to_conc_factor = param["load_to_conc_factor"]
            conc_to_load_factor = param["conc_to_load_factor"]

            conc_to_load_factor = param["conc_to_load_factor"]

            influent_conc = facility_data[f"{conc_col}_influent"] = data[
                f"{conc_col}_influent"
            ]
            inflow_load = facility_data[f"{load_col}_inflow"] = (
                facility_data[f"{vol_col}_inflow"] * influent_conc * conc_to_load_factor
            )

            compute_pollutant_load_reduction(
                facility_data,
                dry_weather_facility_performance_map,
                tmnt_facility_type,
                conc_unit,
                poc_long,
                load_col,
                conc_col,
                vol_col,
                load_to_conc_factor,
                conc_to_load_factor,
                inflow_load,
                influent_conc,
            )

    # combine individual facilities into a total value to report for the node.
    for season, param in product(seasons, dry_weather_parameters):
        vol_col = f"{season}_dry_weather_flow_cuft"

        load_col = season + "_" + param["load_col"]
        conc_col = season + "_" + param["conc_col"]
        load_to_conc_factor = param["load_to_conc_factor"]

        # accumulate loads reduced on the whole wqmp site
        data[f"{load_col}_discharged"] = sum(
            [
                facility_data.get(f"{load_col}_discharged", 0)
                for facility_data in facilities
            ]
        )

        data[f"{load_col}_removed"] = sum(
            [
                facility_data.get(f"{load_col}_removed", 0)
                for facility_data in facilities
            ]
        )

        data[f"{load_col}_total_removed"] = data[f"{load_col}_removed"] + data.get(
            f"{load_col}_removed_upstream", 0.0
        )

        discharge_conc = (
            safe_divide(data[f"{load_col}_discharged"], data[f"{vol_col}_discharged"])
            * load_to_conc_factor
        )
        data[f"{conc_col}_effluent"] = discharge_conc

        # for symmetry with non-treatment nodes, though it's the same as '_discharge'.
        data[f"{load_col}_total_discharged"] = (
            data[load_col] + data[f"{load_col}_discharged"]
        )

    return data
