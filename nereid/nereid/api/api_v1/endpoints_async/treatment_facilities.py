from typing import Any, Dict, Tuple

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid._compat import model_construct, model_dump
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
) -> Tuple[TreatmentFacilities, Dict[str, Any]]:
    unvalidated_data = model_dump(treatment_facilities)["treatment_facilities"]

    valid_models = validate_treatment_facility_models(unvalidated_data, context)

    return (
        model_construct(TreatmentFacilities, treatment_facilities=valid_models),
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
    tmnt_facility_req: Tuple[TreatmentFacilities, Dict[str, Any]] = Depends(
        validate_facility_request
    ),
) -> Dict[str, Any]:
    treatment_facilities, context = tmnt_facility_req

    task = bg.initialize_treatment_facilities.s(
        treatment_facilities=model_dump(treatment_facilities),
        pre_validated=True,
        context=context,
    )
    return run_task(request, task, "get_treatment_facility_parameters")


@router.get(
    "/treatment_facility/validate/{task_id}",
    tags=["treatment_facility", "validate"],
    response_model=TreatmentFacilitiesResponse,
    response_class=ORJSONResponse,
)
async def get_treatment_facility_parameters(
    request: Request, task_id: str
) -> Dict[str, Any]:
    task = bg.initialize_treatment_facilities.AsyncResult(task_id, app=router)
    return standard_json_response(request, task, "get_treatment_facility_parameters")
