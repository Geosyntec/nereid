from typing import Any, Dict, Tuple

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.models.treatment_facility_models import (
    validate_treatment_facility_models,
)
from nereid.api.api_v1.models.watershed_models import Watershed, WatershedResponse
from nereid.api.api_v1.utils import get_valid_context
from nereid.src import tasks

router = APIRouter()


def validate_watershed_request(
    watershed_req: Watershed,
    context: dict = Depends(get_valid_context),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:

    watershed: Dict[str, Any] = watershed_req.dict(by_alias=True)

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
    watershed_pkg: Tuple[Dict[str, Any], Dict[str, Any]] = Depends(
        validate_watershed_request
    ),
) -> Dict[str, Any]:
    watershed, context = watershed_pkg

    data = tasks.solve_watershed(
        watershed=watershed, treatment_pre_validated=True, context=context
    )
    return {"data": data}
