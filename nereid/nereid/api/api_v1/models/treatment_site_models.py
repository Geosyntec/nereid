from typing import List, Optional

from pydantic import BaseModel, Field

from nereid.api.api_v1.models.response_models import JSONAPIResponse
from nereid.api.api_v1.models.treatment_facility_models import SimpleFacilityBase

## Treatment Site Request Models


class TreatmentSite(SimpleFacilityBase):
    area_pct: float = Field(0.0, le=100.0, ge=0.0)
    retained_pct: float = Field(0.0, le=100.0, ge=0.0)
    eliminate_all_dry_weather_flow_override: bool = False


class TreatmentSites(BaseModel):
    treatment_sites: List[TreatmentSite]

    class Config:
        schema_extra = {
            "example": {
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
        }


## Treatment Site Response Models


class TreatmentSiteGroupBase(TreatmentSite):
    class Config:
        extra = "allow"


class TreatmentSiteGroup(BaseModel):
    node_id: str
    node_type: str
    treatment_facilities: List[TreatmentSiteGroupBase]
    errors: Optional[List[str]] = None

    class Config:
        extra = "allow"


class TreatmentSiteGroups(BaseModel):
    treatment_sites: List[TreatmentSiteGroup]


class TreatmentSiteResponse(JSONAPIResponse):
    data: Optional[TreatmentSiteGroups] = None
