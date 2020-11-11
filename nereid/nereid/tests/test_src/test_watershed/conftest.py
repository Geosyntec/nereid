import networkx as nx
import numpy
import pytest

from nereid.src.land_surface.tasks import land_surface_loading
from nereid.tests.utils import generate_random_land_surface_request


@pytest.fixture
def watershed_graph():
    g = nx.gnr_graph(n=13, p=0.0, seed=0)
    nx.relabel_nodes(g, lambda x: str(x), copy=False)

    return g


@pytest.fixture
def initial_node_data(contexts, watershed_graph):

    context = contexts["default"]
    numpy.random.seed(42)
    ls_req = generate_random_land_surface_request(watershed_graph.nodes(), context)
    ls_attrs = land_surface_loading(ls_req, details=False, context=context)["summary"]

    return {dct["node_id"]: dct for dct in ls_attrs}
