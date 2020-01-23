from typing import List, Tuple
from collections import Counter
from functools import partial

import networkx as nx
from .algorithms import find_cycle


def validate_network(G: nx.Graph, **kwargs) -> Tuple[List, List, List, List]:
    """Checks if there is a cycle, and prints a helpful
    message if there is.
    """
    _partial_sort = partial(sorted, key=lambda x: str(x))

    # force cycles to be ordered so that we can test against them
    simplecycles = list(map(_partial_sort, nx.simple_cycles(G)))

    findcycles = find_cycle(G, **kwargs)

    multiple_outs = [(k, v) for k, v in G.out_degree() if v > 1]

    duplicate_edges: List[str] = []
    if len(G.edges()) != len(set(G.edges())):
        duplicate_edges = [k for k, v in Counter(G.edges()).items() if v > 1]

    return simplecycles, findcycles, multiple_outs, duplicate_edges


def is_valid(G: nx.Graph) -> bool:
    return all([len(_) == 0 for _ in validate_network(G)])
