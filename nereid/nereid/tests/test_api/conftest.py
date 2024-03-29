import json
import time
from itertools import product

import networkx as nx
import pytest
from fastapi.testclient import TestClient

from nereid.factory import create_app
from nereid.src.network.utils import clean_graph_dict
from nereid.tests.utils import generate_n_random_valid_watershed_graphs, get_test_data


@pytest.fixture(scope="module")
def client(async_mode):
    mode = "none"
    if async_mode:
        mode = "replace"
    app = create_app(settings_override={"ASYNC_MODE": mode})
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def named_validation_responses(client):
    route = "api/v1/network/validate"
    responses = {}
    slow_valid = clean_graph_dict(nx.gnr_graph(150, p=0.05, seed=42))
    slow_invalid = clean_graph_dict(nx.gnc_graph(150, seed=42))

    init_post_requests = [
        (
            "valid_graph_response_fast",
            json.loads(get_test_data("network_validate_is_valid.json")),
        ),
        (
            "invalid_graph_response_fast",
            json.loads(get_test_data("network_validate_is_invalid_cycle.json")),
        ),
        ("valid_graph_response_slow", slow_valid),
        ("invalid_graph_response_slow", slow_invalid),
    ]

    for name, payload in init_post_requests:
        response = client.post(route, json=payload)
        responses[name] = response

    yield responses


@pytest.fixture(scope="module")
def named_subgraph_responses(client):
    route = "api/v1/network/subgraph"
    responses = {}

    slow_graph = clean_graph_dict(nx.gnr_graph(200, p=0.05, seed=42))
    nodes = [{"id": "3"}, {"id": "29"}, {"id": "18"}]

    init_post_requests = [
        # name, file or object, is-fast
        (
            "subgraph_response_fast",
            json.loads(get_test_data("network_subgraph_request.json")),
            # True
        ),
        (
            "subgraph_response_slow",
            {"graph": slow_graph, "nodes": nodes},
            # False,
        ),
    ]

    for name, payload in init_post_requests:
        response = client.post(route, json=payload)
        responses[name] = response
        result_route = response.json().get("result_route")

        if result_route:
            # trigger the svg render here so it's ready to get later.
            client.get(result_route + "/img?media_type=svg")
            time.sleep(0.5)

    yield responses


@pytest.fixture(scope="module")
def solution_sequence_response(client):
    min_branch_size = [2, 6, 10, 50]
    n_graphs = [1, 3, 5, 10]
    min_max = [(3, 4), (10, 11), (20, 40)]

    responses = {}

    for bs, ngraph, minmax in product(min_branch_size, n_graphs, min_max):
        g = generate_n_random_valid_watershed_graphs(ngraph, *minmax)
        payload = clean_graph_dict(g)

        route = "api/v1/network/solution_sequence"

        response = client.post(route + f"?min_branch_size={bs}", json=payload)

        responses[(bs, ngraph, minmax)] = response
        result_route = response.json().get("result_route")

        if all([minmax == (10, 11), ngraph == 3, bs == 6, result_route]):
            client.get(result_route + "/img?media_type=svg")
            time.sleep(0.5)

    yield responses


@pytest.fixture(scope="module")
def land_surface_loading_responses(client, land_surface_loading_response_dicts):
    details = ["true", "false"]
    responses = {}

    for detail_tf, ((nrows, nnodes), ls_request) in product(
        details, land_surface_loading_response_dicts.items()
    ):
        payload = ls_request
        route = "api/v1/land_surface/loading" + f"?details={detail_tf}"
        response = client.post(route, json=payload)

        responses[(detail_tf, nrows, nnodes)] = response

    yield responses


@pytest.fixture(scope="module")
def treatment_facility_responses(client, treatment_facility_dicts):
    responses = {}

    for name, dct in treatment_facility_dicts.items():
        payload = {"treatment_facilities": [dct]}
        route = "api/v1/treatment_facility/validate"
        response = client.post(route, json=payload)
        responses[name] = response

    yield responses


@pytest.fixture(scope="module")
def default_context_treatment_facility_responses(
    client, default_context_treatment_facility_dicts
):
    responses = {}

    for name, dct in default_context_treatment_facility_dicts.items():
        payload = {"treatment_facilities": [dct]}
        route = "api/v1/treatment_facility/validate"
        response = client.post(route, json=payload)
        responses[name] = response

    yield responses


@pytest.fixture(scope="module")
def treatment_site_responses(client, valid_treatment_site_requests):
    responses = {}

    for name, dct in valid_treatment_site_requests.items():
        payload = dct
        route = "api/v1/treatment_site/validate"
        response = client.post(route, json=payload)
        responses[name] = response

    yield responses


@pytest.fixture(scope="module")
def watershed_responses(client, watershed_requests):
    responses = {}

    for name, dct in watershed_requests.items():
        payload = dct
        route = "api/v1/watershed/solve"
        response = client.post(route, json=payload)
        responses[name] = response

    yield responses
