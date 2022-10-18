from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

import networkx as nx

from nereid.core.utils import safe_divide
from nereid.src.network.utils import sum_node_attr
from nereid.src.watershed.loading import compute_pollutant_load_reduction


def accumulate_dry_weather_loading(
    g: nx.DiGraph,
    data: Dict[str, Any],
    predecessors: List[str],
    dry_weather_parameters: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """This function helps aggregate the state of the watershed upstream of
    the current node for dry weather conditions. This function considers dry weather
    for two seasons per year, summer and winter.

    This function is only called by `nereid.src.watershed.solve_watershed.solve_node`

    Parameters
    ----------
    g : nx.DiGraph
        graph object used to fetch upstream information.
    data : dict
        information about the current node. this may be a land surface node, a treatment facility,
        or a treatment site.
    predecessors : list
        set of nodes immediately upstream of current node. These are used to aggregate flow
        volume and pollutant load.
    dry_weather_parameters : list of dicts
        this contains information aabout each parameter, like long_name, short_name and
        conversion factor information. see the *land_surface_emc_tables in the config file.
        these dicts are pre-processed to cache some helpful unit conversions prior to
        being passed to this function.
        Reference: `nereid.src.wq_parameters.init_wq_parameters`

    """

    if not dry_weather_parameters:
        return data

    seasons = ["summer", "winter"]

    for season in seasons:

        accumulate_dry_weather_volume_by_season(g, data, predecessors, season)
        accumulate_dry_weather_pollutant_loading_by_season(
            g, data, predecessors, dry_weather_parameters, season
        )

    return data


def accumulate_dry_weather_volume_by_season(
    g: nx.DiGraph,
    data: Dict[str, Any],
    predecessors: List[str],
    season: str,
) -> Dict[str, Any]:
    """aggregate dry weather volume for a single season

    This function is called only by `accumulate_dry_weather_loading`

    Parameters
    ----------
    * : see `accumulate_dry_weather_loading`
    season : string
        the season we want to aggregate.

    """

    for suffix in ["", "_psecond"]:

        dw_col = f"{season}_dry_weather_flow_cuft" + suffix

        data[dw_col] = data.get(dw_col, 0.0)

        data[f"{dw_col}_direct"] = sum_node_attr(g, predecessors, dw_col)

        data[f"{dw_col}_upstream"] = sum_node_attr(
            g, predecessors, f"{dw_col}_discharged"
        )
        data[f"{dw_col}_inflow"] = data[f"{dw_col}_direct"] + data[f"{dw_col}_upstream"]

        data[f"{dw_col}_retained_upstream"] = sum_node_attr(
            g, predecessors, f"{dw_col}_total_retained"
        )

        # initialize with assumption of no volume reduction
        data[f"{dw_col}_discharged"] = data[f"{dw_col}_inflow"]
        data[f"{dw_col}_total_discharged"] = data[f"{dw_col}_inflow"] + data[dw_col]
        data[f"{dw_col}_total_retained"] = data[f"{dw_col}_retained_upstream"]

    return data


def accumulate_dry_weather_pollutant_loading_by_season(
    g: nx.DiGraph,
    data: Dict[str, Any],
    predecessors: List[str],
    dry_weather_parameters: List[Dict[str, Any]],
    season: str,
) -> Dict[str, Any]:
    """aggregate dry weather pollutant load for a single season

    This function is called only by `accumulate_dry_weather_loading`

    Parameters
    ----------
    * : see `accumulate_dry_weather_loading`
    season : string
        the season we want to aggregate.

    """

    for param in dry_weather_parameters:

        inflow_volume = data[f"{season}_dry_weather_flow_cuft_inflow"]

        load_col = season + "_" + param["load_col"]
        conc_col = season + "_" + param["conc_col"]
        load_to_conc_factor = param["load_to_conc_factor"]
        data[load_col] = data.get(load_col, 0.0)

        data[f"{load_col}_direct"] = sum_node_attr(g, predecessors, load_col)

        data[f"{load_col}_upstream"] = sum_node_attr(
            g, predecessors, f"{load_col}_discharged"
        )
        inflow_load = data[f"{load_col}_inflow"] = (
            data[f"{load_col}_direct"] + data[f"{load_col}_upstream"]
        )

        data[f"{load_col}_removed_upstream"] = sum_node_attr(
            g, predecessors, f"{load_col}_total_removed"
        )

        influent_conc = safe_divide(inflow_load, inflow_volume) * load_to_conc_factor
        data[f"{conc_col}_influent"] = influent_conc

        # initialize with assumption of no treatment
        data[f"{conc_col}_effluent"] = influent_conc
        data[f"{load_col}_discharged"] = inflow_load
        data[f"{load_col}_total_discharged"] = inflow_load + data[load_col]
        data[f"{load_col}_total_removed"] = data[f"{load_col}_removed_upstream"]

    return data


def compute_dry_weather_volume_performance(data):
    """
    This function is only called by `nereid.src.watershed.solve_watershed.solve_node`
    This function must be called after:
        `accumulate_dry_weather_loading`

    """
    seasons = ["summer", "winter"]

    for season in seasons:
        init_dry_weather_tmnt_rate_by_season(data, season)
        compute_dry_weather_volume_performance_by_season(data, season)

    return data


def init_dry_weather_tmnt_rate_by_season(
    data: Dict[str, Any], season: str
) -> Dict[str, Any]:
    """This function helps normalize how the treatment rate for dry weather flow
    is credited, particularly for facilities that are volume-based and so have
    no treatment-rate type attributes. This function will consider the rate of
    treatment for each compartment of a volume based facility so that it's available
    to later calculations regarding dry weather volume reduction.

    This function is only called by `compute_dry_weather_volume_performance`

    """

    dw_retention_rate_cfs = data.get(f"{season}_dry_weather_retention_rate_cfs")
    months_operational = data.get("months_operational") or "both"
    is_operational = months_operational in [season, "both"]
    dwf_override = data.get("eliminate_all_dry_weather_flow_override") or False

    if is_operational and dwf_override:
        # This override will set the retention capacity to be equal to the inflow rate.
        dw_inflow_cfs = (
            data.get(f"{season}_dry_weather_flow_cuft_psecond_inflow") or 0.0
        )
        dw_retention_rate_cfs = dw_inflow_cfs
        data[f"{season}_dry_weather_retention_rate_cfs"] = dw_retention_rate_cfs

    if dw_retention_rate_cfs is None:
        retention_vol = data.get("retention_volume_cuft", 0.0)
        retention_ddt_seconds = data.get("retention_ddt_hr", 0.0) * 3600

        dw_retention_rate_cfs = safe_divide(retention_vol, retention_ddt_seconds)
        data[f"{season}_dry_weather_retention_rate_cfs"] = dw_retention_rate_cfs

    dw_treatment_rate_cfs = data.get(f"{season}_dry_weather_treatment_rate_cfs")
    if dw_treatment_rate_cfs is None:

        dw_treatment_rate_cfs = data.get("treatment_rate_cfs")
        treatment_volume_cuft = data.get("treatment_volume_cuft", 0.0)

        if dw_treatment_rate_cfs is None:
            if treatment_volume_cuft > 1e-3:

                treatment_ddt_seconds = data.get("treatment_ddt_hr", 0.0) * 3600

                dw_treatment_rate_cfs = safe_divide(
                    treatment_volume_cuft, treatment_ddt_seconds
                )
            else:
                dw_treatment_rate_cfs = 0.0

        data[f"{season}_dry_weather_treatment_rate_cfs"] = dw_treatment_rate_cfs

    return data


def compute_dry_weather_volume_performance_by_season(
    data: Dict[str, Any], season: str
) -> Dict[str, Any]:
    """This function checks to see if the dry weather flow rate can be eliminated
    by the retention rate, and if not, applies treatment to the discharge volume
    up to the treatment rate capacity. discharge rates higher than the treatment
    rate are considered bypassed flow.

    All performance is based on flow rate, and assume completely steaady state.
    Thus volume reduced and volume treated are computed ad stored based upon the
    flow rate performance.

    This function is only called by `compute_dry_weather_volume_performance`

    """

    dw_retention_rate_cfs = data.get(f"{season}_dry_weather_retention_rate_cfs", 0.0)
    dw_treatment_rate_cfs = data.get(f"{season}_dry_weather_treatment_rate_cfs", 0.0)
    months_operational = data.get("months_operational", "both")

    cfs_col = f"{season}_dry_weather_flow_cuft_psecond"
    dw_inflow_cfs_col = cfs_col + "_inflow"
    dw_inflow_cfs = data.get(dw_inflow_cfs_col, 0.0)

    vol_col = f"{season}_dry_weather_flow_cuft"
    dw_inflow_vol_col = vol_col + "_inflow"
    dw_inflow_vol = data.get(dw_inflow_vol_col, 0.0)

    vol_retained = 0.0
    vol_treated = 0.0
    dw_flow_rate_discharged = dw_inflow_cfs  # assume no flowrate attenuation
    dw_flow_retained_frac = 0.0
    dw_flow_treated_frac = 0.0
    dw_flow_tmnt_rate = 0.0

    if (months_operational in [season, "both"]) and (dw_inflow_cfs > 0):
        # this is the rate that is not able to be eliminated by retention
        # it may still be treated.
        _discharge_rate = max(dw_inflow_cfs - dw_retention_rate_cfs, 0)

        # this is the flowrate that will be discharged, and some of it may be treated.
        dw_flow_rate_discharged = min(_discharge_rate, dw_inflow_cfs)
        dw_flow_retained_frac = 1 - safe_divide(dw_flow_rate_discharged, dw_inflow_cfs)
        vol_retained = dw_flow_retained_frac * dw_inflow_vol

        if dw_flow_retained_frac < 1:
            dw_flow_tmnt_rate = min(dw_treatment_rate_cfs, dw_flow_rate_discharged)
            dw_flow_treated_frac = safe_divide(
                dw_flow_tmnt_rate, dw_flow_rate_discharged
            )
            vol_treated = dw_flow_treated_frac * (dw_inflow_vol - vol_retained)

    data[cfs_col + "_retained"] = dw_inflow_cfs - dw_flow_rate_discharged
    data[cfs_col + "_retained_pct"] = dw_flow_retained_frac * 100
    data[cfs_col + "_treated"] = dw_flow_tmnt_rate
    data[cfs_col + "_treated_pct"] = dw_flow_treated_frac * 100
    data[cfs_col + "_discharged"] = dw_flow_rate_discharged
    data[cfs_col + "_total_retained"] = data[cfs_col + "_retained"] + data.get(
        cfs_col + "_retained_upstream", 0.0
    )
    # for symmetry with non-treatment nodes.
    data[f"{cfs_col}_total_discharged"] = (
        data.get(cfs_col, 0) + data[f"{cfs_col}_discharged"]
    )

    data[vol_col + "_retained"] = vol_retained
    data[vol_col + "_retained_pct"] = 100 * safe_divide(vol_retained, dw_inflow_vol)

    data[vol_col + "_treated"] = vol_treated
    data[vol_col + "_treated_pct"] = 100 * safe_divide(vol_treated, dw_inflow_vol)

    data[vol_col + "_captured"] = vol_treated + vol_retained
    data[vol_col + "_captured_pct"] = 100 * safe_divide(
        vol_treated + vol_retained, dw_inflow_vol
    )

    data[vol_col + "_bypassed"] = max(dw_inflow_vol - (vol_treated + vol_retained), 0)
    data[vol_col + "_bypassed_pct"] = 100 * safe_divide(
        data[vol_col + "_bypassed"], dw_inflow_vol
    )

    data[vol_col + "_discharged"] = dw_inflow_vol - vol_retained
    data[vol_col + "_total_retained"] = data[vol_col + "_retained"] + data.get(
        vol_col + "_retained_upstream", 0.0
    )
    # for symmetry with non-treatment nodes.
    data[f"{vol_col}_total_discharged"] = (
        data.get(vol_col, 0) + data[f"{vol_col}_discharged"]
    )

    return data


def compute_dry_weather_load_reduction(
    data: Dict[str, Any],
    dry_weather_parameters: List[Dict[str, Any]],
    dry_weather_facility_performance_map: Mapping[Tuple[str, str], Callable],
) -> Dict[str, Any]:
    """This function computes how load reduction is effected by the volume reduced
    and/or treated by the current facility. This function requires that the volume
    balance is already computed.

    This function is only called by `nereid.src.watershed.solve_watershed.solve_node`
    This function must be called after all of the following have been called:
        `accumulate_dry_weather_loading`
        `compute_dry_weather_volume_performance`

    Parameters
    ----------
    data : dict
        information about current node, including facility sizing information and
        inflow characteristics.
    dry_weather_parameters: list of dicts
        this contains information aabout each parameter, like long_name, short_name and
        conversion factor information. see the *land_surface_emc_tables in the config file.
        these dicts are pre-processed to cache some helpful unit conversions too prior to
        being passed to this function.
        Reference: `nereid.src.wq_parameters.init_wq_parameters`
    dry_weather_facility_performance_map : mapping
        this mapping uses a facility type and a pollutant as the keys to retrieve a function
        that returns effluent concentration as output when given influent concentration as input.
        Reference: `nereid.src.tmnt_performance.tmnt.effluent_conc`
        Reference: `nereid.src.tmnt_performance.tasks.effluent_function_map`

    """

    tmnt_facility_type = data.get("tmnt_performance_facility_type", r"¯\_(ツ)_/¯")

    seasons = ["summer", "winter"]
    for season in seasons:
        vol_col = f"{season}_dry_weather_flow_cuft"

        for param in dry_weather_parameters:
            conc_unit = param["concentration_unit"]
            poc_long = param["long_name"]

            load_col = season + "_" + param["load_col"]
            conc_col = season + "_" + param["conc_col"]

            load_to_conc_factor = param["load_to_conc_factor"]
            conc_to_load_factor = param["conc_to_load_factor"]

            inflow_load = data[f"{load_col}_inflow"]
            influent_conc = data[f"{conc_col}_influent"]

            compute_pollutant_load_reduction(
                data,
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

    return data
