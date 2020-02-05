from typing import Optional, Any, List
from pydantic import BaseModel, AnyHttpUrl

from nereid.src.network.models import SubgraphNodes, NetworkValidation


class JSONAPIResponse(BaseModel):
    status: str
    task_id: Optional[str] = None
    result_route: Optional[str] = None
    data: Optional[Any] = None


class ReferenceData(BaseModel):
    state: str
    region: str
    file: str
    filedata: Any


class ReferenceDataResponse(JSONAPIResponse):
    data: Optional[ReferenceData] = None


class NetworkValidationResponse(JSONAPIResponse):
    data: Optional[NetworkValidation] = None


class SubgraphResponse(JSONAPIResponse):
    data: Optional[SubgraphNodes] = None
