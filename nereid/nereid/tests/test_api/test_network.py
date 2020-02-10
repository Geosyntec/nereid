from pathlib import Path
import json
import time

import pytest
import networkx as nx
from starlette.testclient import TestClient

from nereid.core.config import API_LATEST
from nereid.main import app
from nereid.api.api_v1.models import network_models
from nereid.src.network.utils import nxGraph_to_dict
import nereid.tests.test_data


TEST_PATH = Path(nereid.tests.test_data.__file__).parent.resolve()


def get_payload(file):
    path = TEST_PATH / file
    return path.read_text()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def named_validation_responses(client):

    route = API_LATEST + "/network/validate"
    responses = {}
    slow_valid = json.dumps(nxGraph_to_dict(nx.gnr_graph(15000, p=0.05, seed=42)))
    slow_invalid = json.dumps(nxGraph_to_dict(nx.gnc_graph(15000, seed=42)))

    init_post_requests_fromfile = [
        ("valid_graph_response_fast", get_payload("network_validate_is_valid.json")),
        (
            "invalid_graph_response_fast",
            get_payload("network_validate_is_invalid_cycle.json"),
        ),
        ("valid_graph_response_slow", slow_valid),
        ("invalid_graph_response_slow", slow_invalid),
    ]

    for name, payload in init_post_requests_fromfile:
        responses[name] = client.post(route, data=payload)

    return responses


@pytest.mark.parametrize(
    "post_response_name, isfast, isvalid",
    [
        ("valid_graph_response_fast", True, True),
        ("invalid_graph_response_fast", True, False),
        ("valid_graph_response_slow", False, True),
        ("invalid_graph_response_slow", False, False),
    ],
)
def test_post_network_validate_fast(
    client, named_validation_responses, post_response_name, isfast, isvalid
):

    post_response = named_validation_responses[post_response_name]
    assert post_response.status_code == 200

    prjson = post_response.json()
    assert network_models.NetworkValidationResponse(**prjson)
    assert prjson["task_id"] is not None
    assert prjson["result_route"] is not None
    ping = client.get(prjson["result_route"])
    assert ping.status_code == 200

    if isfast:
        assert prjson["status"].lower() == "success"
        assert prjson["data"] is not None
        assert prjson["data"]["isvalid"] == isvalid
    else:
        assert prjson["status"].lower() != "failure"


@pytest.mark.parametrize(
    "post_response_name, isfast, isvalid",
    [
        ("valid_graph_response_fast", True, True),
        ("invalid_graph_response_fast", True, False),
        ("valid_graph_response_slow", False, True),
        ("invalid_graph_response_slow", False, False),
    ],
)
def test_get_network_validate_fast(
    client, named_validation_responses, post_response_name, isfast, isvalid
):
    post_response = named_validation_responses[post_response_name]

    prjson = post_response.json()
    result_route = prjson["result_route"]

    get_response = client.get(result_route)
    assert get_response.status_code == 200

    grjson = get_response.json()
    assert network_models.NetworkValidationResponse(**grjson)

    assert grjson["task_id"] == prjson["task_id"]
    assert grjson["result_route"] == prjson["result_route"]
    if isfast:
        assert grjson["status"].lower() == "success"
        assert grjson["data"] is not None
        assert grjson["data"]["isvalid"] == isvalid
    else:
        assert grjson["status"].lower() != "failure"


@pytest.fixture(scope="module")
def named_subgraph_responses(client):

    route = API_LATEST + "/network/subgraph"
    responses = {}

    slow_graph = nxGraph_to_dict(nx.gnr_graph(200, p=0.05, seed=42))
    nodes = [{"id": "3"}, {"id": "29"}, {"id": "18"}]

    init_post_requests = [
        # name, file or object, is-fast
        ("subgraph_response_fast", get_payload("network_subgraph_request.json"), True),
        (
            "subgraph_response_slow",
            json.dumps(dict(graph=slow_graph, nodes=nodes)),
            False,
        ),
    ]

    for name, payload, isfast in init_post_requests:
        response = client.post(route, data=payload)
        responses[name] = response
        result_route = response.json()["result_route"]

        if isfast:
            # trigger the svg render here so it's ready to get later.
            client.get(result_route + "/img?media_type=svg")
            time.sleep(0.5)

    return responses


@pytest.mark.parametrize(
    "post_response_name, exp_n_nodes", [("subgraph_response_fast", 2)]
)
def test_get_finished_network_subgraph(
    client, named_subgraph_responses, post_response_name, exp_n_nodes
):
    post_response = named_subgraph_responses[post_response_name]

    prjson = post_response.json()
    result_route = prjson["result_route"]

    get_response = client.get(result_route)
    assert get_response.status_code == 200

    grjson = get_response.json()
    assert network_models.SubgraphResponse(**prjson)

    assert grjson["status"].lower() == "success"
    assert grjson["task_id"] is not None
    assert grjson["result_route"] is not None
    assert grjson["data"] is not None
    assert len(grjson["data"]["subgraph_nodes"]) == exp_n_nodes


@pytest.mark.parametrize(
    "post_response_name", [("subgraph_response_fast"), ("subgraph_response_slow")]
)
def test_post_network_subgraph(client, named_subgraph_responses, post_response_name):
    post_response = named_subgraph_responses[post_response_name]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert network_models.SubgraphResponse(**prjson)
    assert prjson["status"].lower() != "failure"
    assert prjson["task_id"] is not None
    assert prjson["result_route"] is not None


@pytest.mark.parametrize(
    "post_response_name, isfast",
    [("subgraph_response_fast", True), ("subgraph_response_slow", False)],
)
def test_get_render_subgraph_svg(
    client, named_subgraph_responses, post_response_name, isfast
):

    post_response = named_subgraph_responses[post_response_name]
    rjson = post_response.json()

    result_route = rjson["result_route"]

    svg_response = client.get(result_route + "/img")
    assert svg_response.status_code == 200
    if isfast:
        assert "svg" in svg_response.content.decode()
    else:
        srjson = svg_response.json()
        assert srjson["status"].lower() != "failure"
        assert srjson["task_id"] is not None
