import networkx as nx
from nereid.core.celery_app import celery_app

from nereid.src.network.tasks import network_subgraphs, validate_network


@celery_app.task(acks_late=True, track_started=True)
def background_validate_network_from_dict(graph):
    return validate_network(graph)


@celery_app.task(acks_late=True, track_started=True)
def background_network_subgraphs(graph, nodes):
    return network_subgraphs(graph, nodes)
