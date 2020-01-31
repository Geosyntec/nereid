import pytest

from nereid.src.network.tasks import (
    validate_network,
    network_subgraphs,
    render_subgraph_svg,
)


@pytest.mark.parametrize(
    "edgelist, isvalid, exp",
    [
        (
            [("a", "b"), ("b", "c"), ("d", "c"), ("c", "e")],
            True,
            ([], [], [], []),
        ),  # this one's valid
        (
            [("a", "b"), ("b", "c"), ("d", "c"), ("c", "a")],
            False,
            ([["a", "b", "c"]], [("a", "b", 0), ("b", "c", 0), ("c", "a", 0)], [], []),
        ),  # cycle a->b->c->a
        (
            [("a", "b"), ("b", "c"), ("d", "c"), ("c", "e"), ("c", "e")],
            False,
            ([], [], [("c", 2)], [("c", "e")]),
        ),  # duplicate edge
        (
            [("a", "b"), ("b", "c"), ("d", "c"), ("a", "e")],
            False,
            ([], [], [("a", 2)], []),
        ),  # multiple out edges, a->b & a->e
    ],
)
def test_validate_network(edgelist, isvalid, exp):
    expected_result = [isvalid] + list(exp)

    g = {"edges": [{"source": s, "target": t} for s, t in edgelist], "directed": True}

    result = validate_network(g)

    keys = [
        "isvalid",
        "node_cycles",
        "edge_cycles",
        "multiple_out_edges",
        "duplicate_edges",
    ]

    for key, value in zip(keys, expected_result):
        result[key] = value


@pytest.fixture
def subgraph_request():
    return {
        "graph": {
            "directed": True,
            "edges": [
                {"source": "3", "target": "1"},
                {"source": "5", "target": "3"},
                {"source": "7", "target": "1"},
                {"source": "9", "target": "1"},
                {"source": "11", "target": "1"},
                {"source": "13", "target": "3"},
                {"source": "15", "target": "9"},
                {"source": "17", "target": "7"},
                {"source": "19", "target": "17"},
                {"source": "21", "target": "15"},
                {"source": "23", "target": "1"},
                {"source": "25", "target": "5"},
                {"source": "27", "target": "11"},
                {"source": "29", "target": "7"},
                {"source": "31", "target": "11"},
                {"source": "33", "target": "25"},
                {"source": "35", "target": "23"},
                {"source": "4", "target": "2"},
                {"source": "6", "target": "2"},
                {"source": "8", "target": "6"},
                {"source": "10", "target": "2"},
                {"source": "12", "target": "2"},
                {"source": "14", "target": "2"},
                {"source": "16", "target": "12"},
                {"source": "18", "target": "12"},
                {"source": "20", "target": "8"},
                {"source": "22", "target": "6"},
                {"source": "24", "target": "12"},
            ],
        },
        "nodes": [{"id": "3"}, {"id": "29"}, {"id": "18"}],
    }


@pytest.fixture()
def subgraph_result(subgraph_request):
    return network_subgraphs(subgraph_request["graph"], subgraph_request["nodes"])


def test_network_subgraphs(subgraph_request):
    result = network_subgraphs(subgraph_request["graph"], subgraph_request["nodes"])

    assert "graph" in result
    assert "subgraph_nodes" in result
    assert "requested_nodes" in result


def test_render_subgraph_svg(subgraph_result):
    result = render_subgraph_svg(subgraph_result)
    assert b"svg" in result
