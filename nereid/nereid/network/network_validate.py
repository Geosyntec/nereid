import time
from typing import List, Tuple, Dict
from collections import Counter
from functools import partial

import networkx as nx

from .utils import graph_factory


def celery_test(seconds: int = 1):  # pragma: no cover
    start = time.time()
    print("entering long task..")
    time.sleep(seconds)
    end = time.time()

    secs = end - start

    # raise ValueError('test fail')
    # make this work right

    return {"message": f"task took {secs:.1f} seconds."}


def find_cycle(G: nx.Graph, **kwargs) -> List:
    """Wraps networkx.find_cycle to return empty list
    if no cycle is found.
    """
    try:
        return list(nx.find_cycle(G, **kwargs))

    except nx.exception.NetworkXNoCycle:
        return []


def validate_network(G: nx.Graph, **kwargs) -> Tuple[List, List, List, List]:
    """Checks if there is a cycle, and prints a helpful
    message if there is.
    """
    _partial_sort = partial(sorted, key=lambda x: str(x))

    # force cycles to be ordered so that we can test against them
    simplecycles = list(map(_partial_sort, nx.simple_cycles(G)))

    findcycles = find_cycle(G, **kwargs)

    multiple_outs = [(k, v) for k, v in G.out_degree() if v > 1]

    duplicate_edges = []
    if len(G.edges()) != len(set(G.edges())):
        duplicate_edges = [k for k, v in Counter(G.edges()).items() if v > 1]

    return simplecycles, findcycles, multiple_outs, duplicate_edges


def is_valid(G):
    return all([len(_) == 0 for _ in validate_network(G)])


def validate_network_from_dict(graph: Dict) -> Dict:
    G = graph_factory(graph)
    res = validate_network(G)

    if all([len(_) == 0 for _ in res]):
        return {"status": "valid"}

    else:
        simplecycles, findcycles, multiple_outs, duplicate_edges = res
        return {
            "status": "invalid",
            "node_cycles": simplecycles,
            "edge_cycles": findcycles,
            "multiple_out_edges": multiple_outs,
            "duplicate_edges": duplicate_edges,
        }
