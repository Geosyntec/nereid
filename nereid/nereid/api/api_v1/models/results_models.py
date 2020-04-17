from typing import List

from pydantic import BaseModel


class Result(BaseModel):
    node_id: str

    class Config:
        extra = "allow"


class PreviousResult(Result):
    pass


class PreviousResults(BaseModel):
    previous_results: List[PreviousResult]
