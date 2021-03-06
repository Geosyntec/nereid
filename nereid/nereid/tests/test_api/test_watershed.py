import json
from copy import deepcopy

import networkx as nx
import pytest

from nereid.api.api_v1.models import watershed_models
from nereid.core import config
from nereid.src.network.algorithms import get_subset
from nereid.src.network.utils import graph_factory, nxGraph_to_dict
from nereid.src.watershed.utils import attrs_to_resubmit
from nereid.tests.utils import check_subgraph_response_equal


@pytest.mark.parametrize("size", [50, 100])
@pytest.mark.parametrize("pct_tmnt", [0, 0.3, 0.6])
def test_post_solve_watershed(watershed_responses, size, pct_tmnt):

    post_response = watershed_responses[size, pct_tmnt]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert watershed_models.WatershedResponse(**prjson)
    assert prjson["status"].lower() != "failure"


@pytest.mark.parametrize("size", [50, 100])
@pytest.mark.parametrize("pct_tmnt", [0, 0.3, 0.6])
def test_get_solve_watershed(client, watershed_responses, size, pct_tmnt):

    key = size, pct_tmnt
    post_response = watershed_responses[key]

    prjson = post_response.json()
    if config.NEREID_FORCE_FOREGROUND:  # pragma: no cover
        grjson = prjson
    else:
        result_route = prjson["result_route"]

        get_response = client.get(result_route)
        assert get_response.status_code == 200

        grjson = get_response.json()
    assert watershed_models.WatershedResponse(**prjson)
    assert grjson["task_id"] == prjson["task_id"]
    assert grjson["result_route"] == prjson["result_route"]
    assert grjson["status"].lower() != "failure"

    if grjson["status"].lower() == "success":  # pragma: no branch
        grlen = len(grjson["data"]["results"]) + len(grjson["data"]["leaf_results"])
        assert grlen == size, (grlen, size)
        for res in grjson["data"]["results"]:
            errors = res.get("errors", "")
            assert "error" not in errors.lower()

            assert res.get("_version") is not None


def test_post_solve_watershed_stable(
    client, watershed_requests, watershed_responses, watershed_test_case
):

    size, pct_tmnt, dirty_nodes = watershed_test_case
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

    subg = nx.DiGraph(g.subgraph(get_subset(g, nodes=dirty_nodes)).edges)
    subgraph = {"graph": nxGraph_to_dict(subg)}

    new_request = deepcopy(watershed_request)
    new_request.update(subgraph)
    new_request.update(previous_results)

    payload = json.dumps(new_request)
    route = config.API_LATEST + "/watershed/solve"
    response = client.post(route, data=payload)

    subgraph_results = response.json()["data"]["results"]

    check_subgraph_response_equal(subgraph_results, results)
