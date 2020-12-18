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
        ...,
        example={
            "treatment_facilities": [
                {
                    "node_id": "nt-node-1",
                    "facility_type": "no_treatment",
                    "ref_data_key": "10101200",
                    "design_storm_depth_inches": 1.45,
                },
                {
                    "node_id": "oTmWdvoyRzya",
                    "facility_type": "dry_extended_detention",
                    "ref_data_key": "10101200",
                    "design_storm_depth_inches": 1.05,
                    "is_online": False,
                    "tributary_area_tc_min": 30,
                    "total_volume_cuft": 5500,
                    "retention_volume_cuft": 4400,
                    "area_sqft": 1600,
                    "treatment_drawdown_time_hr": 24 * 3,
                    "hsg": "d",
                    "offline_diversion_rate_cfs": 2.9,
                },
                {
                    "node_id": "aZicdXaYylsb",
                    "facility_type": "infiltration",
                    "ref_data_key": "10101200",
                    "design_storm_depth_inches": 0.44,
                    "is_online": False,
                    "tributary_area_tc_min": 25,
                    "total_volume_cuft": 6200,
                    "area_sqft": 2000,
                    "inf_rate_inhr": 3.5,
                    "offline_diversion_rate_cfs": 5,
                },
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
                },
                {
                    "node_id": "pDLdcSVxlOlT",
                    "facility_type": "biofiltration",
                    "ref_data_key": "20101000",
                    "design_storm_depth_inches": 0.95,
                    "is_online": False,
                    "tributary_area_tc_min": 40,
                    "total_volume_cuft": 4400,
                    "area_sqft": 1200,
                    "media_filtration_rate_inhr": 15,
                    "offline_diversion_rate_cfs": 6,
                },
                {
                    "node_id": "xVsEmNryLuzm",
                    "facility_type": "wet_detention",
                    "ref_data_key": "20101000",
                    "design_storm_depth_inches": 0.71,
                    "is_online": False,
                    "tributary_area_tc_min": 45,
                    "pool_volume_cuft": 5500,
                    "pool_drawdown_time_hr": 24 * 30,
                    "treatment_volume_cuft": 2500,
                    "treatment_drawdown_time_hr": 12,
                    "winter_demand_cfs": 0.05,
                    "summer_demand_cfs": 0.88,
                    "offline_diversion_rate_cfs": 4,
                },
            ]
        },
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
