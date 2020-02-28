import networkx as nx
from nereid.core.celery_app import celery_app

from nereid.src.network.tasks import (
    validate_network,
    network_subgraphs,
    render_subgraph_svg,
    solution_sequence,
    render_solution_sequence_svg,
)


@celery_app.task(acks_late=True, track_started=True)
def background_validate_network_from_dict(graph):
    return validate_network(graph)  # pragma: no cover


@celery_app.task(acks_late=True, track_started=True)
def background_network_subgraphs(graph, nodes):
    return network_subgraphs(graph, nodes)  # pragma: no cover


@celery_app.task(acks_late=True, track_started=True)
def background_render_subgraph_svg(task_result, npi):
    return render_subgraph_svg(task_result, npi).decode()  # pragma: no cover


@celery_app.task(acks_late=True, track_started=True)
def background_solution_sequence(graph, min_branch_size):
    return solution_sequence(graph, min_branch_size)  # pragma: no cover


@celery_app.task(acks_late=True, track_started=True)
def background_render_solution_sequence_svg(task_result, npi):
    return render_solution_sequence_svg(task_result, npi).decode()  # pragma: no cover
