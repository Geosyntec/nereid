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


def _recursive_get_subset(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    if subset is None:
        subset = set([node])

    for p in g.predecessors(node):
        subset.add(p)

    for s in g.successors(node):
        subset.add(s)

        if s != node:
            _recursive_get_subset(g, s, subset=subset)

    return subset


def get_subset(g: nx.DiGraph, nodes: Union[Set[str], List[str]]) -> Set[str]:
    if isinstance(nodes, (set, list)):
        result = set()
        for n in nodes:
            result.update(_recursive_get_subset(g, n))
    else:
        result = _recursive_get_subset(g, nodes)

    return result


def get_all_predecessors(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    if subset is None:
        subset = set([node])

    for p in g.predecessors(node):
        subset.add(p)
        get_all_predecessors(g, p, subset=subset)
    return subset


def get_all_successors(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    if subset is None:
        subset = set([node])

    for s in g.successors(node):
        subset.add(s)
        if node != s:
            get_all_successors(g, s, subset=subset)
    return subset
