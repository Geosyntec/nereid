from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.models.treatment_site_models import (
    TreatmentSiteResponse,
    TreatmentSites,
)
from nereid.api.api_v1.utils import get_valid_context
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
) -> Dict[str, Any]:
    data = tasks.initialize_treatment_sites(treatment_sites.dict(), context=context)

    return {"data": data}
