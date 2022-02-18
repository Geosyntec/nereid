from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.models.treatment_site_models import (
    TreatmentSiteResponse,
    TreatmentSites,
)
from nereid.api.api_v1.utils import get_valid_context

router = APIRouter()


@router.post(
    "/treatment_site/validate",
    tags=["treatment_site", "validate"],
    response_model=TreatmentSiteResponse,
    response_class=ORJSONResponse,
)
async def initialize_treatment_site(
    request: Request,
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
    treatment_sites = treatment_sites.dict()
    data = request.app.tasks.initialize_treatment_sites(
        treatment_sites, context=context
    )

    return {"data": data}
