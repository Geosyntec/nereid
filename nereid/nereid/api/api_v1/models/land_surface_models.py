from typing import List, Optional

from pydantic import BaseModel, Field

from nereid.api.api_v1.models.response_models import JSONAPIResponse

## Land Surface Request Models


class LandSurface(BaseModel):
    node_id: str
    surface_key: str = Field(..., example="104506-RESSFH-B-5")
    area_acres: float
    imp_area_acres: float


class LandSurfaces(BaseModel):
    land_surfaces: List[LandSurface]


## Land Surface Response Models


class LandSurfaceBase(BaseModel):
    class Config:
        extra = "allow"


class LandSurfaceSummary(LandSurfaceBase):
    node_id: str
    area_acres: float
    imp_area_acres: float
    perv_area_acres: float
    imp_ro_volume_cuft: float
    perv_ro_volume_cuft: float
    runoff_volume_cuft: float
    eff_area_acres: float
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
    subbasin: str
    land_use: str
    soil: str
    slope: str
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
    summary: List[LandSurfaceSummary]
    details: Optional[List[LandSurfaceDetails]] = None
    errors: Optional[List[str]] = None


class LandSurfaceResponse(JSONAPIResponse):
    data: Optional[LandSurfaceResults] = None
