import pytest
import networkx as nx

from nereid.src.network.validate import is_valid, validate_network


@pytest.mark.parametrize(
    "edgelist, isvalid, result",
    [
        (
            [["a", "b"], ["b", "c"], ["d", "c"], ["c", "e"]],
            True,
            ([], [], [], []),
        ),  # this one's valid
        (
            [["a", "b"], ["b", "c"], ["d", "c"], ["c", "a"]],
            False,
            (
                [["a", "b", "c"]],
                [["a", "b", "0"], ["b", "c", "0"], ["c", "a", "0"]],
                [],
                [],
            ),
        ),  # cycle a->b->c->a
        (
            [["a", "b"], ["b", "c"], ["d", "c"], ["c", "e"], ["c", "e"]],
            False,
            ([], [], [["c", "2"]], [["c", "e"]]),
        ),  # duplicate edge
        (
            [["a", "b"], ["b", "c"], ["d", "c"], ["a", "e"]],
            False,
            ([], [], [["a", "2"]], []),
        ),  # multiple out edges, a->b & a->e
    ],
)
def test_validate_network(edgelist, isvalid, result):

    g = nx.from_edgelist(edgelist, create_using=nx.MultiDiGraph)
    assert isvalid == is_valid(g)
    assert result == validate_network(g)


@pytest.mark.parametrize(
    "g, expected",
    [  # multiple out connections
        (nx.gnc_graph(10, seed=42), False),
        # multiple out connections, cycles, duplicated edges
        (nx.random_k_out_graph(10, 2, 1, seed=42), False),
        (nx.gn_graph(10, seed=42), True),
    ],
)
def test_isvalid(g, expected):
    assert expected == is_valid(g)
