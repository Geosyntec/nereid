import json
import time
from itertools import product

import pytest
from starlette.testclient import TestClient
import networkx as nx

from nereid.main import app
from nereid.core.config import API_LATEST
from nereid.src.network.utils import clean_graph_dict
from nereid.tests.utils import get_payload, generate_n_random_valid_watershed_graphs


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def named_validation_responses(client):

    route = API_LATEST + "/network/validate"
    responses = {}
    slow_valid = json.dumps(clean_graph_dict(nx.gnr_graph(15000, p=0.05, seed=42)))
    slow_invalid = json.dumps(clean_graph_dict(nx.gnc_graph(15000, seed=42)))

    init_post_requests = [
        ("valid_graph_response_fast", get_payload("network_validate_is_valid.json")),
        (
            "invalid_graph_response_fast",
            get_payload("network_validate_is_invalid_cycle.json"),
        ),
        ("valid_graph_response_slow", slow_valid),
        ("invalid_graph_response_slow", slow_invalid),
    ]

    for name, payload in init_post_requests:
        response = client.post(route, data=payload)
        responses[name] = response

    yield responses


@pytest.fixture(scope="module")
def named_subgraph_responses(client):

    route = API_LATEST + "/network/subgraph"
    responses = {}

    slow_graph = clean_graph_dict(nx.gnr_graph(200, p=0.05, seed=42))
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

    yield responses


@pytest.fixture(scope="module")
def solution_sequence_response(client):

    min_branch_size = [2, 6, 10, 50]
    n_graphs = [1, 3, 5, 10]
    min_max = [(10, 11), (20, 40)]

    responses = {}

    for bs, ngraph, minmax in product(min_branch_size, n_graphs, min_max):

        g = generate_n_random_valid_watershed_graphs(ngraph, *minmax)
        payload = json.dumps(clean_graph_dict(g))

        route = API_LATEST + "/network/solution_sequence"

        response = client.post(route + f"?min_branch_size={bs}", data=payload)

        responses[(bs, ngraph, minmax)] = response

        if all([minmax == (10, 11), ngraph == 3, bs == 6]):
            result_route = response.json()["result_route"]
            client.get(result_route + "/img?media_type=svg")
            time.sleep(0.5)

    yield responses
