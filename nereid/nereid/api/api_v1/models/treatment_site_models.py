from typing import List, Optional

from pydantic import BaseModel

from nereid.api.api_v1.models.response_models import JSONAPIResponse

## Treatment Site Request Models


class TreatmentSite(BaseModel):
    node_id: str
    facility_type: str
    area_pct: float
    captured_pct: float
    retained_pct: float
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
