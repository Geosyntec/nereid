from typing import Optional, Any, List
from pydantic import BaseModel, Field

from nereid.api.api_v1.models.response_models import JSONAPIResponse

## Network Request Models

# https://github.com/jsongraph/json-graph-specification
class Node(BaseModel):
    id: str
    metadata: Optional[dict] = {}


class Edge(BaseModel):
    metadata: Optional[dict] = {}
    source: str
    target: str


class Graph(BaseModel):
    directed: Optional[bool] = False
    edges: List[Edge]
    type_: Optional[str] = Field(None, alias="type")
    label: Optional[str]
    metadata: Optional[dict]
    nodes: Optional[List[Node]]


class Nodes(BaseModel):
    nodes: List[Node]


class SubgraphNodes(BaseModel):
    subgraph_nodes: List[Nodes]


class NetworkValidation(BaseModel):
    isvalid: bool
    node_cycles: Optional[List[List[str]]]
    edge_cycles: Optional[List[List[str]]]
    multiple_out_edges: Optional[List[List[str]]]
    duplicate_edges: Optional[List[List[str]]]


## Network Response Models


class NetworkValidationResponse(JSONAPIResponse):
    data: Optional[NetworkValidation] = None


class SubgraphResponse(JSONAPIResponse):
    data: Optional[SubgraphNodes] = None
