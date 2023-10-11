from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.async_utils import standard_json_response
from nereid.bg_worker import celery_app
from nereid.models.response_models import JSONAPIResponse

router = APIRouter(prefix="/task", default_response_class=ORJSONResponse)


@router.get("/{task_id}", response_model=JSONAPIResponse)
async def get_task(request: Request, task_id: str) -> dict[str, Any]:
    task = celery_app.AsyncResult(task_id)
    return await standard_json_response(request, task)
