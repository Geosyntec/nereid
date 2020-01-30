from typing import Dict, List, Any, Union

import networkx as nx

from nereid.core.cache import cache_decorator

from . import validate
from .utils import graph_factory
from .algorithms import get_subset
from .render import render_subgraphs, fig_to_image


def validate_network(graph: Dict) -> Dict[str, Union[bool, List]]:
    G = graph_factory(graph)

    isvalid = validate.is_valid(G)

    result: Dict[str, Union[bool, List]] = {"isvalid": isvalid}

    if isvalid:
        return result

    else:
        _keys = ["node_cycles", "edge_cycles", "multiple_out_edges", "duplicate_edges"]
        for key, value in zip(_keys, validate.validate_network(G)):
            result[key] = value

        return result


def network_subgraphs(
    graph: Dict[str, Any], nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:

    node_ids = [node["id"] for node in nodes]

    G = graph_factory(graph)
    subset = get_subset(G, node_ids)
    g = G.subgraph(subset)

    subgraph_nodes = [
        {"nodes": [{"id": n} for n in nodes]}
        for nodes in nx.weakly_connected_components(g)
    ]

    result: Dict[str, Any] = {"graph": graph}
    result.update({"requested_nodes": nodes})
    result.update({"subgraph_nodes": subgraph_nodes})

    return result


@cache_decorator(ex=3600 * 24)  # expires in 24 hours
def render_subgraph_svg(task_result: dict) -> str:

    g = graph_factory(task_result["graph"])

    fig = render_subgraphs(
        g, task_result["requested_nodes"], task_result["subgraph_nodes"]
    )

    svg_bin = fig_to_image(fig)
    svg = svg_bin.read().decode("utf-8")

    return svg
