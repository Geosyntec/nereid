from pydantic import BaseModel


class Result(BaseModel):
    node_id: str

    model_config = {"extra": "allow"}


class PreviousResult(Result):
    pass


class PreviousResults(BaseModel):
    previous_results: list[PreviousResult]
