from typing import Any, Optional

from pydantic import BaseModel


class JSONAPIResponse(BaseModel):
    status: str = "SUCCESS"
    task_id: Optional[str] = None
    result_route: Optional[str] = None
    data: Optional[Any] = None
