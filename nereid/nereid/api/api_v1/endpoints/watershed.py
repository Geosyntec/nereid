from typing import Dict, Any, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.utils import get_valid_context, run_task, standard_json_response
from nereid.api.api_v1.models.watershed_models import Watershed, WatershedResponse
from nereid.api.api_v1.models.treatment_facility_models import (
    TreatmentFacilities,
    validate_treatment_facility_models,
)
from nereid.src.watershed.tasks import solve_watershed

router = APIRouter()


def validate_watershed_request(
    watershed_req: Watershed = Body(
        ...,
        example={
            "graph": {
                "directed": True,
                "nodes": [{"id": "A"}, {"id": "B"}],
                "edges": [{"source": "A", "target": "B"}],
            },
            "land_surfaces": [
                {
                    "node_id": "1",
                    "surface_key": "10101100-RESMF-A-5",
                    "area_acres": 1.834347898661638,
                    "imp_area_acres": 1.430224547955745,
                },
                {
                    "node_id": "0",
                    "surface_key": "10101100-OSDEV-A-0",
                    "area_acres": 4.458327528535912,
                    "imp_area_acres": 0.4457209193544626,
                },
                {
                    "node_id": "0",
                    "surface_key": "10101000-IND-A-10",
                    "area_acres": 3.337086111390218,
                    "imp_area_acres": 0.47675887386582366,
                },
                {
                    "node_id": "0",
                    "surface_key": "10101100-COMM-C-0",
                    "area_acres": 0.5641157902710026,
                    "imp_area_acres": 0.40729090799199347,
                },
                {
                    "node_id": "1",
                    "surface_key": "10101200-TRANS-C-5",
                    "area_acres": 0.007787658410143283,
                    "imp_area_acres": 0.007727004694355631,
                },
            ],
            "treatment_facilities": [
                {
                    "node_id": "ghlqRFuJxyDO",
                    "facility_type": "bioretention",
                    "ref_data_key": "10101200",
                    "design_storm_depth_inches": 0.18256140532417647,
                    "is_online": True,
                    "tributary_area_tc_min": 15,
                    "total_volume_cuft": 5800,
                    "retention_volume_cuft": 3500,
                    "area_sqft": 1300,
                    "media_filtration_rate_inhr": 12,
                    "hsg": "a",
                    "offline_diversion_rate_cfs": 6,
                }
            ],
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
            ],
        },
    ),
    context: dict = Depends(get_valid_context),
) -> Tuple[Dict[str, Any], Dict[str, Any]]:

    watershed: Dict[str, Any] = watershed_req.dict(by_alias=True)

    unvalidated_treatment_facilities = watershed["treatment_facilities"]
    valid_models = validate_treatment_facility_models(
        unvalidated_treatment_facilities, context
    )
    validated_treatment_facilities = TreatmentFacilities.construct(
        treatment_facilities=valid_models
    )
    watershed["treatment_facilities"] = validated_treatment_facilities.dict()[
        "treatment_facilities"
    ]

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

    task = bg.background_solve_watershed.s(
        watershed=watershed, treatment_pre_validated=True, context=context
    )
    return run_task(task=task, router=router, get_route="get_watershed_result")


@router.get(
    "/watershed/solve/{task_id}",
    tags=["watershed", "main"],
    response_model=WatershedResponse,
    response_class=ORJSONResponse,
)
async def get_watershed_result(task_id: str) -> Dict[str, Any]:
    task = bg.background_solve_watershed.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_watershed_result")
