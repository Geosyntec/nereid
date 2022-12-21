from collections import deque
from functools import partial
from typing import Callable, List, Tuple

import networkx as nx

from nereid.src.network.algorithms import find_cycle
from nereid.src.network.utils import GraphType


def validate_network(
    G: GraphType, **kwargs: dict
) -> Tuple[List[List], List[List[str]], List[List[str]], List[List[str]]]:
    """Checks if there is a cycle, and prints a helpful
    message if there is.
    """
    _partial_sort: Callable = partial(sorted, key=lambda x: str(x))

    # force cycles to be ordered so that we can test against them
    node_cycles: List[List] = list(map(_partial_sort, nx.simple_cycles(G)))

    edge_cycles = [list(map(str, _)) for _ in find_cycle(G, **kwargs)]

    out_degs = nx.MultiDiGraph(G).out_degree()
    if isinstance(out_degs, int):  # pragma: no cover
        out_degs = [("", out_degs)]
    multiple_outs = [[str(node), str(deg)] for node, deg in out_degs if deg > 1]

    duplicate_edges: List[List] = []
    if len(G.edges()) != len(set(G.edges())):
        duplicate_edges = [
            [s, t] for s, t, *k in nx.MultiGraph(G).edges(keys=True) if k[0]
        ]

    return node_cycles, edge_cycles, multiple_outs, duplicate_edges


def is_valid(G: GraphType) -> bool:
    try:
        # catch cycles
        deque(nx.topological_sort(G), maxlen=0)
    except nx.exception.NetworkXUnfeasible:
        return False

    try:
        out_degs = nx.DiGraph(G).out_degree()
        # catch multiple out connections
        assert all((v <= 1 for _, v in out_degs))  # type: ignore

        # catch
        assert len(G.edges()) == len(set(G.edges()))
    except Exception:
        return False

    return True
