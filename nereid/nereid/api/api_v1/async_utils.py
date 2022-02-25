from typing import Any, Dict, Optional

from celery import Task
from celery.exceptions import TimeoutError
from celery.result import AsyncResult
from fastapi import APIRouter

from nereid.core.config import settings


def wait_a_sec_and_see_if_we_can_return_some_data(
    task: AsyncResult, timeout: float = 0.2
) -> Optional[Dict[str, Any]]:
    result = None
    try:
        result = task.get(timeout=timeout)
    except TimeoutError:
        pass

    return result


def run_task(
    task: Task,
    router: APIRouter,
    get_route: str,
    force_foreground: Optional[bool] = False,
) -> Dict[str, Any]:

    if force_foreground or settings.FORCE_FOREGROUND:  # pragma: no cover
        response = dict(data=task(), task_id="foreground", result_route="foreground")

    else:
        response = standard_json_response(task.apply_async(), router, get_route)

    return response


def standard_json_response(
    task: AsyncResult,
    router: APIRouter,
    get_route: str,
    timeout: float = 0.2,
    api_version: str = settings.API_LATEST,
) -> Dict[str, Any]:
    router_path = router.url_path_for(get_route, task_id=task.id)

    result_route = f"{api_version}{router_path}"

    _ = wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=timeout)

    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():
        response["data"] = task.result

    return response
