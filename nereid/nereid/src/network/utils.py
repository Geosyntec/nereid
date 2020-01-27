import json
import networkx as nx


def graph_factory(graph: nx.Graph):
    """

    Parameters
    ----------
    graph : dict

    """
    g = nx.MultiGraph()
    if graph["directed"]:
        g = g.to_directed()

    edges = graph.get("edges", None)
    if not edges:
        raise ValueError("edges are required")

    G = nx.from_edgelist(
        [(d.get("source"), d.get("target"), d.get("metadata")) for d in edges],
        create_using=g,
    )

    if graph.get("nodes"):
        nx.set_node_attributes(
            G, {n.get("id"): n.get("metadata") for n in graph["nodes"]}
        )

    return G


def nxGraph_to_dict(g):
    result = nx.node_link_data(g, {"link": "edges"})
    for dct in result["nodes"]:
        dct["id"] = str(dct["id"])

    for dct in result["edges"]:
        dct["source"] = str(dct["source"])
        dct["target"] = str(dct["target"])
    return result
