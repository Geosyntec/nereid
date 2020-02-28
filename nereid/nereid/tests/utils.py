from pathlib import Path
from typing import Union, Dict, Set, List

import numpy
import networkx as nx

import nereid.tests.test_data

TEST_PATH = Path(nereid.tests.test_data.__file__).parent.resolve()


def get_payload(file):
    path = TEST_PATH / file
    return path.read_text()


def is_equal_subset(
    subset: Union[Dict, List, Set], superset: Union[Dict, List, Set]
) -> bool:
    """determine if all shared keys have equal value"""

    if isinstance(subset, dict):
        return all(
            key in superset and is_equal_subset(val, superset[key])
            for key, val in subset.items()
        )

    if isinstance(subset, list) or isinstance(subset, set):
        return all(
            any(is_equal_subset(subitem, superitem) for superitem in superset)
            for subitem in subset
        )

    # assume that subset is a plain value if none of the above match
    return subset == superset


def generate_n_random_valid_watershed_graphs(
    n_graphs: int = 3,
    min_graph_nodes: int = 20,
    max_graph_nodes: int = 50,
    seed: int = 42,
):

    G = nx.DiGraph()
    numpy.random.seed(seed)
    for i in range(n_graphs):
        n_nodes = numpy.random.randint(min_graph_nodes, max_graph_nodes)
        offset = len(G.nodes())
        g = nx.gnr_graph(n_nodes, 0.0, seed=i)
        G.add_edges_from([((offset + s), (offset + t)) for s, t in g.edges])
    return G
