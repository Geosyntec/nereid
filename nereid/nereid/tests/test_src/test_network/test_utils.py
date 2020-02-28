import pytest
import networkx as nx

from nereid.src.network import utils

# import graph_factory, nxGraph_to_dict, thin_graph_dict, clean_graph_dict

from nereid.tests.utils import is_equal_subset


def test_graph_factory_no_edges():
    g1 = {"nodes": [{"id": "A"}, {"id": "C"}, {"id": "B"}]}

    G = utils.graph_factory(g1)
    assert len(G.nodes) == 3


def test_round_trip_dict_to_dict(graph_dict_isvalid):
    graph_dict, isvalid = graph_dict_isvalid

    # round trips back to dictionaries are only possible if graph is directed.
    # this is because if the graph is undirected, then the 'source' and 'target'
    # keys _might_ be swapped.
    # if graph_dict['directed']:
    _g = utils.graph_factory(graph_dict)
    rt_graph_dict = utils.nxGraph_to_dict(_g)
    assert is_equal_subset(graph_dict, rt_graph_dict)


def test_round_trip_graph_to_graph(graph_obj_isvalid):
    graph_obj, isvalid = graph_obj_isvalid

    _g = utils.nxGraph_to_dict(graph_obj)

    G = utils.graph_factory(_g)

    assert nx.is_isomorphic(G, graph_obj)  # same structure nodes and edges

    for node, data in G.nodes(data=True):  # same node attrs
        assert data == graph_obj.nodes[node]

    if G.is_multigraph():
        for s, t, k, data in G.edges(data=True, keys=True):  # same edge attrs
            assert is_equal_subset(graph_obj.edges[(s, t, k)], data)
    else:
        for s, t, data in G.edges(data=True):  # same edge attrs
            assert is_equal_subset(graph_obj.edges[(s, t)], data)


def test_thin_graph_dict(graph_dict_isvalid):

    graph_dict, isvalid = graph_dict_isvalid

    _graph_dict = utils.thin_graph_dict(graph_dict)

    assert is_equal_subset(_graph_dict, graph_dict)

    edge_meta = [dct.get("metadata", {}) for dct in _graph_dict.get("edges", [{}])]
    node_meta = [dct.get("metadata", {}) for dct in _graph_dict.get("nodes", [{}])]

    assert all([len(e) == 1 if "key" in e else len(e) == 0 for e in edge_meta])
    assert all([len(n) == 0 for n in node_meta])


@pytest.mark.parametrize("check", ["edges", "nodes", "multigraph", "directed"])
def test_thin_graph_dict_roundtrip_dict_to_dict(graph_dict_isvalid, check):

    graph_dict, isvalid = graph_dict_isvalid

    _graph_dict = utils.thin_graph_dict(graph_dict)

    _g = utils.graph_factory(_graph_dict)
    rt_graph_dict = utils.nxGraph_to_dict(_g)

    # if it's in the input, check that it's in the output too.
    if graph_dict.get(check, None) is not None:
        assert is_equal_subset(rt_graph_dict[check], graph_dict[check])


def test_thin_graph_dict_roundtrip_graph_to_graph(graph_obj_isvalid):

    graph_obj, isvalid = graph_obj_isvalid

    _g = utils.thin_graph_dict(utils.nxGraph_to_dict(graph_obj))

    rt_Graph = utils.graph_factory(_g)

    assert rt_Graph.is_directed() == graph_obj.is_directed()
    assert rt_Graph.is_multigraph() == graph_obj.is_multigraph()
    assert nx.is_isomorphic(rt_Graph, graph_obj)


def test_clean_graph_object(graph_obj_isvalid):

    graph_obj, isvalid = graph_obj_isvalid
    clean_graph_dict = utils.clean_graph_dict(graph_obj)

    assert all([isinstance(n["id"], str) for n in clean_graph_dict["nodes"]])
    assert all([isinstance(e["source"], str) for e in clean_graph_dict["edges"]])
    assert all([isinstance(e["target"], str) for e in clean_graph_dict["edges"]])

    clean_graph_obj = nx.relabel_nodes(graph_obj, lambda x: str(x))
    _g = utils.graph_factory(clean_graph_dict)

    assert nx.is_isomorphic(_g, clean_graph_obj)
