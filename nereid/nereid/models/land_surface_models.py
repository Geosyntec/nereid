from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from nereid.models.node import Node
from nereid.models.response_models import JSONAPIResponse

## Land Surface Request Models


class LandSurface(Node):
    surface_key: Annotated[
        str, Field(..., examples=["104506-RESSFH-B-5"]), BeforeValidator(str)
    ]
    area_acres: float = Field(..., gt=0.0)
    imp_area_acres: float = Field(..., ge=0.0)


LS_EXAMPLE = {
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
    ]
}


class LandSurfaces(BaseModel):
    land_surfaces: list[LandSurface]

    model_config = {"json_schema_extra": {"examples": [LS_EXAMPLE]}}


## Land Surface Response Models


class LandSurfaceBase(Node):
    node_type: str = "land_surface"

    model_config = {"extra": "allow"}


class LandSurfaceSummary(LandSurfaceBase):
    area_acres: float
    imp_area_acres: float
    perv_area_acres: float
    imp_ro_volume_cuft: float
    perv_ro_volume_cuft: float
    runoff_volume_cuft: float  # required for watershed solution
    eff_area_acres: float  # required for watershed solution
    land_surfaces_count: float
    imp_pct: float
    ro_coeff: float


class LandSurfaceDetails(LandSurfaceBase):
    surface_key: Annotated[str, Field(...), BeforeValidator(str)]
    area_acres: float
    imp_area_acres: float
    surface_id: Annotated[str, Field(...), BeforeValidator(str)]
    perv_ro_depth_inches: float
    imp_ro_depth_inches: float
    perv_ro_coeff: float
    imp_ro_coeff: float
    perv_area_acres: float
    imp_area_sqft: float
    perv_area_sqft: float
    imp_ro_depth_feet: float
    perv_ro_depth_feet: float
    imp_ro_volume_cuft: float
    perv_ro_volume_cuft: float
    runoff_volume_cuft: float
    imp_eff_area_acres: float
    perv_eff_area_acres: float
    eff_area_acres: float


class LandSurfaceResults(BaseModel):
    summary: list[LandSurfaceSummary] | None = None
    details: list[LandSurfaceDetails] | None = None
    errors: list[str] | None = None


class LandSurfaceResponse(JSONAPIResponse):
    data: LandSurfaceResults | None = None
