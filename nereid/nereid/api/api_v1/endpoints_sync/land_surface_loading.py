from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

from nereid.api.utils import get_valid_context
from nereid.models.land_surface_models import (
    LandSurfaceResponse,
    LandSurfaces,
)
from nereid.src import tasks

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
) -> dict[str, Any]:
    land_surfaces_req = land_surfaces.model_dump(by_alias=True)

    data = tasks.land_surface_loading(
        land_surfaces=land_surfaces_req, details=details, context=context
    )

    return {"data": data}
