from typing import Optional, Any
from pydantic import BaseModel


class JSONAPIResponse(BaseModel):
    status: str
    task_id: Optional[str] = None
    result_route: Optional[str] = None
    data: Optional[Any] = None
