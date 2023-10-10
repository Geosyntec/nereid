from typing import Any, Dict, Tuple

from fastapi import APIRouter, Depends, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid._compat import model_dump
from nereid.api.api_v1.async_utils import run_task, standard_json_response
from nereid.api.api_v1.models.treatment_facility_models import (
    validate_treatment_facility_models,
)
from nereid.api.api_v1.models.watershed_models import Watershed, WatershedResponse
from nereid.api.api_v1.utils import get_valid_context

router = APIRouter()


def validate_watershed_request(
    watershed_req: Watershed,
    context: dict = Depends(get_valid_context),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    watershed: Dict[str, Any] = model_dump(watershed_req, by_alias=True)

    unvalidated_treatment_facilities = watershed.get("treatment_facilities")
    if unvalidated_treatment_facilities is not None:
        valid_models = validate_treatment_facility_models(
            unvalidated_treatment_facilities, context
        )

        watershed["treatment_facilities"] = valid_models

    return watershed, context


@router.post(
    "/watershed/solve",
    tags=["watershed", "main"],
    response_model=WatershedResponse,
    response_class=ORJSONResponse,
)
async def post_solve_watershed(
    request: Request,
    watershed_pkg: Tuple[Dict[str, Any], Dict[str, Any]] = Depends(
        validate_watershed_request
    ),
) -> Dict[str, Any]:
    watershed, context = watershed_pkg
    task = bg.solve_watershed.s(
        watershed=watershed, treatment_pre_validated=True, context=context
    )
    return await run_task(request, task, "get_watershed_result")


@router.get(
    "/watershed/solve/{task_id}",
    tags=["watershed", "main"],
    response_model=WatershedResponse,
    response_class=ORJSONResponse,
)
async def get_watershed_result(request: Request, task_id: str) -> Dict[str, Any]:
    task = bg.solve_watershed.AsyncResult(task_id, app=router)
    return await standard_json_response(request, task, "get_watershed_result")
