import json
import networkx as nx


def _graph_factory(graph):
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


def graph_factory(graph):
    """
    Parameters
    ----------
    network : dict
        

    Returns:
        nx.graph or List[nx.graph]

    """
    # network = json.loads(network_json)
    return _graph_factory(graph)
    # elif network.get("graphs"):
    #     graphs = network["graphs"]
    #     return nx.compose_all(list(map(_graph_factory, graphs)))
    # else:
    #     raise ValueError("network must have a `graph` attribute")


def dep_graph_factory(network):
    """
    Parameters
    ----------
    network : dict
        

    Returns:
        nx.graph or List[nx.graph]

    """
    # network = json.loads(network_json)
    if network.get("graph"):
        return _graph_factory(network["graph"])
    # elif network.get("graphs"):
    #     graphs = network["graphs"]
    #     return nx.compose_all(list(map(_graph_factory, graphs)))
    else:
        raise ValueError("network must have a `graph` attribute")


def _recursive_get_subset(g, node, subset=None):
    if subset is None:
        subset = set([node])

    for p in g.predecessors(node):
        subset.add(p)

    for s in g.successors(node):
        subset.add(s)

        if s != node:
            _recursive_get_subset(g, s, subset=subset)

    return subset


def get_subset(g, nodes):
    if isinstance(nodes, (set, list)):
        result = set()
        for n in nodes:
            result.update(_recursive_get_subset(g, n))
    else:
        result = _recursive_get_subset(g, nodes)

    return result


def get_all_predecessors(g, node, subset=None):
    if subset is None:
        subset = set([node])

    for p in g.predecessors(node):
        subset.add(p)
        get_all_predecessors(g, p, subset=subset)
    return subset


def get_all_successors(g, node, subset=None):
    if subset is None:
        subset = set([node])

    for s in g.successors(node):
        subset.add(s)
        if node != s:
            get_all_successors(g, s, subset=subset)
    return subset
