from typing import List, Optional

from pydantic import BaseModel, Field

from nereid._compat import PYDANTIC_V2
from nereid.api.api_v1.models.response_models import JSONAPIResponse

## Land Surface Request Models


class LandSurface(BaseModel):
    node_id: str
    surface_key: str = Field(..., examples=["104506-RESSFH-B-5"])
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
    land_surfaces: List[LandSurface]

    if PYDANTIC_V2:
        model_config = {"json_schema_extra": {"examples": [LS_EXAMPLE]}}
    else:

        class Config:
            schema_extra = {"examples": [LS_EXAMPLE]}


## Land Surface Response Models


class LandSurfaceBase(BaseModel):
    node_type: str = "land_surface"

    if PYDANTIC_V2:
        model_config = {"extra": "allow"}
    else:

        class Config:
            extra = "allow"


class LandSurfaceSummary(LandSurfaceBase):
    node_id: str
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
    node_id: str
    surface_key: str
    area_acres: float
    imp_area_acres: float
    surface_id: str
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
    summary: Optional[List[LandSurfaceSummary]] = None
    details: Optional[List[LandSurfaceDetails]] = None
    errors: Optional[List[str]] = None


class LandSurfaceResponse(JSONAPIResponse):
    data: Optional[LandSurfaceResults] = None
