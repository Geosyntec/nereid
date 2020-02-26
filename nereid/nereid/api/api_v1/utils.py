from typing import Any, Dict, Optional, Tuple
import os

from fastapi import APIRouter, HTTPException
from celery.exceptions import TimeoutError
from celery.result import AsyncResult

from nereid.core import config, utils
import nereid.bg_worker as bg


def wait_a_sec_and_see_if_we_can_return_some_data(
    task: AsyncResult, timeout: float = 0.2
) -> Optional[Dict[str, Any]]:
    result = None
    try:
        result = task.get(timeout=timeout)
    except TimeoutError:
        pass

    return result


def run_task_by_name(
    taskname: str,
    router: APIRouter,
    args: Tuple,
    get_route: str,
    force_foreground: Optional[bool] = False,
) -> Dict[str, Any]:

    if force_foreground:
        fxn = getattr(bg, taskname)
        result = fxn(*args)
        return dict(data=result)

    background_task = getattr(bg, "background_" + taskname)
    task = background_task.apply_async(args=args)
    return standard_json_response(task, router, get_route)


def standard_json_response(
    task: AsyncResult,
    router: APIRouter,
    get_route: str,
    timeout: float = 0.2,
    api_version: str = config.API_LATEST,
) -> Dict[str, Any]:
    router_path = router.url_path_for(get_route, task_id=task.id)

    result_route = f"{api_version}{router_path}"

    _ = wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=timeout)

    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    # TODO: remove this pragma and apply to other routes
    if task.successful():  # pragma: no branch
        response["data"] = task.result

    return response


def get_valid_context(state: str = "state", region: str = "region") -> Dict[str, Any]:
    context = utils.get_request_context(state, region)
    isvalid, msg = utils.validate_request_context(context)
    if not isvalid:
        raise HTTPException(status_code=400, detail=msg)
    return context
