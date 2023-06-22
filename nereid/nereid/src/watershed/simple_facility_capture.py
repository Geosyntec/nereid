from typing import Any, Dict

from nereid.core.utils import safe_divide


def compute_simple_facility_volume_capture(
    data: Dict[str, Any], vol_col: str
) -> Dict[str, Any]:

    inflow_volume = data.get(f"{vol_col}_inflow", 0)

    data["node_errors"] = []
    data["node_warnings"] = []

    # check if we are solving for dry weather water balance, and if so, is there
    # an override condition
    dwf_override = data.get("eliminate_all_dry_weather_flow_override")
    is_dwf = any(s in vol_col for s in ["summer", "winter"])

    if is_dwf and dwf_override:
        captured_fraction = retained_fraction = 1
    else:
        captured_fraction = data["captured_pct"] / 100
        retained_fraction = data["retained_pct"] / 100

    treated_fraction = max(0, captured_fraction - retained_fraction)

    data[f"{vol_col}_captured"] = inflow_volume * captured_fraction

    data[f"{vol_col}_retained"] = inflow_volume * retained_fraction

    data[f"{vol_col}_treated"] = inflow_volume * treated_fraction

    data[f"{vol_col}_discharged"] = inflow_volume - data[f"{vol_col}_retained"]

    data[f"{vol_col}_bypassed"] = inflow_volume * (1 - captured_fraction)

    for attr in ["captured", "treated", "retained", "bypassed"]:
        partial_volume = data.get(f"{vol_col}_{attr}", 0)
        data[f"{vol_col}_{attr}_pct"] = 100 * safe_divide(partial_volume, inflow_volume)

    data[f"{vol_col}_discharged"] = inflow_volume - data.get(f"{vol_col}_retained", 0)

    # for symmetry with non-treatment nodes.
    data[f"{vol_col}_total_discharged"] = (
        data.get(vol_col, 0) + data[f"{vol_col}_discharged"]
    )

    data[f"{vol_col}_total_retained"] = data.get(f"{vol_col}_retained", 0.0) + data.get(
        f"{vol_col}_retained_upstream", 0.0
    )

    return data


def compute_simple_facility_wet_weather_volume_capture(
    data: Dict[str, Any]
) -> Dict[str, Any]:
    compute_simple_facility_volume_capture(data, "runoff_volume_cuft")
    for attr in ["captured", "treated", "retained", "bypassed"]:
        data[f"{attr}_pct"] = data[f"runoff_volume_cuft_{attr}_pct"]

    return data


def compute_simple_facility_dry_weather_volume_capture(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    seasons = ["summer", "winter"]
    vol_cols = [f"{s}_dry_weather_flow_cuft" for s in seasons] + [
        f"{s}_dry_weather_flow_cuft_psecond" for s in seasons
    ]

    for vol_col in vol_cols:
        compute_simple_facility_volume_capture(data, vol_col)

    return data
