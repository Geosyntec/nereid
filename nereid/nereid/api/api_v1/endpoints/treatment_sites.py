from typing import Dict, Any, List, Tuple

from fastapi import APIRouter, Body, Depends

# from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

# import nereid.bg_worker as bg
from nereid.src.treatment_site.tasks import initialize_treatment_sites
from nereid.api.api_v1.utils import standard_json_response, run_task, get_valid_context
from nereid.api.api_v1.models.treatment_site_models import (
    TreatmentSites,
    TreatmentSiteResponse,
)

router = APIRouter()


@router.post(
    "/treatment_site/validate",
    tags=["treatment_site", "validate"],
    response_model=TreatmentSiteResponse,
    response_class=ORJSONResponse,
)
async def initialize_treatment_site(
    treatment_sites: TreatmentSites = Body(
        ...,
        example={
            "treatment_sites": [
                {
                    "node_id": "WQMP-1a-tmnt",
                    "facility_type": "bioretention",
                    "area_pct": 75,
                    "captured_pct": 80,
                    "retained_pct": 10,
                },
                {
                    "node_id": "WQMP-1a-tmnt",
                    "facility_type": "nt",
                    "area_pct": 25,
                    "captured_pct": 0,
                    "retained_pct": 0,
                },
                {
                    "node_id": "WQMP-1b-tmnt",
                    "facility_type": "bioretention",
                    "area_pct": 75,
                    "captured_pct": 50,
                    "retained_pct": 10,
                },
                {
                    "node_id": "WQMP-1b-tmnt",
                    "facility_type": "nt",
                    "area_pct": 25,
                    "captured_pct": 0,
                    "retained_pct": 0,
                },
            ]
        },
    ),
    context: dict = Depends(get_valid_context),
) -> Dict[str, Any]:

    return dict(
        data=initialize_treatment_sites(treatment_sites.dict(), context=context)
    )

    # task = bg.background_initialize_treatment_facilities.s(
    #     treatment_facilities=treatment_facilities.dict(),
    #     pre_validated=True,
    #     context=context,
    # )
    # return run_task(
    #     task=task, router=router, get_route="get_treatment_facility_parameters"
    # )
