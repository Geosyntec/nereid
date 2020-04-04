from copy import deepcopy
from itertools import product
from typing import Any, Callable, Dict, List, Mapping, Tuple

from nereid.core.utils import safe_divide
from nereid.src.watershed.loading import compute_pollutant_load_reduction


def solve_treatment_site(
    data: Dict[str, Any],
    wet_weather_parameters: List[Dict[str, Any]],
    dry_weather_parameters: List[Dict[str, Any]],
    wet_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
    dry_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
) -> Dict[str, Any]:

    compute_site_volume_capture(data)
    compute_site_wet_weather_load_reduction(
        data, wet_weather_parameters, wet_weather_facility_performance_map
    )
    compute_site_dry_weather_load_reduction(
        data, dry_weather_parameters, dry_weather_facility_performance_map
    )

    return data


def compute_site_volume_capture(data):

    _compute_site_volume_capture(data, "runoff_volume_cuft")
    for attr in ["captured", "treated", "retained", "bypassed"]:
        data[f"{attr}_pct"] = data[f"runoff_volume_cuft_{attr}_pct"]

    seasons = ["summer", "winter"]
    vol_cols = [f"{s}_dry_weather_flow_cuft" for s in seasons]

    for vol_col in vol_cols:
        _compute_site_volume_capture(data, vol_col)

    return data


def _compute_site_volume_capture(data: Dict[str, Any], vol_col: str) -> Dict[str, Any]:

    site_inflow_volume = data.get(f"{vol_col}_inflow", 0)
    facilities = data.get("treatment_facilities", [])

    for facility_data in facilities:
        facility_data["node_errors"] = []
        facility_data["node_warnings"] = []

        site_fraction = facility_data["area_pct"] / 100
        captured_fraction = facility_data["captured_pct"] / 100
        retained_fraction = facility_data["retained_pct"] / 100
        treated_fraction = max(0, captured_fraction - retained_fraction)

        facility_inflow_volume = facility_data[f"{vol_col}_inflow"] = (
            site_inflow_volume * site_fraction
        )

        facility_data[f"{vol_col}_captured"] = (
            facility_inflow_volume * captured_fraction
        )

        facility_data[f"{vol_col}_retained"] = (
            facility_inflow_volume * retained_fraction
        )

        facility_data[f"{vol_col}_treated"] = facility_inflow_volume * treated_fraction

        facility_data[f"{vol_col}_discharged"] = (
            facility_inflow_volume - facility_data[f"{vol_col}_retained"]
        )

        facility_data[f"{vol_col}_bypassed"] = facility_inflow_volume * (
            1 - captured_fraction
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
    data: Dict[str, Any],
    wet_weather_parameters: List[Dict[str, Any]],
    wet_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
) -> Dict[str, Any]:

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
    data: Dict[str, Any],
    dry_weather_parameters: List[Dict[str, Any]],
    dry_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
) -> Dict[str, Any]:

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
