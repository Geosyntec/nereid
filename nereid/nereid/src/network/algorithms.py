from typing import List, Optional, Set, Union

import networkx as nx


def find_cycle(G: nx.Graph, **kwargs) -> List:
    """Wraps networkx.find_cycle to return empty list
    if no cycle is found.
    """
    try:
        return list(nx.find_cycle(G, **kwargs))

    except nx.exception.NetworkXNoCycle:
        return []


def get_subset(g: nx.DiGraph, nodes: Union[str, Set[str], List[str]]) -> Set[str]:
    """This algorithm is for determining which nodes in a graph must be re-solved if
    `nodes` are dirty. It looks for the immediate parents of each dirty node, all
    descendants of the dirty nodes down to the root node (no 'out' edge connections),
    and the immediate parents of _each_ descdendant. This algorithm only works on
    directed acyclic graphs (DAGs).
    """
    if isinstance(nodes, (int, str)):
        nodes = [nodes]

    node_parents = {s for n in nodes for s in g.predecessors(n)}
    desc = {s for n in nodes for s in get_all_successors(g, n)}
    desc_parents = {s for d in desc for s in g.predecessors(d)}

    return set(nodes) | node_parents | desc | desc_parents


def get_all_predecessors(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    """This algorithm is a good deal faster than the nx.ancestors variant,
    **but** it only works on directed acyclic graphs (DAGs).
    """
    if subset is None:
        subset = set()

    for p in g.predecessors(node):
        subset.add(p)
        get_all_predecessors(g, p, subset=subset)
    return subset


def get_all_successors(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    """This algorithm is a good deal faster than the nx.descendants variant,
    **but** it only works on directed acyclic graphs (DAGs).
    """
    if subset is None:
        subset = set()

    for s in g.successors(node):
        subset.add(s)
        get_all_successors(g, s, subset=subset)
    return subset
