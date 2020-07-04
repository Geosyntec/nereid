from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.models.treatment_facility_models import (
    TreatmentFacilitiesStrict,
    validate_treatment_facility_models,
)
from nereid.api.api_v1.models.watershed_models import Watershed, WatershedResponse
from nereid.api.api_v1.utils import get_valid_context, run_task, standard_json_response
from nereid.src.watershed.tasks import solve_watershed

router = APIRouter()


def validate_watershed_request(
    watershed_req: Watershed, context: dict = Depends(get_valid_context),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:

    watershed: Dict[str, Any] = watershed_req.dict(by_alias=True)

    unvalidated_treatment_facilities = watershed.get("treatment_facilities")
    if unvalidated_treatment_facilities is not None:
        valid_models = validate_treatment_facility_models(
            unvalidated_treatment_facilities, context
        )
        validated_treatment_facilities = TreatmentFacilitiesStrict.construct(
            treatment_facilities=valid_models
        )
        watershed["treatment_facilities"] = validated_treatment_facilities.dict()[
            "treatment_facilities"
        ]

    return watershed, context


@router.post(
    "/watershed/solve",
    tags=["watershed", "main"],
    response_model=WatershedResponse,
    response_class=ORJSONResponse,
)
async def post_solve_watershed(
    watershed_pkg: Tuple[Dict[str, Any], Dict[str, Any]] = Depends(
        validate_watershed_request
    ),
) -> Dict[str, Any]:
    watershed, context = watershed_pkg

    task = bg.background_solve_watershed.s(
        watershed=watershed, treatment_pre_validated=True, context=context
    )
    return run_task(task=task, router=router, get_route="get_watershed_result")


@router.get(
    "/watershed/solve/{task_id}",
    tags=["watershed", "main"],
    response_model=WatershedResponse,
    response_class=ORJSONResponse,
)
async def get_watershed_result(task_id: str) -> Dict[str, Any]:
    task = bg.background_solve_watershed.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_watershed_result")
