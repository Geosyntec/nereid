from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from nereid.core.celery_app import celery_app
from nereid.api.api_v1.utils import standard_json_response
from nereid.api.api_v1.models.response_models import JSONAPIResponse

router = APIRouter(prefix="/task", default_response_class=ORJSONResponse)


@router.get("/{task_id}", response_model=JSONAPIResponse)
async def get_task(task_id: str) -> JSONAPIResponse:
    task = celery_app.AsyncResult(task_id)
    return standard_json_response(task, router=router, get_route="get_task")

