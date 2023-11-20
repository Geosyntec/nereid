from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

from nereid.api.utils import get_valid_context
from nereid.models.treatment_site_models import (
    TreatmentSiteResponse,
    TreatmentSites,
)
from nereid.src import tasks

router = APIRouter()


@router.post(
    "/treatment_site/validate",
    tags=["treatment_site", "validate"],
    response_model=TreatmentSiteResponse,
    response_class=ORJSONResponse,
)
async def initialize_treatment_site(
    treatment_sites: TreatmentSites = Body(...),
    context: dict = Depends(get_valid_context),
) -> dict[str, Any]:
    data = tasks.initialize_treatment_sites(
        treatment_sites.model_dump(), context=context
    )

    return {"data": data}
