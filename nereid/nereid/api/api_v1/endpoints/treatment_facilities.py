from typing import Any, Dict, Tuple, Union

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.models.treatment_facility_models import (
    TreatmentFacilities,
    TreatmentFacilitiesResponse,
    TreatmentFacilitiesStrict,
    validate_treatment_facility_models,
)
from nereid.api.api_v1.utils import get_valid_context, run_task, standard_json_response

router = APIRouter()


def validate_facility_request(
    treatment_facilities: Union[TreatmentFacilities, TreatmentFacilitiesStrict] = Body(
        ...
    ),
    context: dict = Depends(get_valid_context),
) -> Tuple[TreatmentFacilities, Dict[str, Any]]:

    unvalidated_data = treatment_facilities.dict()["treatment_facilities"]

    valid_models = validate_treatment_facility_models(unvalidated_data, context)

    return (
        TreatmentFacilities.construct(treatment_facilities=valid_models),
        context,
    )


@router.post(
    "/treatment_facility/validate",
    tags=["treatment_facility", "validate"],
    response_model=TreatmentFacilitiesResponse,
    response_class=ORJSONResponse,
)
async def initialize_treatment_facility_parameters(
    tmnt_facility_req: Tuple[TreatmentFacilities, Dict[str, Any]] = Depends(
        validate_facility_request
    )
) -> Dict[str, Any]:

    treatment_facilities, context = tmnt_facility_req

    task = bg.background_initialize_treatment_facilities.s(
        treatment_facilities=treatment_facilities.dict(),
        pre_validated=True,
        context=context,
    )
    return run_task(
        task=task, router=router, get_route="get_treatment_facility_parameters"
    )


@router.get(
    "/treatment_facility/validate/{task_id}",
    tags=["treatment_facility", "validate"],
    response_model=TreatmentFacilitiesResponse,
    response_class=ORJSONResponse,
)
async def get_treatment_facility_parameters(task_id: str) -> Dict[str, Any]:
    task = bg.background_initialize_treatment_facilities.AsyncResult(
        task_id, app=router
    )
    return standard_json_response(task, router, "get_treatment_facility_parameters")
