from typing import Dict, List, Any

import networkx as nx

from . import validate
from .utils import graph_factory
from .algorithms import get_subset


def network_subgraphs(
    graph: Dict[str, Any], nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:

    nodelist = [node["id"] for node in nodes]

    G = graph_factory(graph)
    subset = get_subset(G, nodelist)
    g = G.subgraph(subset)

    subgraph_nodes = [
        {"nodes": [{"id": n} for n in nodes]}
        for nodes in nx.weakly_connected_components(g)
    ]

    result: Dict[str, Any] = {"graph": graph}
    result.update({"requested_nodes": nodes})
    result.update({"subgraph_nodes": subgraph_nodes})

    return result


def validate_network(graph: Dict) -> Dict:
    G = graph_factory(graph)
    res = validate.validate_network(G)

    if all([len(_) == 0 for _ in res]):
        return {"status": "valid"}

    else:
        simplecycles, findcycles, multiple_outs, duplicate_edges = res
        return {
            "status": "invalid",
            "node_cycles": simplecycles,
            "edge_cycles": findcycles,
            "multiple_out_edges": multiple_outs,
            "duplicate_edges": duplicate_edges,
        }
