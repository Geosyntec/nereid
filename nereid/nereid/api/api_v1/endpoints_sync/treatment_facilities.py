from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

from nereid._compat import model_construct, model_dump
from nereid.api.api_v1.models.treatment_facility_models import (
    TreatmentFacilities,
    TreatmentFacilitiesResponse,
    validate_treatment_facility_models,
)
from nereid.api.api_v1.utils import get_valid_context
from nereid.src import tasks

router = APIRouter()


def validate_facility_request(
    treatment_facilities: TreatmentFacilities = Body(...),
    context: dict = Depends(get_valid_context),
) -> tuple[TreatmentFacilities, dict[str, Any]]:
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
    tmnt_facility_req: tuple[TreatmentFacilities, dict[str, Any]] = Depends(
        validate_facility_request
    ),
) -> dict[str, Any]:
    treatment_facilities, context = tmnt_facility_req

    data = tasks.initialize_treatment_facilities(
        treatment_facilities=model_dump(treatment_facilities),
        pre_validated=True,
        context=context,
    )
    return {"data": data}
