from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from nereid.core.utils import get_request_context
from nereid.api.utils import standard_json_response
from nereid.api.api_v1.models.land_surface_models import (
    LandSurfaces,
    LandSurfaceResponse,
)
import nereid.bg_worker as bg


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
                    "node_id": "5",
                    "surface_key": "401070-TRANS-B-10",
                    "area_acres": 6.02,
                    "imp_area_acres": 3.28,
                },
                {
                    "node_id": "5",
                    "surface_key": "401070-OSAGNI-B-10",
                    "area_acres": 3.84,
                    "imp_area_acres": 1.14,
                },
                {
                    "node_id": "8",
                    "surface_key": "401070-TRANS-D-5",
                    "area_acres": 2.72,
                    "imp_area_acres": 1.30,
                },
            ]
        },
        # embed=True,
    ),
    details: bool = False,
    state: str = "state",
    region: str = "region",
):

    land_surfaces_req = land_surfaces.dict(by_alias=True)
    req_ctxt = get_request_context(state=state, region=region)

    task = bg.background_land_surface_loading.apply_async(
        args=(land_surfaces_req, jsonable_encoder(details), req_ctxt)
    )

    return standard_json_response(task, router, "get_land_surface_loading_result")


@router.get(
    "/land_surface/loading/{task_id}",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
)
async def get_land_surface_loading_result(task_id: str):
    task = bg.background_land_surface_loading.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_land_surface_loading_result")
