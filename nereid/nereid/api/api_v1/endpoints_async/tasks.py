from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.async_utils import standard_json_response
from nereid.models.response_models import JSONAPIResponse

router = APIRouter(prefix="/task", default_response_class=ORJSONResponse)


@router.get("/ping", response_model=JSONAPIResponse)
async def get_ping(request: Request) -> dict[str, Any]:  # pragma: no cover
    task = bg.background_ping.apply_async()
    return await standard_json_response(request, task)


@router.get("/{task_id}", response_model=JSONAPIResponse)
async def get_task(request: Request, task_id: str) -> dict[str, Any]:
    task = bg.celery_app.AsyncResult(task_id)
    return await standard_json_response(request, task)
