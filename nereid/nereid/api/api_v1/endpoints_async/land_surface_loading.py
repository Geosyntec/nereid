from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.api_v1.async_utils import run_task, standard_json_response
from nereid.api.api_v1.models.land_surface_models import (
    LandSurfaceResponse,
    LandSurfaces,
)
from nereid.api.api_v1.utils import get_valid_context

router = APIRouter()


@router.post(
    "/land_surface/loading",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
    response_class=ORJSONResponse,
)
async def calculate_loading(
    request: Request,
    land_surfaces: LandSurfaces = Body(...),
    details: bool = False,
    context: dict = Depends(get_valid_context),
) -> dict[str, Any]:
    land_surfaces_req = land_surfaces.model_dump(by_alias=True)

    task = bg.land_surface_loading.s(
        land_surfaces=land_surfaces_req, details=details, context=context
    )

    return await run_task(request, task, "get_land_surface_loading_result")


@router.get(
    "/land_surface/loading/{task_id}",
    tags=["land_surface", "loading"],
    response_model=LandSurfaceResponse,
    response_class=ORJSONResponse,
)
async def get_land_surface_loading_result(
    request: Request,
    task_id: str,
) -> dict[str, Any]:
    task = bg.land_surface_loading.AsyncResult(task_id, app=router)
    return await standard_json_response(
        request, task, "get_land_surface_loading_result"
    )
