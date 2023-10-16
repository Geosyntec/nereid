import logging
import os

from celery import Celery

from nereid.src import tasks

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("tasks", backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    broker_connection_retry_on_startup=True,
)

inspector = celery_app.control.inspect()

logger = logging.getLogger("nereid-celery-worker")


@celery_app.task(acks_late=True, track_started=True)
def background_ping():  # pragma: no cover
    logger.info("background pinged")
    return True


@celery_app.task(acks_late=True, track_started=True)
def background_sleep(seconds: int = 1):  # pragma: no cover
    logger.info("background worker sleeping...")
    import time

    time.sleep(seconds)
    logger.info("background worker sleep complete.")
    return True


@celery_app.task(acks_late=True, track_started=True)
def validate_network(graph):  # pragma: no cover
    return tasks.validate_network(graph=graph)


@celery_app.task(acks_late=True, track_started=True)
def network_subgraphs(graph, nodes):  # pragma: no cover
    return tasks.network_subgraphs(graph=graph, nodes=nodes)


@celery_app.task(acks_late=True, track_started=True)
def render_subgraph_svg(task_result, npi):  # pragma: no cover
    return tasks.render_subgraph_svg(task_result=task_result, npi=npi).decode()


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
def initialize_treatment_sites(treatment_sites, context):  # pragma: no cover
    return tasks.initialize_treatment_sites(
        treatment_sites=treatment_sites,
        context=context,
    )


@celery_app.task(acks_late=True, track_started=True)
def solve_watershed(watershed, treatment_pre_validated, context):  # pragma: no cover
    return tasks.solve_watershed(
        watershed=watershed,
        treatment_pre_validated=treatment_pre_validated,
        context=context,
    )
