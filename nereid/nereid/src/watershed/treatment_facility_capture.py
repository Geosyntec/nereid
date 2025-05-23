from typing import Any, Callable, TypedDict, cast

import numpy

from nereid.core.utils import safe_divide
from nereid.src.watershed.design_functions import design_intensity_inhr


class Compartment(TypedDict):
    volume: float
    ddt: float
    performance: float
    xoffset: float
    error: str


def compute_volume_capture_with_nomograph(
    data: dict[str, Any],
    nomograph_map: dict[str, Callable],
) -> dict[str, Any]:
    """Compute volume captured by a treatment facility if it treats wet weather flow
    via either volume or flow-based calculation strategies.

    This function is only called by `.solve_watershed.solve_node`
    This function must be called after all of the following have been called:
        `.dry_weather_loading.accumulate_dry_weather_loading`
        `.wet_weather_loading.accumulate_wet_weather_loading`

    Parameters
    ----------
    data : dict
        information about the node, including treatment facility sizing and inflow
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

    def default_volume_nomo(size=None, ddt=None, performance=None):
        return 0.0  # pragma: no cover

    volume_nomo = nomograph_map.get(vol_nomo_file, default_volume_nomo)

    flow_nomo_file = data.get("flow_nomograph", "")

    def default_flow_nomo(intensity=None, tc=None, performance=None):
        return 0.0  # pragma: no cover

    flow_nomo = nomograph_map.get(flow_nomo_file, default_flow_nomo)

    peak_nomo_file = data.get("peak_nomograph", "")

    def default_peak_nomo(size=None, ddt=None, performance=None):
        return 0.0  # pragma: no cover

    peak_nomo = nomograph_map.get(peak_nomo_file, default_peak_nomo)

    data["retention_volume_cuft"] = data.get("retention_volume_cuft", 0.0)
    data["retention_ddt_hr"] = data.get("retention_ddt_hr", 0.0)
    data["treatment_volume_cuft"] = data.get("treatment_volume_cuft", 0.0)
    data["treatment_ddt_hr"] = data.get("treatment_ddt_hr", 0.0)

    if all(v in node_type for v in ["volume_based", "facility"]):
        if data["_has_upstream_vol_storage"]:
            data = compute_volume_based_nested_facility(data, volume_nomo)

        else:
            data = compute_volume_based_standalone_facility(data, volume_nomo)

        # writeup step 2, equation 4. this value is stored, but is
        # not used until there is a next-downstream facility.
        data["during_storm_det_volume_cuft"] = detention_vol(
            tmnt_ddt=data["treatment_ddt_hr"],
            cumul_within_storm_vol=data["during_storm_design_vol_cuft_cumul"],
            ret_vol=data["retention_volume_cuft"],
            tmnt_vol=data["treatment_volume_cuft"],
        )

        if peak_nomo_file:
            data = compute_peak_flow_reduction(data, peak_nomo)

    elif "flow_based_facility" in node_type:
        data = compute_flow_based_facility(data, flow_nomo, volume_nomo)

    elif "dry_well_facility" in node_type:
        data = compute_dry_well_facility(data, flow_nomo, volume_nomo)

    else:  # pragma: no cover
        # this should be impossible to reach since this function is called within the
        # solve_watershed_loading function
        msg = f"ERROR: solution strategy does not exist for node type {node_type}"
        data["node_errors"].append(msg)
        return data

    # writeup step 3-a. This volume reduction is calculated, but is
    # not used until the next-downstream facility.
    data["vol_reduction_cuft"] = max(
        0,
        (data["retained_pct"] / 100) * (data["design_volume_cuft_cumul"]),
    )

    return data


def compute_volume_based_standalone_facility(
    data: dict[str, Any],
    volume_nomo: Callable,
) -> dict[str, Any]:
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
        q_ret = safe_divide(ret_vol_cuft, (ret_ddt_hr * 3600))
        q_trt = safe_divide(trt_vol_cuft, (trt_ddt_hr * 3600))
        q_tot = q_ret + q_trt

        ret_mvol = (trt_vol_cuft * safe_divide(q_ret, q_tot)) + ret_vol_cuft
        trt_mvol = trt_vol_cuft + ret_vol_cuft - ret_mvol

        ret_mddt = safe_divide(ret_mvol, (q_ret * 3600))
        trt_mddt = safe_divide(trt_mvol, (q_trt * 3600))

    else:
        ret_mvol = ret_vol_cuft
        trt_mvol = trt_vol_cuft
        ret_mddt = ret_ddt_hr
        trt_mddt = trt_ddt_hr

    data["_ret_mvol"] = ret_mvol
    data["_trt_mvol"] = trt_mvol
    data["_ret_mddt"] = ret_mddt
    data["_trt_mddt"] = trt_mddt

    retention_vol_frac = safe_divide(ret_mvol, design_volume)
    treatment_vol_frac = safe_divide(trt_mvol, design_volume)

    input_compartments = [
        cast(
            Compartment,
            {
                "volume": retention_vol_frac,
                "ddt": float(ret_mddt),
            },
        ),  # retention compartment is [0]
        cast(
            Compartment,
            {
                "volume": treatment_vol_frac,
                "ddt": float(trt_mddt),
            },
        ),  # treatment compartment is [1]
    ]

    compartments = solve_volume_based_compartments(input_compartments, volume_nomo)
    data["compartments"] = compartments

    retained_percent = min(100, 100 * compartments[0]["performance"])
    # min retention pct is meant to estimate incidental retention performance of
    # vegetated tmnt-only BMPs.
    minimum_retention_pct_override = data.get("minimum_retention_pct_override", 0.0)
    retained_percent = max(retained_percent, minimum_retention_pct_override)
    captured_percent = max(retained_percent, 100 * compartments[1]["performance"])
    treated_percent = captured_percent - retained_percent

    data["retained_pct"] = retained_percent
    data["captured_pct"] = captured_percent
    data["treated_pct"] = treated_percent
    data["_nomograph_solution_status"] = "successful; volume based; standalone"
    for i, c in enumerate(compartments):
        if c["error"]:  # pragma: no cover
            data["_nomograph_solution_status"] += f"; c{i}[{c['error']}]"
            data["node_errors"].append(f"c{i}[{c['error']}]")
    return data


def solve_volume_based_compartments(
    compartments: list[Compartment],
    volume_nomo: Callable,
) -> list[Compartment]:
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
        c["error"] = ""
        size = c["volume"]
        ddt = c["ddt"] if size > 1e-6 else 0.0

        xoffset = 0.0
        if (prev_performance > 0) and (ddt > 0):
            xoffset = volume_nomo(performance=prev_performance, ddt=ddt)

        performance = (
            volume_nomo(size=size + xoffset, ddt=ddt)
            if (size + ddt) > 0
            else prev_performance
        )
        if numpy.isnan(performance):  # pragma: no cover
            c["error"] = "size and ddt are out of bounds."
        c["performance"] = prev_performance = numpy.nanmax([0.0, performance])
        c["xoffset"] = xoffset

    return compartments


def compute_volume_based_nested_facility(
    data: dict[str, Any],
    volume_nomo: Callable,
) -> dict[str, Any]:
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

        data["raw_retained_pct"] = min(
            100,
            100
            * float(
                volume_nomo(size=data["ret_vol_xmax"], ddt=data["retention_ddt_hr"])
            ),
        )

        # compute treatment
        # writeup step 7
        data["trt_vol_xoff"] = (
            float(
                volume_nomo(
                    performance=data["raw_retained_pct"] / 100,
                    ddt=data["treatment_ddt_hr"],
                )
            )
            if data.get("treatment_volume_cuft")
            else 0
        )

    else:
        data["raw_retained_pct"] = 0
        data["trt_vol_xoff"] = float(
            volume_nomo(
                performance=data["us_vol_reduction_pct"] / 100,
                ddt=data["treatment_ddt_hr"],
            )
        )

    # writeup step 8
    data["treatment_vol_frac"] = safe_divide(
        data["treatment_volume_cuft"], data["design_volume_cuft_cumul"]
    )

    # writeup step 9; raw_captured_pct aka 'Cumul Capture Eff'
    data["trt_vol_xmax"] = data["treatment_vol_frac"] + data["trt_vol_xoff"]
    data["raw_captured_pct"] = (
        min(
            100,
            100
            * float(
                volume_nomo(size=data["trt_vol_xmax"], ddt=data["treatment_ddt_hr"])
            ),
        )
        if data.get("trt_vol_xmax")
        else data["raw_retained_pct"]
    )

    # writeup step 10
    # adjust capture efficiency for upstream retention
    # NOTE: what if the upstream vol reduction is > the raw captured pct???
    data["adjusted_captured_pct"] = min(
        100,
        max(
            0,
            100
            * (
                max(data["raw_captured_pct"] - data["us_vol_reduction_pct"], 0)
                * safe_divide(1, (100 - data["us_vol_reduction_pct"]))
            ),
        ),
    )

    # writeup step 11
    # final capture efficiency
    captured_pct = min(
        100,
        100
        * safe_divide(
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
        ),
    )

    # writeup step 12
    # adjust final retention
    retained_pct = data["adjusted_retained_pct"] = min(
        100,
        max(
            0,
            100
            * (
                max(data["raw_retained_pct"] - data["us_vol_reduction_pct"], 0)
                * safe_divide(1, (100 - data["us_vol_reduction_pct"]))
            ),
        ),
    )

    retained_pct = min(retained_pct, captured_pct, 100)

    captured_pct = (
        captured_pct if data.get("treatment_volume_cuft", 0.0) > 0 else retained_pct
    )

    treated_pct = captured_pct - retained_pct

    data["captured_pct"] = captured_pct
    data["retained_pct"] = retained_pct
    data["treated_pct"] = treated_pct
    data["_nomograph_solution_status"] = "successful; volume based; nested"

    return data


def detention_vol(
    tmnt_ddt: float,
    cumul_within_storm_vol: float,
    ret_vol: float,
    tmnt_vol: float,
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
    data: dict[str, Any],
    flow_nomo: Callable,
    volume_nomo: Callable,
) -> dict[str, Any]:
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
        all the current node's information. this will be treatment facility size
        information and characteristics of incoming upstream flow.
    *_nomo : thinly wrapped 2D CloughTocher Interpolators
        Reference: `nereid.src.nomograph.nomo`

    """

    tc = data.get("tributary_area_tc_min")
    if tc is None or tc < 5:
        tc = 5
        msg = f"overriding tributary_area_tc_min from '{tc}' to 5 minutes."
        data["node_warnings"].append(msg)

    intensity = data["design_intensity_inhr"] = design_intensity_inhr(
        data.get("treatment_rate_cfs", 0.0), data["eff_area_acres_cumul"]
    )

    captured_fraction = float(flow_nomo(intensity=intensity, tc=tc) or 0.0)
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


def compute_dry_well_facility(
    data: dict[str, Any],
    flow_nomo: Callable,
    volume_nomo: Callable,
) -> dict[str, Any]:
    """best of flow-based and volume based nomographs for bmp volume and treatment rate.

    the fate of all of the treatment for a drywell is _always_ retention.

    Parameters
    ----------
    data : dict
        all the current node's information. this will be treatment facility size
        information and characteristics of incoming upstream flow.
    *_nomo : thinly wrapped 2D CloughTocher Interpolators
        Reference: `nereid.src.nomograph.nomo`

    """

    tc = data.get("tributary_area_tc_min")
    if tc is None or tc < 5:
        tc = 5
        msg = f"overriding tributary_area_tc_min from '{tc}' to 5 minutes."
        data["node_warnings"].append(msg)

    # check flow nomo
    intensity = data["design_intensity_inhr"] = design_intensity_inhr(
        data.get("retention_rate_cfs", 0.0), data["eff_area_acres_cumul"]
    )

    flow_based_captured_fraction = float(flow_nomo(intensity=intensity, tc=tc) or 0.0)

    # check volume nomo
    size_fraction = safe_divide(
        data.get("retention_volume_cuft", 0.0), data["design_volume_cuft_cumul"]
    )
    ret_ddt_hr = data.get("retention_ddt_hr", 0.0)

    volume_based_captured_fraction = float(
        volume_nomo(size=size_fraction, ddt=ret_ddt_hr) or 0.0
    )

    # check which is best capture
    solution_type = "flow based"
    if volume_based_captured_fraction > flow_based_captured_fraction:
        solution_type = "volume based"

    captured_pct = (
        max(flow_based_captured_fraction, volume_based_captured_fraction) * 100
    )

    # for dry wells, all capture is retention.
    data["retained_pct"] = captured_pct
    data["captured_pct"] = captured_pct
    data["treated_pct"] = 0.0
    data["_nomograph_solution_status"] = f"successful; dry well {solution_type}"

    return data


def compute_peak_flow_reduction(
    data: dict[str, Any],
    peak_nomo: Callable,
) -> dict[str, Any]:
    ret_vol_cuft = data["retention_volume_cuft"]
    trt_vol_cuft = data["treatment_volume_cuft"]

    ret_ddt_hr = data.get("retention_ddt_hr", 0.0)
    trt_ddt_hr = data.get("treatment_ddt_hr", 0.0)

    design_volume = data["design_volume_cuft_cumul"]

    retention_vol_frac = safe_divide(ret_vol_cuft, design_volume)
    treatment_vol_frac = safe_divide(trt_vol_cuft, design_volume)

    data["peak_flow_mitigated_pct"] = 0.0

    size = treatment_vol_frac
    ddt = trt_ddt_hr
    if trt_vol_cuft <= 1e-2:
        size = retention_vol_frac
        ddt = ret_ddt_hr
    if size <= 1e-2:
        return data  # Early exit. No peak mitigation

    performance_fraction = float(peak_nomo(size=size, ddt=ddt))

    data["peak_flow_mitigated_pct"] = performance_fraction * 100

    return data
