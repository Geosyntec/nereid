from typing import Any

from pydantic import BaseModel


class JSONAPIResponse(BaseModel):
    status: str = "SUCCESS"
    task_id: str | None = None
    result_route: str | None = None
    data: Any | None = None
