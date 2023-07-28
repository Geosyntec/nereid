from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

from nereid._compat import model_dump
from nereid.api.api_v1.models.treatment_site_models import (
    TreatmentSiteResponse,
    TreatmentSites,
)
from nereid.api.api_v1.utils import get_valid_context
from nereid.src.treatment_site.tasks import initialize_treatment_sites

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
    data = initialize_treatment_sites(model_dump(treatment_sites), context=context)

    return {"data": data}

    # task = bg.background_initialize_treatment_facilities.s(
    #     treatment_facilities=treatment_facilities.dict(),
    #     pre_validated=True,
    #     context=context,
    # )
    # return run_task(
    #     task=task, router=router, get_route="get_treatment_facility_parameters"
    # )
