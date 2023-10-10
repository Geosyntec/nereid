from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.async_utils import run_task, standard_json_response
from nereid.api.api_v1.models.treatment_facility_models import (
    TreatmentFacilities,
    TreatmentFacilitiesResponse,
    validate_treatment_facility_models,
)
from nereid.api.api_v1.utils import get_valid_context

router = APIRouter()


def validate_facility_request(
    treatment_facilities: TreatmentFacilities = Body(...),
    context: dict = Depends(get_valid_context),
) -> tuple[TreatmentFacilities, dict[str, Any]]:
    unvalidated_data = treatment_facilities.model_dump()["treatment_facilities"]

    valid_models = validate_treatment_facility_models(unvalidated_data, context)

    return (
        TreatmentFacilities.model_construct(treatment_facilities=valid_models),
        context,
    )


@router.post(
    "/treatment_facility/validate",
    tags=["treatment_facility", "validate"],
    response_model=TreatmentFacilitiesResponse,
    response_class=ORJSONResponse,
)
async def initialize_treatment_facility_parameters(
    request: Request,
    tmnt_facility_req: tuple[TreatmentFacilities, dict[str, Any]] = Depends(
        validate_facility_request
    ),
) -> dict[str, Any]:
    treatment_facilities, context = tmnt_facility_req

    task = bg.initialize_treatment_facilities.s(
        treatment_facilities=treatment_facilities.model_dump(),
        pre_validated=True,
        context=context,
    )
    return await run_task(request, task, "get_treatment_facility_parameters")


@router.get(
    "/treatment_facility/validate/{task_id}",
    tags=["treatment_facility", "validate"],
    response_model=TreatmentFacilitiesResponse,
    response_class=ORJSONResponse,
)
async def get_treatment_facility_parameters(
    request: Request, task_id: str
) -> dict[str, Any]:
    task = bg.initialize_treatment_facilities.AsyncResult(task_id, app=router)
    return await standard_json_response(
        request, task, "get_treatment_facility_parameters"
    )
