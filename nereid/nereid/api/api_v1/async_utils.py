import asyncio
from typing import Any, Dict, Optional, Union

from celery import Task
from celery.result import AsyncResult
from fastapi import Request

from nereid.core.config import settings


async def wait_a_sec_and_see_if_we_can_return_some_data(
    task: AsyncResult,
    timeout: float | None = None,
    exp: float | None = None,
) -> None:
    if timeout is None:  # pragma: no cover
        timeout = 0.5

    if exp is None:  # pragma: no cover
        exp = 1

    t = 0.0
    inc = 0.05  # check back every inc seconds
    while t < timeout:
        if task.ready():  # exit even if the task failed
            return None
        else:
            inc *= exp
            t += inc
            await asyncio.sleep(inc)
    return None


async def run_task(
    request: Request,
    task: Task,
    get_route: str = "get_task",
    force_foreground: Optional[bool] = False,
    timeout: float = 0.2,
) -> Dict[str, Any]:
    if force_foreground or settings.FORCE_FOREGROUND:  # pragma: no cover
        task_ret: Union[bytes, str] = task()
        response = {
            "data": task_ret,
            "task_id": "foreground",
            "result_route": "foreground",
        }

    else:
        response = await standard_json_response(
            request, task.apply_async(), get_route=get_route, timeout=timeout
        )

    return response


async def standard_json_response(
    request: Request,
    task: AsyncResult,
    get_route: str = "get_task",
    timeout: float = 0.2,
) -> Dict[str, Any]:
    _ = await wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=timeout)
    result_route = str(request.url_for(get_route, task_id=task.id))

    response = {
        "task_id": task.task_id,
        "status": task.status,
        "result_route": result_route,
    }

    if task.successful():
        response["data"] = task.result

    return response
