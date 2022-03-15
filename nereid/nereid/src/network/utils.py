import copy
from typing import Any, Collection, Dict

import networkx as nx


def graph_factory(graph: Dict[str, Any]) -> nx.Graph:
    """
    Parameters
    ----------
    graph : dict

    """

    edges = graph.get("edges", None)
    nodes = graph.get("nodes", None)

    # if not edges:
    #     raise ValueError("edges are required")

    # need to be as permissive as possible. if user does
    # not
    is_multigraph = graph.get("multigraph", True)
    is_directed = graph.get("directed", False)

    # multi graphs are not valid graphs for `nereid`. These are caught
    # by the src.network.validate module. we need to create them as
    # multi graphs so we can identify which edges are duplicated.
    if is_multigraph:
        if is_directed:
            cls = nx.MultiDiGraph

        else:
            cls = nx.MultiGraph
            # this is the most tolerant type of graph

    elif is_directed:
        cls = nx.DiGraph

    else:
        cls = nx.Graph  # for testing purposes

    if edges:

        if is_multigraph:
            g = cls(
                nx.from_edgelist(
                    [
                        (
                            d.get("source"),
                            d.get("target"),
                            d.get("key", None),
                            d.get("metadata", {}),
                        )
                        for d in edges
                    ],
                    create_using=cls(),
                )
            )
        else:
            g = cls(
                nx.from_edgelist(
                    [
                        (d.get("source"), d.get("target"), d.get("metadata", {}))
                        for d in edges
                    ],
                    create_using=cls(),
                )
            )
    else:
        g = cls()

    if nodes:
        g.add_nodes_from([(n.get("id"), n.get("metadata", {})) for n in nodes])

    return g


def thin_graph_dict(graph_dict: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(graph_dict)

    nodes = result.get("nodes", None)
    if nodes is not None:
        for dct in nodes:
            dct["metadata"] = {}

    edges = result.get("edges", [{}])
    for dct in edges:
        meta = dct.get("metadata", {})

        if "key" in meta and meta.get("key", None) is not None:
            key = meta["key"]
            dct["metadata"] = {"key": key}
        else:
            dct["metadata"] = {}

    return result


def nxGraph_to_dict(g: nx.Graph) -> Dict[str, Any]:
    """Convert a networkx garph object into a dictionary
    suitable for serialization.

    Example:

    g = nx.gnr_graph(n=7, p=0, seed=0)
    nxGraph_to_dict(g)
    >>>{
        'directed': True,
        'multigraph': False,
        'graph': {},
        'nodes': [
            {'metadata': {}, 'id': 0},
            {'metadata': {}, 'id': 1},
            {'metadata': {}, 'id': 2},
            {'metadata': {}, 'id': 3},
            {'metadata': {}, 'id': 4},
            {'metadata': {}, 'id': 5},
            {'metadata': {}, 'id': 6}
        ],
        'edges': [
            {'metadata': {}, 'source': 1, 'target': 0},
            {'metadata': {}, 'source': 2, 'target': 1},
            {'metadata': {}, 'source': 3, 'target': 2},
            {'metadata': {}, 'source': 4, 'target': 2},
            {'metadata': {}, 'source': 5, 'target': 2},
            {'metadata': {}, 'source': 6, 'target': 1}
        ]
    }
    """
    result: Dict[str, Any] = nx.node_link_data(g, {"link": "edges"})
    for dct in result["nodes"]:
        id_ = dct.pop("id")
        dct["metadata"] = copy.deepcopy(dct)
        dct["id"] = id_

    for dct in result["edges"]:
        source = dct.pop("source")
        target = dct.pop("target")
        dct["metadata"] = copy.deepcopy(dct)
        dct.pop("key", 0)
        dct["source"] = source
        dct["target"] = target

    return result


def clean_graph_dict(g: nx.Graph) -> Dict[str, Any]:
    """
    Converts a graph to a dictionary, ensuring all node labels
    are converted to strings
    """
    return nxGraph_to_dict(nx.relabel_nodes(g, lambda x: str(x)))


def sum_node_attr(g: nx.Graph, nodes: Collection, attr: str) -> float:
    """Returns sum of one attribute for node's upstream nodes

    Parameters
    ----------

    g: node network (nx.DiGraph)
    nodes: nodes to aggregate. This allows predecessors to be computed only
    once for all attr rather than for each attr
    attr: name of attribute to return sum of (e.g.  "eff_area_ac")
    """
    return sum(g.nodes[n].get(attr, 0) for n in nodes)
