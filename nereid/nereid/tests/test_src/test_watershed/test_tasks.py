from copy import deepcopy

import pytest
import numpy
import networkx as nx

from nereid.src.network.algorithms import get_subset
from nereid.src.network.utils import nxGraph_to_dict, graph_factory
from nereid.src.watershed.tasks import solve_watershed
from nereid.tests.utils import attrs_to_resubmit


@pytest.mark.parametrize("n_nodes", [13, 55, 77, 115])
def test_solve_watershed_land_surface_only(contexts, watershed_requests, n_nodes):

    pct_tmnt = 0
    watershed_request = watershed_requests[(n_nodes, pct_tmnt)]
    context = contexts["default"]
    response_dict = solve_watershed(
        watershed=watershed_request, treatment_pre_validated=False, context=context,
    )
    result = response_dict["results"]
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


@pytest.mark.parametrize("pct_tmnt", [0.3, 0.6, 0.8])
@pytest.mark.parametrize("n_nodes", [13, 55, 77, 115])
def test_solve_watershed_with_treatment(
    contexts, watershed_requests, n_nodes, pct_tmnt
):

    watershed_request = watershed_requests[(n_nodes, pct_tmnt)]
    context = contexts["default"]
    response_dict = solve_watershed(
        watershed=watershed_request, treatment_pre_validated=False, context=context,
    )

    result = response_dict["results"]
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


@pytest.mark.parametrize("pct_tmnt", [0, 0.3, 0.6, 0.8])
@pytest.mark.parametrize("n_nodes", [13, 55, 77, 115])
def test_stable_watershed_subgraph_solutions(
    contexts, watershed_requests, n_nodes, pct_tmnt
):

    watershed_request = watershed_requests[(n_nodes, pct_tmnt)]
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

    numpy.random.seed(42)
    for cyc in range(3):
        n_dirty_nodes = numpy.random.randint(2, len(g) - 1, size=4)
        for dirty_nodes in [
            numpy.random.choice(g.nodes(), size=size, replace=False)
            for size in n_dirty_nodes
        ]:

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

            for subg_result in subgraph_results:
                node = subg_result["node_id"]
                og_result = [n for n in results if n["node_id"] == node][0]
                subg_node_degree = subg.in_degree(node)
                for k, v in subg_result.items():
                    og = og_result[k]
                    if isinstance(v, str):
                        err_stmt = f"node: {node}; degree: {subg_node_degree}, attr: {k}, orig value: {og}; new value: {v}"
                        assert v == og, err_stmt
                    elif isinstance(v, (int, float)):
                        err_stmt = f"node: {node}; degree: {subg_node_degree}, attr: {k}, orig value: {og}; new value: {v}"
                        # allow floating point errors only
                        if og == 0:
                            assert v >= 0 and v < 1e-3, (type(og), type(v), err_stmt)
                        else:
                            assert (
                                abs(og - v) < 1e-3 or (abs(og - v) / og) < 1e-6
                            ), err_stmt
