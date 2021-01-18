from copy import deepcopy

import networkx as nx
import pytest

from nereid.src.network.algorithms import get_subset
from nereid.src.network.utils import graph_factory, nxGraph_to_dict
from nereid.src.watershed.tasks import solve_watershed
from nereid.src.watershed.utils import attrs_to_resubmit
from nereid.tests.utils import check_subgraph_response_equal


@pytest.mark.parametrize("n_nodes", [50, 100])
def test_solve_watershed_land_surface_only(contexts, watershed_requests, n_nodes):

    pct_tmnt = 0
    watershed_request = deepcopy(watershed_requests[(n_nodes, pct_tmnt)])
    context = contexts["default"]
    response_dict = solve_watershed(
        watershed=watershed_request, treatment_pre_validated=False, context=context,
    )
    result = response_dict["results"] + response_dict["leaf_results"]
    outfall_results = [n for n in result if n["node_id"] == "0"][0]
    assert len(result) == len(watershed_request["graph"]["nodes"])
    assert all([len(n["node_errors"]) == 0 for n in result])

    for single, total in [
        ("eff_area_acres", "eff_area_acres_total_cumul"),
        ("runoff_volume_cuft", "runoff_volume_cuft_total_discharged"),
        ("TSS_load_lbs", "TSS_load_lbs_total_discharged"),
        (
            "summer_dry_weather_flow_cuft",
            "summer_dry_weather_flow_cuft_total_discharged",
        ),
        ("summer_dwTSS_load_lbs", "summer_dwTSS_load_lbs_total_discharged"),
        (
            "winter_dry_weather_flow_cuft",
            "winter_dry_weather_flow_cuft_total_discharged",
        ),
        ("winter_dwTSS_load_lbs", "winter_dwTSS_load_lbs_total_discharged"),
    ]:

        outfall_total = outfall_results[total]
        assert outfall_total > 1e-3
        sum_individual = sum([n.get(single, 0.0) for n in result])

        # allow floating point errors only
        assert abs(outfall_total - sum_individual) / outfall_total < 1e-15


@pytest.mark.parametrize("pct_tmnt", [0.3, 0.6,])
@pytest.mark.parametrize("n_nodes", [50, 100])
def test_solve_watershed_with_treatment(
    contexts, watershed_requests, n_nodes, pct_tmnt
):

    watershed_request = deepcopy(watershed_requests[(n_nodes, pct_tmnt)])
    context = contexts["default"]
    response_dict = solve_watershed(
        watershed=watershed_request, treatment_pre_validated=False, context=context,
    )

    result = response_dict["results"] + response_dict["leaf_results"]
    outfall_results = [n for n in result if n["node_id"] == "0"][0]
    assert len(result) == len(watershed_request["graph"]["nodes"])
    assert all([len(n["node_errors"]) == 0 for n in result])

    sum_ret = sum([n.get("runoff_volume_cuft_retained", 0.0) for n in result])
    sum_inflow = sum([n.get("runoff_volume_cuft", 0.0) for n in result])
    outflow = outfall_results["runoff_volume_cuft_total_discharged"]

    assert abs(sum_inflow - sum_ret - outflow) / sum_inflow < 1e-15

    scalers = [
        ("summer_dwTSS_load_lbs_removed", "summer_dwTSS_load_lbs_total_removed"),
        ("runoff_volume_cuft_retained", "runoff_volume_cuft_total_retained"),
        (
            "summer_dry_weather_flow_cuft_retained",
            "summer_dry_weather_flow_cuft_total_retained",
        ),
        (
            "summer_dry_weather_flow_cuft_psecond_retained",
            "summer_dry_weather_flow_cuft_psecond_total_retained",
        ),
    ]

    for s, t in scalers:
        outfall_total = outfall_results[t]
        sum_individual = sum([n.get(s, 0.0) for n in result])

        # assert that these add up
        assert abs(sum_individual - outfall_total) < 1e-6, (s, t)

    for load_type in [
        "runoff_volume_cuft_total_retained",
        "TSS_load_lbs_total_removed",
        "summer_dry_weather_flow_cuft_total_retained",
        "summer_dwTSS_load_lbs_total_removed",
        "winter_dry_weather_flow_cuft_total_retained",
        "winter_dwTSS_load_lbs_total_removed",
    ]:
        # check that treatment happened
        assert outfall_results[load_type] > 0


def test_stable_watershed_stable_subgraph_solutions(
    contexts, watershed_requests, watershed_test_case
):

    n_nodes, pct_tmnt, dirty_nodes = watershed_test_case
    watershed_request = deepcopy(watershed_requests[(n_nodes, pct_tmnt)])
    context = contexts["default"]
    response_dict = solve_watershed(
        watershed=watershed_request, treatment_pre_validated=False, context=context,
    )
    results = response_dict["results"]

    reqd_min_attrs = attrs_to_resubmit(results)
    previous_results = {
        "previous_results": [
            {k: dct[k] for k in dct.keys() if k in reqd_min_attrs + ["node_id"]}
            for dct in results
        ]
    }

    g = graph_factory(watershed_request["graph"])

    # this subgraph is empty, has no data.
    subg = nx.DiGraph(g.subgraph(get_subset(g, nodes=dirty_nodes)).edges)
    subgraph = {"graph": nxGraph_to_dict(subg)}

    new_request = deepcopy(watershed_request)
    new_request.update(subgraph)
    new_request.update(previous_results)

    subgraph_response_dict = solve_watershed(
        watershed=new_request, treatment_pre_validated=False, context=context,
    )
    subgraph_results = subgraph_response_dict["results"]

    check_subgraph_response_equal(subgraph_results, results)


@pytest.mark.parametrize(
    "facility_type, eliminates_wet_volume, treats_wet_volume, captures_dwf",
    [
        ("no_treatment", False, False, False),
        ("dry_extended_detention", True, True, True),
        ("infiltration", True, False, True),
        ("bioretention", True, True, True),
        ("biofiltration", False, True, True),
        ("wet_detention", False, True, True),
        ("sand_filter", False, True, True),
        ("swale", True, True, True),
        ("hydrodynamic_separator", False, True, True),
        ("dry_well", True, False, True),
        ("cistern", True, False, True),
        ("dry_weather_diversion", False, False, True),
        ("dry_weather_treatment", False, False, True),
        ("low_flow_facility", False, False, True),
    ],
)
def test_treatment_facility_waterbalance(
    contexts,
    simple_3_node_watershed,
    treatment_facilities_dict,
    facility_type,
    eliminates_wet_volume,
    treats_wet_volume,
    captures_dwf,
):

    context = contexts["default"]
    facility = treatment_facilities_dict[facility_type]
    facility["node_id"] = "1"
    watershed_request = simple_3_node_watershed

    watershed_request["treatment_facilities"] = [facility]

    response_dict = solve_watershed(
        watershed=watershed_request, treatment_pre_validated=False, context=context,
    )

    results = response_dict["results"]

    treatment_results = [res for res in results if res.get("node_id") == "1"][0]

    ret_pct = treatment_results.get("retained_pct") or 0
    tmnt_pct = treatment_results.get("treated_pct") or 0
    dwf_captured = (
        treatment_results.get("summer_dry_weather_flow_cuft_captured_pct") or 0
    ) + (treatment_results.get("winter_dry_weather_flow_cuft_captured_pct") or 0)

    assert eliminates_wet_volume == (ret_pct > 1), treatment_results
    assert treats_wet_volume == (tmnt_pct > 1), treatment_results
    assert captures_dwf == (dwf_captured > 1), treatment_results

    return
