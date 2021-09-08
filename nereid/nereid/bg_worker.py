import logging

from nereid.core.celery_app import celery_app
from nereid.core.utils import validate_request_context
from nereid.src.land_surface.tasks import land_surface_loading
from nereid.src.network.tasks import (
    network_subgraphs,
    render_solution_sequence_svg,
    render_subgraph_svg,
    solution_sequence,
    validate_network,
)
from nereid.src.treatment_facility.tasks import initialize_treatment_facilities
from nereid.src.watershed.tasks import solve_watershed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(acks_late=True, track_started=True)
def background_ping():  # pragma: no cover
    logger.info("background pinged")
    return True


@celery_app.task(acks_late=True, track_started=True)
def background_validate_request_context(context):
    return validate_request_context(context)  # pragma: no cover


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
def background_initialize_treatment_facilities(
    treatment_facilities, pre_validated, context
):
    return initialize_treatment_facilities(  # pragma: no cover
        treatment_facilities=treatment_facilities,
        pre_validated=pre_validated,
        context=context,
    )


@celery_app.task(acks_late=True, track_started=True)
def background_solve_watershed(watershed, treatment_pre_validated, context):
    return solve_watershed(  # pragma: no cover
        watershed=watershed,
        treatment_pre_validated=treatment_pre_validated,
        context=context,
    )
