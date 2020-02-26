from typing import Dict, Any

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

import nereid.bg_worker as bg
from nereid.api.api_v1.utils import (
    standard_json_response,
    run_task_by_name,
    get_valid_context,
)
from nereid.api.api_v1.models.land_surface_models import (
    LandSurfaces,
    LandSurfaceResponse,
)


router = APIRouter()


@router.post(
    "/land_surface/loading",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
)
async def calculate_loading(
    land_surfaces: LandSurfaces = Body(
        ...,
        example={
            "land_surfaces": [
                {
                    "node_id": "1",
                    "surface_key": "10101200-RESMF-C-5",
                    "area_acres": 1.834347898661638,
                    "imp_area_acres": 1.430224547955745,
                },
                {
                    "node_id": "0",
                    "surface_key": "10101200-OSDEV-A-0",
                    "area_acres": 4.458327528535912,
                    "imp_area_acres": 0.4457209193544626,
                },
                {
                    "node_id": "0",
                    "surface_key": "10102000-IND-A-10",
                    "area_acres": 3.337086111390218,
                    "imp_area_acres": 0.47675887386582366,
                },
                {
                    "node_id": "0",
                    "surface_key": "10101200-COMM-C-0",
                    "area_acres": 0.5641157902710026,
                    "imp_area_acres": 0.40729090799199347,
                },
                {
                    "node_id": "1",
                    "surface_key": "20101000-TRANS-C-5",
                    "area_acres": 0.007787658410143283,
                    "imp_area_acres": 0.007727004694355631,
                },
            ]
        },
    ),
    details: bool = False,
    context: dict = Depends(get_valid_context),
) -> Dict[str, Any]:

    land_surfaces_req = land_surfaces.dict(by_alias=True)
    args = (land_surfaces_req, details, context)
    response = run_task_by_name(
        taskname="land_surface_loading",
        router=router,
        args=args,
        get_route="get_land_surface_loading_result",
        force_foreground=False,
    )

    return response


@router.get(
    "/land_surface/loading/{task_id}",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
)
async def get_land_surface_loading_result(task_id: str) -> Dict[str, Any]:
    task = bg.background_land_surface_loading.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_land_surface_loading_result")
