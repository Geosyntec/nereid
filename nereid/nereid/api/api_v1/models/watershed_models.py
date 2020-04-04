from typing import Optional, List
from pydantic import BaseModel

from nereid.api.api_v1.models.response_models import JSONAPIResponse
from nereid.api.api_v1.models.network_models import Graph
from nereid.api.api_v1.models.land_surface_models import LandSurface
from nereid.api.api_v1.models.treatment_facility_models import STRUCTURAL_FACILITY_TYPE
from nereid.api.api_v1.models.treatment_site_models import TreatmentSite
from nereid.api.api_v1.models.results_models import Result, PreviousResult


## Request Model


class Watershed(BaseModel):
    graph: Graph
    land_surfaces: List[LandSurface]
    treatment_facilities: Optional[List[STRUCTURAL_FACILITY_TYPE]] = []
    treatment_sites: Optional[List[TreatmentSite]] = []
    previous_results: Optional[List[PreviousResult]] = []


## Response Models


class WatershedResults(BaseModel):
    results: List[Result]
    errors: Optional[List[str]] = None


class WatershedResponse(JSONAPIResponse):
    data: Optional[WatershedResults] = None
