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


class TreatmentSites(BaseModel):
    treatment_sites: List[TreatmentSite]


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
