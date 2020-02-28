from typing import Optional, Any
from pydantic import BaseModel

from nereid.api.api_v1.models.response_models import JSONAPIResponse


class ReferenceData(BaseModel):
    state: str
    region: str
    file: str
    filedata: Any


class ReferenceDataResponse(JSONAPIResponse):
    data: Optional[ReferenceData] = None
