from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


class Node(BaseModel):
    node_id: Annotated[str, Field(...), BeforeValidator(str)]
