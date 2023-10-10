from typing import Any, Callable

import networkx as nx

from nereid.core.utils import safe_divide
from nereid.src.network.utils import sum_node_attr
from nereid.src.watershed.design_functions import design_volume_cuft
from nereid.src.watershed.loading import compute_pollutant_load_reduction


def accumulate_wet_weather_loading(
    g: nx.DiGraph,
    data: dict[str, Any],
    predecessors: list[str],
    wet_weather_parameters: list[dict[str, Any]],
) -> dict[str, Any]:
    """This function helps aggregate the state of the watershed upstream of
    the current node for wet weather conditions.

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
    wet_weather_parameters : list of dicts
        this contains information aabout each parameter, like long_name, short_name and
        conversion factor information. see the *land_surface_emc_tables in the config file.
        these dicts are pre-processed to cache some helpful unit conversions prior to
        being passed to this function.
        Reference: `nereid.src.wq_parameters.init_wq_parameters`

    IMPORTANT NOTE: land surface nodes do not drain to themselves. Flow 'introduced'
    by an in-line land surface node is counted as 'direct' flow into then next
    downstream node. For convenience, the "_total_cumul" includes the effect of the
    current node, but we never accumulate upstream 'total cumul' values because it
    double counts the value sourced from the node.

    Treatment effects (e.g., retention) will *never* occur in the same node as
    runoff generation, effective area generation, or pollutant loading generation.
    Therefore, the equations for tracking their accumulation are slightly different.

    generally land surface values do not include the current node in the "cumul", but
    treatment related values do.

    this accumulation function avoids double counting and enables accumulations
    with subgraphs by storing multiple values for each attribute. For example,
    "effetive_area" calculations can be accumulated on the graph like so:
        "effective_area" : the current node is a 'source' of this value.
            this idea is similar for runoff volume, retention capacity, etc.
        "effective_area_direct" : this means that the value is 'sourced' from an
            *immediate* parent node.
        "effective_area_upstream" : this is the sum of the influence of the
            grandparents of the current node.
        "effective_area_cumul" : this is the sum of the "direct" and "upstream"
            values - basically the cumulative value 'towards' the current node.
            this does not include the contribution of the current node.
        "effective_area_total_cumul" : this is the total inflow + contribution from
            the current node. This *cannot* be used to accumulate, just to report.

    """

    ## -- Land Surface values

    # "_direct" is the sum of the value coming 'in' to this node. This does *not*
    # include the value sourced from the current node itself.
    data["eff_area_acres_direct"] = sum_node_attr(g, predecessors, "eff_area_acres")

    # "_upstream" is the sum of the value that flowed into this nodes parents *plus*
    # the sum of the value 'sourced' from the grandparent nodes.
    data["eff_area_acres_upstream"] = sum_node_attr(
        g, predecessors, "eff_area_acres_cumul"
    )

    # "_cumul" is the sum of the value that enters the current node from upstream nodes.
    # this does *not* include any contribution from the current node.
    data["eff_area_acres_cumul"] = (
        data["eff_area_acres_direct"] + data["eff_area_acres_upstream"]
    )

    # "_total_cumul" is the
    data["eff_area_acres_total_cumul"] = (
        data.get("eff_area_acres", 0.0) + data["eff_area_acres_cumul"]
    )

    # accumulate runoff
    data["runoff_volume_cuft_direct"] = sum_node_attr(
        g, predecessors, "runoff_volume_cuft"
    )

    data["runoff_volume_cuft_upstream"] = sum_node_attr(
        g, predecessors, "runoff_volume_cuft_discharged"
    )

    inflow_volume = data["runoff_volume_cuft_inflow"] = (
        data["runoff_volume_cuft_direct"] + data["runoff_volume_cuft_upstream"]
    )

    ## -- Treatment Facility values

    # accumulate upstream retention/treatment/detention

    data["runoff_volume_cuft_retained_upstream"] = sum_node_attr(
        g, predecessors, "runoff_volume_cuft_total_retained"
    )

    data["retention_volume_cuft_upstream"] = sum_node_attr(
        g, predecessors, "retention_volume_cuft_cumul"
    )

    data["retention_volume_cuft_cumul"] = (
        data.get("retention_volume_cuft", 0.0) + data["retention_volume_cuft_upstream"]
    )

    # accumulate design volume
    data["design_volume_cuft_direct"] = design_volume_cuft(
        data.get("design_storm_depth_inches", 0.0), data["eff_area_acres_direct"]
    )

    data["design_volume_cuft_upstream"] = sum_node_attr(
        g, predecessors, "design_volume_cuft_cumul"
    )

    # land surface nodes don't have a design depth, so we have to recalc this
    # if there is one set for this node, and it has to include the whole effective
    # area upstream. Patched 2022-03-14.
    data["design_volume_cuft_cumul"] = design_volume_cuft(
        data.get("design_storm_depth_inches", 0.0), data["eff_area_acres_cumul"]
    )

    # during storm detention doesn't exist for the 'current' node
    # yet, it's calculated later.
    data["during_storm_det_volume_cuft_upstream"] = sum_node_attr(
        g, predecessors, "during_storm_det_volume_cuft_cumul"
    )

    # vol reduction doesn't exist for the 'current' node yet,
    # it's calculated later.
    data["vol_reduction_cuft_upstream"] = sum_node_attr(
        g, predecessors, "vol_reduction_cuft_cumul"
    )

    # writeup step 2-a
    data["during_storm_design_vol_cuft_upstream"] = max(
        (
            data["design_volume_cuft_upstream"]
            - data["retention_volume_cuft_upstream"]
            # this is calculated if the node is a treatment facility
            - data["during_storm_det_volume_cuft_upstream"]
        ),
        0,
    )

    # writeup step 2-b
    data["during_storm_design_vol_cuft_cumul"] = (
        data["design_volume_cuft_direct"]
        + data["during_storm_design_vol_cuft_upstream"]
    )

    # track if is a nested node. This is used to change strategies
    # in the BMP wet weather volume capture solver
    _sum_upstream_vol = (
        data["retention_volume_cuft_upstream"]
        + data["during_storm_det_volume_cuft_upstream"]
    )

    data["_has_upstream_vol_storage"] = _sum_upstream_vol > 0

    ## -- accumulate wet weather pollutant loading
    for param in wet_weather_parameters:
        load_col = param["load_col"]
        conc_col = param["conc_col"]
        load_to_conc_factor = param["load_to_conc_factor"]

        data[load_col] = data.get(load_col, 0.0)

        # "_direct" is the sum of the value coming 'in' to this node. This does *not*
        # include the value sourced from the current node itself.
        data[f"{load_col}_direct"] = sum_node_attr(g, predecessors, load_col)

        # "_upstream" is the sum of the value that flowed into this nodes parents *plus*
        # the sum of the value 'sourced' from the grandparent nodes.
        data[f"{load_col}_upstream"] = sum_node_attr(
            g, predecessors, f"{load_col}_discharged"
        )

        # "_inflow" is the sum of the value that enters the current node from upstream nodes.
        # this does *not* include any contribution from the current node.
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


def compute_wet_weather_volume_discharge(data: dict[str, Any]) -> dict[str, Any]:
    """this function aggregates wet weather volume results to prepare them for summarization
    and to prepare the effects of the current node to influence the input to downstream nodes.

    This function is only called by `nereid.src.watershed.solve_watershed.solve_node`

    This function must always be called after `accumulate_wet_weather_loading`
    If the current node performs wet weather volume reduction this function must
    be alled after `.treatment_facility_capture.compute_volume_capture_with_nomograph` so that
    the performance is included in the result passed downstream.

    """
    inflow = data.get("runoff_volume_cuft_inflow", 0.0)

    retained_pct = data.get("retained_pct", 0.0)
    captured_pct = data.get("captured_pct", 0.0)
    treated_pct = data.get("treated_pct", 0.0)
    bypassed_pct = data["bypassed_pct"] = 100 - captured_pct

    data["runoff_volume_cuft_retained"] = inflow * retained_pct / 100
    data["runoff_volume_cuft_captured"] = inflow * captured_pct / 100
    data["runoff_volume_cuft_treated"] = inflow * treated_pct / 100
    data["runoff_volume_cuft_bypassed"] = inflow * bypassed_pct / 100

    vol_reduction_cuft = data.get("vol_reduction_cuft", 0.0)
    data["vol_reduction_cuft_cumul"] = (
        vol_reduction_cuft + data["vol_reduction_cuft_upstream"]
    )

    during_storm_det_volume_cuft = data.get("during_storm_det_volume_cuft", 0.0)
    data["during_storm_det_volume_cuft_cumul"] = (
        during_storm_det_volume_cuft + data["during_storm_det_volume_cuft_upstream"]
    )

    runoff_volume_cuft_retained = data.get("runoff_volume_cuft_retained", 0.0)

    # Use this value for reporting cumulative volume removed by the network, including current node.
    data["runoff_volume_cuft_total_retained"] = runoff_volume_cuft_retained + data.get(
        "runoff_volume_cuft_retained_upstream", 0.0
    )

    # this is the discharge that is read into the next downstream node as the 'upstream' value.
    data["runoff_volume_cuft_discharged"] = (
        data["runoff_volume_cuft_inflow"] - runoff_volume_cuft_retained
    )

    # Use this value for reporting the total outflow volume from a node. This accounts for
    # gains (if node is land surface) and losses (if node performs volume reduction)
    runoff_volume_cuft = data.get("runoff_volume_cuft", 0.0)
    data["runoff_volume_cuft_total_discharged"] = (
        runoff_volume_cuft + data["runoff_volume_cuft_discharged"]
    )

    return data


def compute_wet_weather_load_reduction(
    data: dict[str, Any],
    wet_weather_parameters: list[dict[str, Any]],
    wet_weather_facility_performance_map: dict[tuple[str, str], Callable],
) -> dict[str, Any]:
    """this function relies on the volume treated and volume retained to be set by
    other functions before computing the whole facility load reduction by considering
    influent->effluent concentration transformation, volume capture, and volume reduction
    to compute total load reduction for this node.

    This function is only called by `.solve_watershed.solve_node`

    This function must be called after all of the following have been called:
        `accumulate_upstream_loading`
        `compute_wet_weather_volume_discharge`

    Parameters
    ----------
    data : dict
        information about current node, including facility sizing information and inflow characteristics.
    wet_weather_parameters: list of dicts
        this contains information aabout each parameter, like long_name, short_name and
        conversion factor information. see the *land_surface_emc_tables in the config file.
        these dicts are pre-processed to cache some helpful unit conversions too prior to
        being passed to this function.
        Reference: `nereid.src.wq_parameters.init_wq_parameters`
    wet_weather_facility_performance_map : mapping
        this mapping uses a facility type and a pollutant as the keys to retrieve a function
        that returns effluent concentration as output when given influent concentration as input.
        Reference: `nereid.src.tmnt_performance.tmnt.effluent_conc`
        Reference: `nereid.src.tmnt_performance.tasks.effluent_function_map`

    """

    tmnt_facility_type = data.get("tmnt_performance_facility_type", r"¯\_(ツ)_/¯")
    vol_col = "runoff_volume_cuft"

    for param in wet_weather_parameters:
        conc_unit = param["concentration_unit"]
        poc_long = param["long_name"]

        load_col = param["load_col"]
        conc_col = param["conc_col"]

        load_to_conc_factor = param["load_to_conc_factor"]
        conc_to_load_factor = param["conc_to_load_factor"]

        inflow_load = data[f"{load_col}_inflow"]
        influent_conc = data[f"{conc_col}_influent"]

        compute_pollutant_load_reduction(
            data,
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

    return data


def check_node_results_close(data: dict[str, Any]) -> dict[str, Any]:
    """Run a few mass balance checks on the node."""
    check1 = safe_divide(
        (
            data["runoff_volume_cuft_inflow"]
            - data.get("runoff_volume_cuft_retained", 0.0)
            - data.get("runoff_volume_cuft_treated", 0.0)
            - data.get("runoff_volume_cuft_bypassed", data["runoff_volume_cuft_inflow"])
        ),
        data["runoff_volume_cuft_inflow"],
    )

    if abs(check1) > 0.01:  # pragma: no cover
        data["node_errors"].append(
            f"inflow did not close within 1%. difference is: {check1:%}"
        )

    check2 = safe_divide(
        abs(
            data["runoff_volume_cuft_discharged"]
            - data.get("runoff_volume_cuft_treated", 0.0)
            - data.get("runoff_volume_cuft_bypassed", data["runoff_volume_cuft_inflow"])
        ),
        data["runoff_volume_cuft_discharged"],
    )

    if abs(check2) > 0.01:  # pragma: no cover
        data["node_errors"].append(
            f"discharge did not close within 1 %. difference is: {check2:%}"
        )

    return data
