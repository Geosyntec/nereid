from typing import Any

from pydantic import BaseModel

from nereid.models.response_models import JSONAPIResponse


class ReferenceData(BaseModel):
    state: str
    region: str
    file: str
    filedata: Any


class ReferenceDataResponse(JSONAPIResponse):
    data: ReferenceData | None = None
