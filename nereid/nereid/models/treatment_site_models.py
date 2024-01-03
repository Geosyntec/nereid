from pydantic import BaseModel, Field

from nereid.models.response_models import JSONAPIResponse
from nereid.models.treatment_facility_models import SimpleFacilityBase

## Treatment Site Request Models


class TreatmentSite(SimpleFacilityBase):
    area_pct: float = Field(0.0, le=100.0, ge=0.0)
    retained_pct: float = Field(0.0, le=100.0, ge=0.0)
    eliminate_all_dry_weather_flow_override: bool = False


TMNT_SITES_EXAMPLE: dict = {
    "treatment_sites": [
        {
            "node_id": "WQMP-1a-tmnt",
            "facility_type": "bioretention",
            "area_pct": 75,
            "captured_pct": 80,
            "retained_pct": 10,
        },
        {
            "node_id": "WQMP-1a-tmnt",
            "facility_type": "nt",
            "area_pct": 25,
            "captured_pct": 0,
            "retained_pct": 0,
        },
        {
            "node_id": "WQMP-1b-tmnt",
            "facility_type": "bioretention",
            "area_pct": 75,
            "captured_pct": 50,
            "retained_pct": 10,
        },
        {
            "node_id": "WQMP-1b-tmnt",
            "facility_type": "nt",
            "area_pct": 25,
            "captured_pct": 0,
            "retained_pct": 0,
        },
    ]
}


class TreatmentSites(BaseModel):
    treatment_sites: list[TreatmentSite]

    model_config = {"json_schema_extra": {"example": TMNT_SITES_EXAMPLE}}


## Treatment Site Response Models


class TreatmentSiteGroupBase(TreatmentSite):
    model_config = {"extra": "allow"}


class TreatmentSiteGroup(BaseModel):
    node_id: str
    node_type: str
    treatment_facilities: list[TreatmentSiteGroupBase]
    errors: list[str] | None = None

    model_config = {"extra": "allow"}


class TreatmentSiteGroups(BaseModel):
    treatment_sites: list[TreatmentSiteGroup]


class TreatmentSiteResponse(JSONAPIResponse):
    data: TreatmentSiteGroups | None = None
