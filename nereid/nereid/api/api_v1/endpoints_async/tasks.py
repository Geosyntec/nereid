from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.async_utils import standard_json_response
from nereid.models.response_models import JSONAPIResponse

router = APIRouter(prefix="/task", default_response_class=ORJSONResponse)


@router.get("/ping", response_model=JSONAPIResponse)
async def get_ping(request: Request) -> dict[str, Any]:  # pragma: no cover
    task = bg.background_ping.apply_async()
    return await standard_json_response(request, task)


@router.get("/sleep", response_model=JSONAPIResponse)
async def get_sleep(request: Request, s: int = 1) -> dict[str, Any]:  # pragma: no cover
    task = bg.background_sleep.s(seconds=s).apply_async()
    return await standard_json_response(request, task)


@router.get("/inspect", response_model=JSONAPIResponse)
async def get_inspect(request: Request) -> dict[str, Any]:  # pragma: no cover
    i = bg.inspector
    res = i.reserved()
    act = i.active()
    sch = i.scheduled()
    count = 0
    for workerid in act.keys():
        count += len(res.get(workerid, []))
        count += len(act.get(workerid, []))
        count += len(sch.get(workerid, []))

    response = {
        "data": {
            "count_in_queue": count,
            "reserved": res,
            "active": act,
            "scheduled": sch,
            "stats": i.stats(),
        }
    }
    return response


@router.get("/{task_id}", response_model=JSONAPIResponse)
async def get_task(request: Request, task_id: str) -> dict[str, Any]:
    task = bg.celery_app.AsyncResult(task_id)
    return await standard_json_response(request, task)
