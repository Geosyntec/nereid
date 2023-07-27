from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from fastapi.responses import ORJSONResponse

from nereid._compat import model_dump
from nereid.api.api_v1.models.land_surface_models import (
    LandSurfaceResponse,
    LandSurfaces,
)
from nereid.api.api_v1.utils import get_valid_context
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
) -> Dict[str, Any]:
    land_surfaces_req = model_dump(land_surfaces, by_alias=True)

    data = tasks.land_surface_loading(
        land_surfaces=land_surfaces_req, details=details, context=context
    )

    return {"data": data}
