from copy import deepcopy

import networkx as nx
import pandas
import pytest

from nereid.src.network.utils import graph_factory, nxGraph_to_dict
from nereid.src.tasks import land_surface_loading, solution_sequence, solve_watershed
from nereid.tests.utils import check_results_dataframes


@pytest.mark.parametrize("pct_tmnt", [0.0, 0.6])
@pytest.mark.parametrize("n_nodes", [100])
def test_watershed_solve_sequence(contexts, watershed_requests, n_nodes, pct_tmnt):
    watershed_request = deepcopy(watershed_requests[n_nodes, pct_tmnt])
    context = contexts["default"]

    g = graph_factory(watershed_request["graph"])

    initial_results = land_surface_loading(watershed_request, False, context=context)[
        "summary"
    ]
    db = pandas.DataFrame(initial_results).set_index("node_id")

    _node_list = solution_sequence(watershed_request["graph"], 16)["solution_sequence"][
        "parallel"
    ][0]["series"]
    node_list = [[n["id"] for n in nl["nodes"]] for nl in _node_list]  # type: ignore

    presults = []  # no initial results, obvs
    for branch_nodes in node_list:
        # this subgraph is empty, has no data.
        subg = nx.DiGraph(g.subgraph(branch_nodes).edges)
        subgraph = {"graph": nxGraph_to_dict(subg)}
        previous_results = {
            "previous_results": [
                dct for dct in presults if dct["node_id"] in subg.nodes()
            ]
        }

        subg_request = deepcopy(watershed_request)
        subg_request.update(subgraph)
        subg_request.update(previous_results)

        subgraph_response_dict = solve_watershed(subg_request, False, context=context)
        subgraph_results = subgraph_response_dict["results"]

        presults.extend(subgraph_results)
        db = db.combine_first(pandas.DataFrame(subgraph_results).set_index("node_id"))

    response_dict = solve_watershed(
        watershed=watershed_request,
        treatment_pre_validated=False,
        context=context,
    )
    results = response_dict["results"] + response_dict["leaf_results"]

    check_db = pandas.DataFrame(results).set_index("node_id").sort_index(axis=0)
    check_results_dataframes(db.sort_index(axis=0), check_db)

    for df in [check_db, db]:
        ro_generated = df.query('node_type == "land_surface"').runoff_volume_cuft.sum()
        ro_discharged = df.query(
            "node_id == '0'"
        ).runoff_volume_cuft_total_discharged.sum()
        ro_retained = df.query("node_id == '0'").runoff_volume_cuft_total_retained.sum()

        assert abs(ro_generated - (ro_discharged + ro_retained)) <= 1  # +- 1 cuft
