from typing import Dict, Any
import json
import copy
import logging

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
            g = nx.MultiDiGraph()

        else:
            g = nx.MultiGraph()
            # this is the most tolerant type of graph

    elif is_directed:
        g = nx.DiGraph()

    else:
        g = nx.Graph()  # for testing purposes

    if edges:

        if g.is_multigraph():
            g = nx.from_edgelist(
                [
                    (
                        d.get("source"),
                        d.get("target"),
                        d.get("key", None),
                        d.get("metadata", {}),
                    )
                    for d in edges
                ],
                create_using=g,
            )
        else:
            g = nx.from_edgelist(
                [
                    (d.get("source"), d.get("target"), d.get("metadata", {}))
                    for d in edges
                ],
                create_using=g,
            )

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


def clean_graph_dict(g):
    return nxGraph_to_dict(nx.relabel_nodes(g, lambda x: str(x)))
