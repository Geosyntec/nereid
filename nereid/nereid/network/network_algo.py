from typing import Dict, List

import networkx as nx

from .utils import graph_factory, get_subset


def network_subgraphs(graph: Dict, nodes: List) -> Dict:

    nodelist = [node["id"] for node in nodes]

    G = graph_factory(graph)
    subset = get_subset(G, nodelist)
    g = G.subgraph(subset)

    subgraph_nodes = [
        {"nodes": [{"id": n} for n in nodes]}
        for nodes in nx.weakly_connected_components(g)
    ]

    result = {"graph": graph}
    result.update({"requested_nodes": nodes})
    result.update({"subgraph_nodes": subgraph_nodes})

    return result
