import pytest

from nereid.src.network import tasks
from nereid.src.network.utils import graph_factory


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
            (
                [["a", "b", "c"]],
                [["a", "b", "0"], ["b", "c", "0"], ["c", "a", "0"]],
                [],
                [],
            ),
        ),  # cycle a->b->c->a
        (
            [("a", "b"), ("b", "c"), ("d", "c"), ("c", "e"), ("c", "e")],
            False,
            ([], [], [["c", "2"]], [["c", "e"]]),
        ),  # duplicate edge
        (
            [("a", "b"), ("b", "c"), ("d", "c"), ("a", "e")],
            False,
            ([], [], [["a", "2"]], []),
        ),  # multiple out edges, a->b & a->e
    ],
)
def test_validate_network(edgelist, isvalid, exp):
    expected_result = [isvalid] + list(exp)

    g = {"edges": [{"source": s, "target": t} for s, t in edgelist], "directed": True}

    graph_factory(g)

    result = tasks.validate_network(g)

    keys = [
        "isvalid",
        "node_cycles",
        "edge_cycles",
        "multiple_out_edges",
        "duplicate_edges",
    ]

    if isvalid:
        assert result["isvalid"] == isvalid
    else:
        for key, value in zip(keys, expected_result, strict=True):
            assert result[key] == value


@pytest.fixture
def subgraph_result(subgraph_request_dict):
    return tasks.network_subgraphs(
        subgraph_request_dict["graph"], subgraph_request_dict["nodes"]
    )


def test_network_subgraph_result(subgraph_result):
    result = subgraph_result

    assert "graph" in result
    assert "subgraph_nodes" in result
    assert len(result["subgraph_nodes"]) == 2
    assert "requested_nodes" in result


def test_render_subgraph_svg(subgraph_result):
    result = tasks.render_subgraph_svg(subgraph_result).decode()
    assert "svg" in result


@pytest.fixture
def solution_sequence_result(subgraph_request_dict):
    return tasks.solution_sequence(subgraph_request_dict["graph"], 4)


def test_solution_sequence_result(solution_sequence_result):
    result = solution_sequence_result

    assert "graph" in result
    assert "min_branch_size" in result
    assert len(result["solution_sequence"]["parallel"]) == 2


def test_render_solution_sequence_svg(solution_sequence_result):
    result = tasks.render_solution_sequence_svg(solution_sequence_result).decode()
    assert "svg" in result
