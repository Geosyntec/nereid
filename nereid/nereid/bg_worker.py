import networkx as nx
from nereid.core.celery_app import celery_app

from nereid.src.network.tasks import (
    validate_network,
    network_subgraphs,
    render_subgraph_svg,
    solution_sequence,
    render_solution_sequence_svg,
)
from nereid.src.land_surface.tasks import land_surface_loading
from nereid.src.treatment_facility.tasks import initialize_treatment_facilities


@celery_app.task(acks_late=True, track_started=True)
def background_validate_network(graph):
    return validate_network(graph=graph)  # pragma: no cover


@celery_app.task(acks_late=True, track_started=True)
def background_network_subgraphs(graph, nodes):
    return network_subgraphs(graph=graph, nodes=nodes)  # pragma: no cover


@celery_app.task(acks_late=True, track_started=True)
def background_render_subgraph_svg(task_result, npi):
    return render_subgraph_svg(  # pragma: no cover
        task_result=task_result, npi=npi
    ).decode()


@celery_app.task(acks_late=True, track_started=True)
def background_solution_sequence(graph, min_branch_size):
    return solution_sequence(  # pragma: no cover
        graph=graph, min_branch_size=min_branch_size
    )


@celery_app.task(acks_late=True, track_started=True)
def background_render_solution_sequence_svg(task_result, npi):
    return render_solution_sequence_svg(  # pragma: no cover
        task_result=task_result, npi=npi
    ).decode()


@celery_app.task(acks_late=True, track_started=True)
def background_land_surface_loading(land_surfaces, details, context):
    return land_surface_loading(  # pragma: no cover
        land_surfaces=land_surfaces, details=details, context=context
    )


@celery_app.task(acks_late=True, track_started=True)
def background_initialize_treatment_facilities(treatment_facilities, context):
    return initialize_treatment_facilities(  # pragma: no cover
        treatment_facilities=treatment_facilities, context=context
    )
