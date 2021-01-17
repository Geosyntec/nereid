from typing import Any, Callable, Dict, List, Mapping

from nereid.core.utils import safe_divide


def compute_volume_capture_with_nomograph(
    data: Dict[str, Any], nomograph_map: Mapping[str, Callable],
) -> Dict[str, Any]:
    """Compute volume captured by a treatment facility if it treats wet weather flow
    via either volume or flow-based calculation strategies.

    This function is only called by `.solve_watershed.solve_node`
    This function must be called after all of the following have been called:
        `.dry_weather_loading.accumulate_dry_weather_loading`
        `.wet_weather_loading.accumulate_wet_weather_loading`

    Parameters
    ----------
    data : dict
        information about the node, inclding treatment facility sizing and inflow
        characteristics
    nomograph_map : mapping
        this mapping uses the nomograph data filepath as the key to return a 2d nomograph
        interpolator function. this is not 1:1 with facility types because some facility types,
        like swales, require us to traverse both a flow-based nomograph _and_ a volume based
        nomograph in order to solve for the volume capture, e.g., swales. The necessary information
        for each facility, e.g., which nomograph files to refer to when needed, is joined to the facility
        information from the config.yml::project_reference_data::met_table
        Reference: `nereid.src.nomograph.nomo.load_nomograph_mapping`

    """
    data["_nomograph_solution_status"] = "none"
    node_type = data.get("node_type", "none")

    vol_nomo_file = data.get("volume_nomograph", "")
    volume_nomo = nomograph_map.get(vol_nomo_file)
    if volume_nomo is None:  # pragma: no cover
        volume_nomo = lambda size=None, ddt=None, performance=None: 0.0

    flow_nomo_file = data.get("flow_nomograph", "")
    flow_nomo = nomograph_map.get(flow_nomo_file)
    if flow_nomo is None:  # pragma: no cover
        flow_nomo = lambda intensity=None, tc=None, performance=None: 0.0

    data["retention_volume_cuft"] = data.get("retention_volume_cuft", 0.0)
    data["retention_ddt_hr"] = data.get("retention_ddt_hr", 0.0)
    data["treatment_volume_cuft"] = data.get("treatment_volume_cuft", 0.0)
    data["treatment_ddt_hr"] = data.get("treatment_ddt_hr", 0.0)

    if "volume_based_facility" in node_type:

        sum_upstream_vol = (
            data["retention_volume_cuft_upstream"]
            + data["during_storm_det_volume_cuft_upstream"]
        )

        if sum_upstream_vol == 0:
            data = compute_volume_based_standalone_facility(data, volume_nomo)

        else:
            data = compute_volume_based_nested_facility(data, volume_nomo)

        # writeup step 2, equation 4. this value is stored, but is
        # not used until there is a next-downstream facility.
        data["during_storm_det_volume_cuft"] = detention_vol(
            tmnt_ddt=data["treatment_ddt_hr"],
            cumul_within_storm_vol=data["during_storm_design_vol_cuft_cumul"],
            ret_vol=data["retention_volume_cuft"],
            tmnt_vol=data["treatment_volume_cuft"],
        )

    elif "flow_based_facility" in node_type:
        data = compute_flow_based_facility(data, flow_nomo, volume_nomo)

    else:  # pragma: no cover
        # this should be impossible to reach since this function is called within the
        # solve_watershed_loading function
        msg = f"ERROR: solution strategy does not exist for node type {node_type}"
        data["node_errors"].append(msg)
        return data

    # writeup step 3-a. This volume reduction is calculated, but is
    # not used until the next-downstream facility.
    # NOTE: This doesn't make sense yet if the retention volume > design vol direct.
    # suggest using the design vol cumul? consider a flow-based facility draining to a volume based one,
    # there is no direct runoff in this case.
    data["vol_reduction_cuft"] = max(
        0,
        (data["retained_pct"] / 100)
        # todo: this should maybe not subtract the retention vol?
        * (data["design_volume_cuft_direct"] - data["retention_volume_cuft"]),
    )

    return data


def compute_volume_based_standalone_facility(
    data: Dict[str, Any], volume_nomo: Callable
) -> Dict[str, Any]:
    """Calculate treatment and retention volume for a standalone volume-based
    treatment facility. Standalone means that there are not volume-based facilities
    upstream of the current facility that are performing volume reductions.

    This function is only called by `compute_volume_capture_with_nomograph`, and only
    if the facility node_type contains 'volume_based_facility' and if there is
    no upstream retention due to other treatment facilities. If there are upstream
    facilities, we use the nested facility function: `compute_volume_based_nested_facility`.

    Parameters
    ----------
    data : dict
        information about this node. this will include facility size details and information about
        the incoming flow to be treated.
    volume_nomo : thinly wrapped 2D CloughTocher Interpolator
        Reference: `nereid.src.nomograph.nomo`
    """
    ret_vol_cuft = data["retention_volume_cuft"]
    trt_vol_cuft = data["treatment_volume_cuft"]

    ret_ddt_hr = data.get("retention_ddt_hr", 0.0)
    trt_ddt_hr = data.get("treatment_ddt_hr", 0.0)

    design_volume = data["design_volume_cuft_cumul"]

    if ret_vol_cuft > 0 and trt_vol_cuft > 0:

        q_ret = ret_vol_cuft / (ret_ddt_hr * 3600)
        q_trt = trt_vol_cuft / (trt_ddt_hr * 3600)
        q_tot = q_ret + q_trt

        ret_mvol = (trt_vol_cuft * (q_ret / q_tot)) + ret_vol_cuft
        trt_mvol = trt_vol_cuft + ret_vol_cuft - ret_mvol

        ret_mddt = ret_mvol / (q_ret * 3600)
        trt_mddt = trt_mvol / (q_trt * 3600)

    else:
        ret_mvol = ret_vol_cuft
        trt_mvol = trt_vol_cuft
        ret_mddt = ret_ddt_hr
        trt_mddt = trt_ddt_hr

    retention_vol_frac = safe_divide(ret_mvol, design_volume)
    treatment_vol_frac = safe_divide(trt_mvol, design_volume)

    input_compartments = [
        dict(volume=retention_vol_frac, ddt=ret_mddt),  # retention compartment is [0]
        dict(volume=treatment_vol_frac, ddt=trt_mddt),  # treatment compartment is [1]
    ]

    compartments = solve_volume_based_compartments(input_compartments, volume_nomo)

    retained_percent = min(100, 100 * compartments[0]["performance"])
    captured_percent = max(retained_percent, 100 * compartments[1]["performance"])
    treated_percent = captured_percent - retained_percent

    data["retained_pct"] = retained_percent
    data["captured_pct"] = captured_percent
    data["treated_pct"] = treated_percent
    data["_nomograph_solution_status"] = "successful; volume based; standalone"

    return data


def solve_volume_based_compartments(
    compartments: List[Dict[str, float]], volume_nomo: Callable
) -> List[Dict[str, float]]:
    """Traverse a series of volume-based nomographs from the bottom compartment (retention)
    to the top compartment (treatment). This function accumulates the x-offset from
    each nomograph traversal so that subsequent traversals account for previous compartments.

    This function is only called by the `compute_volume_based_standalone_facility` function.

    Parameters
    ----------
    compartments : list of dicts
        These are the ddt and volume of each compartment to be used during the nomograph
        traversals.
    volume_nomo : thinly wrapped 2D CloughTocher Interpolator
        Reference: `nereid.src.nomograph.nomo`
    """

    prev_performance = 0.0
    for c in compartments:
        size = c["volume"]
        ddt = c["ddt"] if size > 1e-6 else 0.0

        xoffset = 0.0
        if prev_performance > 0:
            xoffset = volume_nomo(performance=prev_performance, ddt=ddt)

        performance = float(volume_nomo(size=size + xoffset, ddt=ddt))
        c["performance"] = performance
        c["xoffset"] = xoffset

        prev_performance = performance

    return compartments


def compute_volume_based_nested_facility(
    data: Dict[str, Any], volume_nomo: Callable
) -> Dict[str, Any]:
    """Process a volume based treatment facility whose performance
    is influenced by upstream volume based facilities.

    This function is only called by `compute_volume_capture_with_nomograph`, and only
    if the current node_type contains 'volume_based_facility' and only if there is also
    upstream retention or detention occurring in the system.

    Parameters
    ----------
    data : dict
        information about the current facility and the incoming flow.

    volume_nomo : thinly wrapped 2D CloughTocher Interpolator
        Reference: `nereid.src.nomograph.nomo`
    """

    # compute retention
    # writeup step 3-b
    data["us_vol_reduction_pct"] = 100 * min(
        1,
        safe_divide(
            data["vol_reduction_cuft_upstream"],
            data["during_storm_design_vol_cuft_cumul"],
        ),
    )

    if data["retention_volume_cuft"] > 0:

        # writeup step 4
        data["us_ret_vol_xoff"] = float(
            volume_nomo(
                performance=data["us_vol_reduction_pct"] / 100,
                ddt=data["retention_ddt_hr"],
            )
        )

        # writeup step 5
        data["retention_vol_frac"] = safe_divide(
            data["retention_volume_cuft"], data["design_volume_cuft_cumul"]
        )

        # writeup step 6
        data["ret_vol_xmax"] = data["retention_vol_frac"] + data["us_ret_vol_xoff"]

        data["raw_retained_pct"] = 100 * float(
            volume_nomo(size=data["ret_vol_xmax"], ddt=data["retention_ddt_hr"])
        )

        # compute treatment
        # writeup step 7
        data["trt_vol_xoff"] = float(
            volume_nomo(
                performance=data["raw_retained_pct"] / 100, ddt=data["treatment_ddt_hr"]
            )
        )

    else:
        data["raw_retained_pct"] = 0
        data["trt_vol_xoff"] = 0

    # writeup step 8
    data["treatment_vol_frac"] = safe_divide(
        data["treatment_volume_cuft"], data["design_volume_cuft_cumul"]
    )

    # writeup step 9; raw_captured_pct aka 'Cumul Capture Eff'
    data["trt_vol_xmax"] = data["treatment_vol_frac"] + data["trt_vol_xoff"]
    data["raw_captured_pct"] = 100 * float(
        volume_nomo(size=data["trt_vol_xmax"], ddt=data["treatment_ddt_hr"])
    )

    # writeup step 10
    # adjust capture efficiency for upstream retention
    # NOTE: what if the upstream vol reduction is > the raw captured pct???
    data["adjusted_captured_pct"] = max(
        0,
        100
        * (
            max(data["raw_captured_pct"] - data["us_vol_reduction_pct"], 0)
            * safe_divide(1, (100 - data["us_vol_reduction_pct"]))
        ),
    )

    # writeup step 11
    # final capture efficiency
    captured_pct = 100 * safe_divide(
        (
            data["adjusted_captured_pct"]
            / 100
            * data["during_storm_design_vol_cuft_cumul"]
            + data["during_storm_det_volume_cuft_upstream"]
        ),
        (
            data["during_storm_design_vol_cuft_cumul"]
            + data["during_storm_det_volume_cuft_upstream"]
        ),
    )

    # writeup step 12
    # adjust final retention
    retained_pct = data["raw_retained_pct"]
    if data["retention_volume_cuft"] > 0:
        retained_pct = data["retained_pct"] = max(
            data["raw_retained_pct"] - data["us_vol_reduction_pct"], 0
        )
    retained_pct = min(retained_pct, captured_pct)
    treated_pct = captured_pct - retained_pct

    data["captured_pct"] = captured_pct
    data["retained_pct"] = retained_pct
    data["treated_pct"] = treated_pct
    data["_nomograph_solution_status"] = "successful; volume based; nested"

    return data


def detention_vol(
    tmnt_ddt: float, cumul_within_storm_vol: float, ret_vol: float, tmnt_vol: float
) -> float:
    """This is a helper function for calculating the volume that is detained (delayed)
    by a treatment facility.

    Parameters
    ----------
    trt_ddt : drawdown time in hours for treatment compartment
    cumul_within_storm_vol : cumul_within_storm_vol as calculated per step 2 equation 3 of writeup
    ret_vol : volume in cubic feet of the retention compartment
    trt_vol : volume in cubic feet of the treatment compartment

    Notes:
        this function will return zero if trt_ddt is zero
        `safe_divide` returns 0 if denominator is 0, rather than nan or infinity
    """
    STORM_DURATION = 24  # hours
    factor = 1 - min(safe_divide(STORM_DURATION, tmnt_ddt), 1)
    vol = min(max(cumul_within_storm_vol - ret_vol, 0), tmnt_vol)
    return factor * vol


def compute_flow_based_facility(
    data: Dict[str, Any], flow_nomo: Callable, volume_nomo: Callable
) -> Dict[str, Any]:
    """Solves volume balance for flow based treatment. these facilities *can* perform both
    treatment via treatment rate nomographs to reduce the effluent concentration and/or
    volume reduction via volume capture nomographs to retain volume. an example of a
    facility that does both is an unlined swale with a treatment rate in cfs, but
    also a (small) facility volume and infiltration lss-rate.

    This function is only called by `compute_volume_capture_with_nomograph` and only if
    the node-type contains 'flow_based_facility'.

    Parameters
    ----------
    data : dict
        all the current node's information. this will be treatment facilily size
        information and characteristics of incoming upstream flow.
    *_nomo : thinly wrapped 2D CloughTocher Interpolators
        Reference: `nereid.src.nomograph.nomo`

    """

    tc = data.get("tributary_area_tc_min")
    if tc is None or tc < 5:
        tc = 5
        msg = f"overriding tributary_area_tc_min from '{tc}' to 5 minutes."
        data["node_warnings"].append(msg)

    captured_fraction = float(
        flow_nomo(intensity=data.get("design_intensity_inhr", 0.0), tc=tc) or 0.0
    )

    size_fraction = safe_divide(
        data.get("retention_volume_cuft", 0.0), data["design_volume_cuft_cumul"]
    )
    ret_ddt_hr = data.get("retention_ddt_hr", 0.0)

    retained_fraction = captured_fraction * float(
        volume_nomo(size=size_fraction, ddt=ret_ddt_hr) or 0.0
    )

    treated_fraction = (
        captured_fraction - retained_fraction
    )  # TODO make this 0.0 if < 1e-6

    data["retained_pct"] = retained_fraction * 100
    data["captured_pct"] = captured_fraction * 100
    data["treated_pct"] = treated_fraction * 100
    data["_nomograph_solution_status"] = "successful; flow based"

    return data
