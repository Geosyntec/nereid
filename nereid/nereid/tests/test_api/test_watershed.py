from copy import deepcopy
import json

import pytest
import numpy
import networkx as nx

from nereid.api.api_v1.models import watershed_models
from nereid.core import config
from nereid.src.network.algorithms import get_subset
from nereid.src.network.utils import nxGraph_to_dict, graph_factory
from nereid.tests.utils import attrs_to_resubmit


@pytest.mark.parametrize("size", [13, 55, 77, 115])
@pytest.mark.parametrize("pct_tmnt", [0, 0.3, 0.6, 0.8])
def test_post_solve_watershed(watershed_responses, size, pct_tmnt):

    post_response = watershed_responses[size, pct_tmnt]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert watershed_models.WatershedResponse(**prjson)
    assert prjson["status"].lower() != "failure"


@pytest.mark.parametrize("size", [13, 115, 250])
@pytest.mark.parametrize("pct_tmnt", [0, 0.3, 0.6, 0.8])
def test_post_solve_watershed_stable(
    client, watershed_requests, watershed_responses, size, pct_tmnt
):
    watershed_request = watershed_requests[size, pct_tmnt]
    post_response = watershed_responses[size, pct_tmnt]

    results = post_response.json()["data"]["results"]

    reqd_min_attrs = attrs_to_resubmit(results)
    previous_results = {
        "previous_results": [
            {k: dct[k] for k in dct.keys() if k in reqd_min_attrs + ["node_id"]}
            for dct in results
        ]
    }

    g = graph_factory(watershed_request["graph"])

    numpy.random.seed(28)

    # this is way overkill, but I wanted to be sure all subsets work.
    # first we pick 4 random node set lenghts. This determines how
    # many dirty nodes we'll have this time. Then we choose a set of
    # this size from the nodes available in the first solve at random.
    # then we subgraph the first graph to just include  the 'influencers'
    # of these nodes, obtaining the minimum set of nodes needed for the solve.
    # Then we solve this subgraph and assert that _literally_nothing_changed_
    # when we solve just a part of the larger graph.
    # Then we rinse and repeat this whole process 2 more times.
    # Then we do all of the previous yet again according to the pytest
    # parametrization
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

            payload = json.dumps(new_request)
            route = config.API_LATEST + "/watershed/solve"
            response = client.post(route, data=payload)

            subgraph_results = response.json()["data"]["results"]

            for subg_result in subgraph_results:
                node = subg_result["node_id"]
                og_result = [n for n in results if n["node_id"] == node][0]
                subg_node_degree = subg.in_degree(node)
                for k, v in subg_result.items():
                    og = og_result[k]
                    if isinstance(v, str):
                        err_stmt = f"node: {node}; degree: {subg_node_degree}, attr: {k}, orig value: {og}; new value: {v}"
                        assert v == og, err_stmt

                    elif "load_mpn" in k and isinstance(v, (int, float)):
                        err_stmt = f"node: {node}; degree: {subg_node_degree}, attr: {k}, orig value: {og}; new value: {v}"
                        # allow floating point errors only
                        if og == 0:
                            assert v >= 0 and v < 1e-3, (og, v, err_stmt)
                        else:
                            # the MPN load is frequently in the gazillions, so this
                            # tolerance can be a little more forgiving, especially considering
                            # the serialization round-trip. Note that the mpn_conc is not
                            # afforded the same concession.
                            assert abs(og - v) < 1, err_stmt

                    elif isinstance(v, (int, float)):
                        err_stmt = f"node: {node}; degree: {subg_node_degree}, attr: {k}, orig value: {og}; new value: {v}"
                        # allow floating point errors only
                        if og == 0:
                            assert v >= 0 and v < 1e-3, (og, v, err_stmt)
                        else:
                            assert (
                                abs(og - v) < 1e-3 or (abs(og - v) / og) < 1e-6
                            ), err_stmt


@pytest.mark.skipif(config.NEREID_FORCE_FOREGROUND, reason="tasks ran in foreground")
@pytest.mark.parametrize("size", [13, 55, 77, 115])
@pytest.mark.parametrize("pct_tmnt", [0, 0.3, 0.6, 0.8])
def test_get_solve_watershed(client, watershed_responses, size, pct_tmnt):

    key = size, pct_tmnt
    post_response = watershed_responses[key]

    prjson = post_response.json()
    result_route = prjson["result_route"]

    get_response = client.get(result_route)
    assert get_response.status_code == 200

    grjson = get_response.json()
    assert watershed_models.WatershedResponse(**prjson)
    assert grjson["task_id"] == prjson["task_id"]
    assert grjson["result_route"] == prjson["result_route"]
    assert grjson["status"].lower() != "failure"

    if grjson["status"].lower() == "success":  # pragma: no branch
        assert len(grjson["data"]["results"]) == size
