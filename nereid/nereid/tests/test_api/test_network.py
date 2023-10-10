import networkx as nx
import pytest

from nereid.api.api_v1.models import network_models
from nereid.core.config import settings
from nereid.src.network.utils import clean_graph_dict
from nereid.tests.utils import poll_testclient_url


@pytest.mark.parametrize(
    "post_response_name, isfast, isvalid",
    [
        ("valid_graph_response_fast", True, True),
        ("invalid_graph_response_fast", True, False),
        ("valid_graph_response_slow", False, True),
        ("invalid_graph_response_slow", False, False),
    ],
)
def test_post_network_validate(
    client, named_validation_responses, post_response_name, isfast, isvalid
):
    post_response = named_validation_responses[post_response_name]
    prjson = post_response.json()
    assert network_models.NetworkValidationResponse(**prjson)

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
def test_get_network_validate(
    client, named_validation_responses, post_response_name, isfast, isvalid
):
    post_response = named_validation_responses[post_response_name]

    prjson = post_response.json()
    grjson = prjson
    result_route = prjson.get("result_route")

    if result_route:
        get_route = f"{settings.API_LATEST}/task/{prjson.get('task_id', 'error$!#*&^')}"
        get_response = client.get(get_route)
        assert get_response.status_code == 200, (prjson, get_route)

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


@pytest.mark.parametrize(
    "post_response_name, exp",
    [
        (
            "subgraph_response_fast",
            {
                "subgraph_nodes": [
                    {
                        "nodes": [
                            {"id": "3", "metadata": {}},
                            {"id": "7", "metadata": {}},
                            {"id": "5", "metadata": {}},
                            {"id": "29", "metadata": {}},
                            {"id": "23", "metadata": {}},
                            {"id": "17", "metadata": {}},
                            {"id": "9", "metadata": {}},
                            {"id": "13", "metadata": {}},
                            {"id": "1", "metadata": {}},
                            {"id": "11", "metadata": {}},
                        ]
                    },
                    {
                        "nodes": [
                            {"id": "12", "metadata": {}},
                            {"id": "6", "metadata": {}},
                            {"id": "2", "metadata": {}},
                            {"id": "4", "metadata": {}},
                            {"id": "24", "metadata": {}},
                            {"id": "10", "metadata": {}},
                            {"id": "16", "metadata": {}},
                            {"id": "18", "metadata": {}},
                            {"id": "14", "metadata": {}},
                        ]
                    },
                ]
            },
        )
    ],
)
def test_get_finished_network_subgraph(
    client, named_subgraph_responses, post_response_name, exp
):
    post_response = named_subgraph_responses[post_response_name]

    prjson = post_response.json()
    grjson = prjson
    result_route = prjson.get("result_route")

    if result_route:
        get_response = poll_testclient_url(client, result_route)
        assert get_response.status_code == 200

        grjson = get_response.json()
        assert grjson["task_id"] is not None
        assert grjson["result_route"] is not None
    assert network_models.SubgraphResponse(**prjson)

    assert grjson["status"].lower() == "success"
    assert grjson["data"] is not None

    assert len(grjson["data"]["subgraph_nodes"]) == len(exp["subgraph_nodes"])


@pytest.mark.parametrize(
    "post_response_name", [("subgraph_response_fast"), ("subgraph_response_slow")]
)
def test_post_network_subgraph(client, named_subgraph_responses, post_response_name):
    post_response = named_subgraph_responses[post_response_name]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert network_models.SubgraphResponse(**prjson)
    assert prjson["status"].lower() != "failure"


@pytest.mark.parametrize(
    "post_response_name",
    [
        ("subgraph_response_fast"),
    ],
)
def test_get_render_subgraph_svg_fast(
    client, named_subgraph_responses, post_response_name
):
    post_response = named_subgraph_responses[post_response_name]
    assert post_response.status_code == 200
    rjson = post_response.json()

    result_route = rjson.get("result_route")

    if result_route:
        svg_response = poll_testclient_url(client, result_route + "/img")
        assert svg_response.status_code == 200
        assert "DOCTYPE svg PUBLIC" in svg_response.content.decode()

        # try to cover cached retrieval by asking again
        svg_response = client.get(result_route + "/img")
        assert svg_response.status_code == 200


def test_get_render_subgraph_svg_slow(client):
    route = settings.API_LATEST + "/network/subgraph"

    slow_graph = clean_graph_dict(nx.gnr_graph(200, p=0.05, seed=42))
    nodes = [{"id": "3"}, {"id": "29"}, {"id": "18"}]

    payload = {"graph": slow_graph, "nodes": nodes}

    response = client.post(route, json=payload)
    result_route = response.json().get("result_route")
    if result_route:
        svg_response = client.get(result_route + "/img")
        assert svg_response.status_code == 200
        srjson = svg_response.json()
        assert srjson["status"].lower() != "failure"
        assert srjson["task_id"] is not None


@pytest.mark.parametrize(
    "post_response_name, isfast",
    [("subgraph_response_fast", True), ("subgraph_response_slow", False)],
)
def test_get_render_subgraph_svg_bad_media_type(
    client, named_subgraph_responses, post_response_name, isfast
):
    post_response = named_subgraph_responses[post_response_name]
    assert post_response.status_code == 200
    rjson = post_response.json()

    result_route = rjson.get("result_route")
    if result_route:
        svg_response = client.get(result_route + "/img?media_type=png")
        assert svg_response.status_code == 400
        assert "media_type not supported" in svg_response.content.decode()


@pytest.mark.parametrize("min_branch_size", [2, 6, 10, 50])
@pytest.mark.parametrize("n_graphs", [1, 3, 5, 10])
@pytest.mark.parametrize("min_max", [(10, 11), (20, 40)])
def test_post_solution_sequence(
    solution_sequence_response, min_branch_size, n_graphs, min_max
):
    key = min_branch_size, n_graphs, min_max
    post_response = solution_sequence_response[key]

    assert post_response.status_code == 200, post_response.content
    prjson = post_response.json()
    assert network_models.SolutionSequenceResponse(**prjson)
    assert prjson["status"].lower() != "failure"


@pytest.mark.parametrize("min_branch_size", [2, 6, 10, 50])
@pytest.mark.parametrize("n_graphs", [1, 3, 5, 10])
@pytest.mark.parametrize("min_max", [(10, 11), (20, 40)])
def test_get_solution_sequence(
    client, solution_sequence_response, min_branch_size, n_graphs, min_max
):
    key = min_branch_size, n_graphs, min_max
    post_response = solution_sequence_response[key]

    prjson = post_response.json()
    grjson = prjson
    result_route = prjson.get("result_route")
    if result_route:
        get_response = client.get(result_route)
        assert get_response.status_code == 200

        grjson = get_response.json()
        assert grjson["task_id"] == prjson["task_id"]
        assert grjson["result_route"] == prjson["result_route"]
    assert network_models.SolutionSequenceResponse(**prjson)
    assert grjson["status"].lower() == "success"
    assert grjson["data"] is not None


@pytest.mark.parametrize("min_branch_size", [6])
@pytest.mark.parametrize("n_graphs", [1, 3])
@pytest.mark.parametrize("min_max", [(3, 4), (10, 11), (20, 40)])
def test_get_render_solution_sequence(
    client, solution_sequence_response, min_branch_size, n_graphs, min_max
):
    key = min_branch_size, n_graphs, min_max
    post_response = solution_sequence_response[key]
    assert post_response.status_code == 200

    prjson = post_response.json()
    result_route = prjson.get("result_route")

    if result_route:
        _ = client.get(result_route + "/img")
        svg_response = client.get(result_route + "/img")

        assert svg_response.status_code == 200

        if "html" in svg_response.headers["content-type"]:
            assert "DOCTYPE svg PUBLIC" in svg_response.content.decode()

        else:
            srjson = svg_response.json()
            assert srjson["status"].lower() != "failure"
            assert srjson["task_id"] is not None


def test_get_render_solution_sequence_bad_media_type(
    client, solution_sequence_response
):
    key = 6, 3, (10, 11)
    post_response = solution_sequence_response[key]
    assert post_response.status_code == 200

    prjson = post_response.json()
    result_route = prjson.get("result_route")
    if result_route:
        svg_response = client.get(result_route + "/img?media_type=png")
        assert svg_response.status_code == 400
        assert "media_type not supported" in svg_response.content.decode()
