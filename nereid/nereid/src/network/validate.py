from typing import List, Tuple
from collections import deque
from functools import partial

import networkx as nx
from .algorithms import find_cycle


def validate_network(
    G: nx.Graph, **kwargs
) -> Tuple[List[List[str]], List[List[str]], List[List[str]], List[List[str]]]:
    """Checks if there is a cycle, and prints a helpful
    message if there is.
    """
    _partial_sort = partial(sorted, key=lambda x: str(x))

    # force cycles to be ordered so that we can test against them
    node_cycles: List[List[str]] = list(
        map(_partial_sort, nx.simple_cycles(G))  # type: ignore
    )

    edge_cycles = [list(map(str, _)) for _ in find_cycle(G, **kwargs)]

    multiple_outs = [[str(k), str(v)] for k, v in G.out_degree() if v > 1]

    duplicate_edges: List[List[str]] = []
    if len(G.edges()) != len(set(G.edges())):
        duplicate_edges = [[s, t] for s, t, k in G.edges(keys=True) if k > 0]

    return node_cycles, edge_cycles, multiple_outs, duplicate_edges


def is_valid(G: nx.Graph) -> bool:
    try:
        # catch cycles
        deque(nx.topological_sort(G), maxlen=0)
    except nx.exception.NetworkXUnfeasible:
        return False

    try:
        # catch multiple out connections
        assert all((v <= 1 for k, v in G.out_degree()))

        # catch
        assert len(G.edges()) == len(set(G.edges()))
    except:
        return False

    return True
