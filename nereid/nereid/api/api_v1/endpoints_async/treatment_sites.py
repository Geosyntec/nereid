from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.async_utils import run_task, standard_json_response
from nereid.api.api_v1.models.treatment_site_models import (
    TreatmentSiteResponse,
    TreatmentSites,
)
from nereid.api.api_v1.utils import get_valid_context

router = APIRouter()


@router.post(
    "/treatment_site/validate",
    tags=["treatment_site", "validate"],
    response_model=TreatmentSiteResponse,
    response_class=ORJSONResponse,
)
async def initialize_treatment_site(
    request: Request,
    treatment_sites: TreatmentSites = Body(...),
    context: dict = Depends(get_valid_context),
) -> dict[str, Any]:
    task = bg.initialize_treatment_sites.s(
        treatment_sites.model_dump(), context=context
    )

    return await run_task(request, task, "get_treatment_site_parameters")


@router.get(
    "/treatment_site/validate/{task_id}",
    tags=["treatment_site", "validate"],
    response_model=TreatmentSiteResponse,
    response_class=ORJSONResponse,
)
async def get_treatment_site_parameters(
    request: Request, task_id: str
) -> dict[str, Any]:
    task = bg.initialize_treatment_sites.AsyncResult(task_id, app=router)
    return await standard_json_response(request, task, "get_treatment_site_parameters")
