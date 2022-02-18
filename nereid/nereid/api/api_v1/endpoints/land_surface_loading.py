from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.models.land_surface_models import (
    LandSurfaceResponse,
    LandSurfaces,
)
from nereid.api.api_v1.utils import get_valid_context, run_task, standard_json_response

router = APIRouter()


@router.post(
    "/land_surface/loading",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
    response_class=ORJSONResponse,
)
async def calculate_loading(
    land_surfaces: LandSurfaces = Body(...),
    details: bool = False,
    context: dict = Depends(get_valid_context),
) -> Dict[str, Any]:

    land_surfaces_req = land_surfaces.dict(by_alias=True)

    task = bg.land_surface_loading.s(
        land_surfaces=land_surfaces_req, details=details, context=context
    )

    return run_task(
        task=task, router=router, get_route="get_land_surface_loading_result"
    )


@router.get(
    "/land_surface/loading/{task_id}",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
    response_class=ORJSONResponse,
)
async def get_land_surface_loading_result(task_id: str) -> Dict[str, Any]:
    task = bg.land_surface_loading.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_land_surface_loading_result")
