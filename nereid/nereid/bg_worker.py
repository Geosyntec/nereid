import networkx as nx
from nereid.core.celery_app import celery_app

from nereid.network.network_validate import validate_network_from_dict
from nereid.network.network_algo import network_subgraphs


@celery_app.task(acks_late=True, track_started=True)
def background_validate_network_from_dict(graph):
    return validate_network_from_dict(graph)


@celery_app.task(acks_late=True, track_started=True)
def background_network_subgraphs(graph, nodes):
    return network_subgraphs(graph, nodes)
