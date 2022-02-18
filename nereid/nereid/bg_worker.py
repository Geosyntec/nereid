import logging

from nereid.core.celery_app import celery_app
from nereid.src import tasks

# import (
#     initialize_treatment_facilities,
#     land_surface_loading,
#     network_subgraphs,
#     render_solution_sequence_svg,
#     render_subgraph_svg,
#     solution_sequence,
#     solve_watershed,
#     validate_network,
# )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(acks_late=True, track_started=True)
def background_ping():  # pragma: no cover
    logger.info("background pinged")
    return True


@celery_app.task(acks_late=True, track_started=True)
def validate_network(graph):  # pragma: no cover
    return tasks.validate_network(graph=graph)


@celery_app.task(acks_late=True, track_started=True)
def network_subgraphs(graph, nodes):  # pragma: no cover
    return tasks.network_subgraphs(graph=graph, nodes=nodes)


@celery_app.task(acks_late=True, track_started=True)
def render_subgraph_svg(task_result, npi):  # pragma: no cover
    bytes_response = tasks.render_subgraph_svg(task_result=task_result, npi=npi)
    return bytes_response.decode()


@celery_app.task(acks_late=True, track_started=True)
def solution_sequence(graph, min_branch_size):  # pragma: no cover
    return tasks.solution_sequence(graph=graph, min_branch_size=min_branch_size)


@celery_app.task(acks_late=True, track_started=True)
def render_solution_sequence_svg(task_result, npi):  # pragma: no cover
    return tasks.render_solution_sequence_svg(task_result=task_result, npi=npi).decode()


@celery_app.task(acks_late=True, track_started=True)
def land_surface_loading(land_surfaces, details, context):  # pragma: no cover
    return tasks.land_surface_loading(
        land_surfaces=land_surfaces, details=details, context=context
    )


@celery_app.task(acks_late=True, track_started=True)
def initialize_treatment_facilities(
    treatment_facilities, pre_validated, context
):  # pragma: no cover
    return tasks.initialize_treatment_facilities(
        treatment_facilities=treatment_facilities,
        pre_validated=pre_validated,
        context=context,
    )


@celery_app.task(acks_late=True, track_started=True)
def solve_watershed(watershed, treatment_pre_validated, context):  # pragma: no cover
    return tasks.solve_watershed(
        watershed=watershed,
        treatment_pre_validated=treatment_pre_validated,
        context=context,
    )
