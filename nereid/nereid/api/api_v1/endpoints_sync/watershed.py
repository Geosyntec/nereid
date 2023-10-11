from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.utils import get_valid_context
from nereid.models.treatment_facility_models import (
    validate_treatment_facility_models,
)
from nereid.models.watershed_models import Watershed, WatershedResponse
from nereid.src import tasks

router = APIRouter()


def validate_watershed_request(
    watershed_req: Watershed,
    context: dict = Depends(get_valid_context),
) -> tuple[dict[str, Any], dict[str, Any]]:
    watershed: dict[str, Any] = watershed_req.model_dump(by_alias=True)

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
    watershed_pkg: tuple[dict[str, Any], dict[str, Any]] = Depends(
        validate_watershed_request
    ),
) -> dict[str, Any]:
    watershed, context = watershed_pkg

    data = tasks.solve_watershed(
        watershed=watershed, treatment_pre_validated=True, context=context
    )
    return {"data": data}
