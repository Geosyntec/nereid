import pytest
import networkx as nx

from nereid.src.network.utils import graph_factory, nxGraph_to_dict
from nereid.tests.utils import is_equal_subset


def test_graph_factory_no_edges():
    g1 = {"nodes": [{"id": "A"}, {"id": "C"}, {"id": "B"}]}

    G = graph_factory(g1)
    assert len(G.nodes) == 3


def test_round_trip_dict_to_dict(graph_dict_isvalid):
    graph_dict, isvalid = graph_dict_isvalid

    # round trips back to dictionaries are only possible if graph is directed.
    # this is because if the graph is undirected, then the 'source' and 'target'
    # keys _might_ be swapped.
    # if graph_dict['directed']:
    _g = graph_factory(graph_dict)
    G = nxGraph_to_dict(_g)
    assert is_equal_subset(graph_dict, G)


def test_round_trip_graph_to_graph(graph_obj_isvalid):
    graph_obj, isvalid = graph_obj_isvalid

    _g = nxGraph_to_dict(graph_obj)

    G = graph_factory(_g)

    assert nx.is_isomorphic(G, graph_obj)  # same structure nodes and edges

    for node, data in G.nodes(data=True):  # same node attrs
        assert data == graph_obj.nodes[node]

    if G.is_multigraph():
        for s, t, k, data in G.edges(data=True, keys=True):  # same edge attrs
            assert is_equal_subset(graph_obj.edges[(s, t, k)], data)
    else:
        for s, t, data in G.edges(data=True):  # same edge attrs
            assert is_equal_subset(graph_obj.edges[(s, t)], data)
