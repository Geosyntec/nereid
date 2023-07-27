from typing import List

from pydantic import BaseModel

from nereid._compat import PYDANTIC_V2


class Result(BaseModel):
    node_id: str

    if PYDANTIC_V2:
        model_config = {"extra": "allow"}
    else:

        class Config:
            extra = "allow"


class PreviousResult(Result):
    pass


class PreviousResults(BaseModel):
    previous_results: List[PreviousResult]
