from typing import Any, Dict, List, Optional, Union

import networkx as nx

from nereid.src.network import validate
from nereid.src.network.algorithms import get_subset, parallel_sequential_subgraph_nodes
from nereid.src.network.render import (
    fig_to_image,
    render_solution_sequence,
    render_subgraphs,
)
from nereid.src.network.utils import graph_factory, thin_graph_dict


def validate_network(graph: Dict) -> Dict[str, Union[bool, List]]:
    """

    Parameters
    ----------
    graph : dict
        graph in graph-dict format.
        For example:
        graph = {
            "directed": True,
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        }

    """

    _graph = thin_graph_dict(graph)
    G = graph_factory(_graph)

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

    _graph = thin_graph_dict(graph)

    node_ids = [node["id"] for node in nodes]

    G = graph_factory(_graph)
    subset = get_subset(G, node_ids)
    sub_g = G.subgraph(subset)

    subgraph_nodes = [
        {"nodes": [{"id": n} for n in nodes]}
        for nodes in nx.weakly_connected_components(sub_g)
    ]

    result: Dict[str, Any] = {"graph": _graph}
    result.update({"requested_nodes": nodes})
    result.update({"subgraph_nodes": subgraph_nodes})

    return result


def render_subgraph_svg(task_result: dict, npi: Optional[float] = None) -> bytes:

    g = graph_factory(task_result["graph"])

    fig = render_subgraphs(
        g,
        request_nodes=task_result["requested_nodes"],
        subgraph_nodes=task_result["subgraph_nodes"],
        npi=npi,
    )

    svg_bin = fig_to_image(fig)
    svg: bytes = svg_bin.read()

    return svg


def solution_sequence(
    graph: Dict[str, Any], min_branch_size: int
) -> Dict[str, Dict[str, List[Dict[str, List[Dict[str, Union[str, Dict]]]]]]]:

    _graph = thin_graph_dict(graph)  # strip unneeded metadata

    G = graph_factory(_graph)

    _sequence = parallel_sequential_subgraph_nodes(G, min_branch_size)

    sequence = {
        "parallel": [
            {"series": [{"nodes": [{"id": n} for n in nodes]} for nodes in series]}
            for series in _sequence
        ]
    }

    result: Dict[str, Any] = {"graph": _graph}
    result["min_branch_size"] = min_branch_size
    result["solution_sequence"] = sequence

    return result


def render_solution_sequence_svg(
    task_result: dict, npi: Optional[float] = None
) -> bytes:

    _graph = thin_graph_dict(task_result["graph"])  # strip unneeded metadata

    g = graph_factory(_graph)

    _sequence = task_result["solution_sequence"]

    solution_sequence = [
        [[n["id"] for n in ser["nodes"]] for ser in p["series"]]
        for p in _sequence["parallel"]
    ]

    fig = render_solution_sequence(g, solution_sequence=solution_sequence, npi=npi)

    svg_bin = fig_to_image(fig)
    svg: bytes = svg_bin.read()

    return svg
