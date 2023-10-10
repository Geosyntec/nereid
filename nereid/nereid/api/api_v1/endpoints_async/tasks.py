from typing import Any, Dict

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.async_utils import standard_json_response
from nereid.api.api_v1.models.response_models import JSONAPIResponse
from nereid.core.celery_app import celery_app

router = APIRouter(prefix="/task", default_response_class=ORJSONResponse)


@router.get("/{task_id}", response_model=JSONAPIResponse)
async def get_task(request: Request, task_id: str) -> Dict[str, Any]:
    task = celery_app.AsyncResult(task_id)
    return await standard_json_response(request, task)
