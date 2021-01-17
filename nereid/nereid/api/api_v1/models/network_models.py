from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from nereid.api.api_v1.models.response_models import JSONAPIResponse

## Network Request Models

# https://github.com/jsongraph/json-graph-specification
class Node(BaseModel):
    id_: Optional[StrictStr] = Field(None, alias="id")
    metadata: Optional[dict] = {}


class Edge(BaseModel):
    source: StrictStr
    target: StrictStr
    metadata: Optional[dict] = {}


class Graph(BaseModel):
    edges: List[Edge]
    nodes: Optional[List[Node]]
    directed: Optional[bool] = False
    multigraph: Optional[bool] = True
    type_: Optional[str] = Field(None, alias="type")
    label: Optional[str]
    metadata: Optional[dict]


class Nodes(BaseModel):
    nodes: List[Node]


class SubgraphNodes(BaseModel):
    subgraph_nodes: List[Nodes]


class SeriesSequence(BaseModel):
    series: List[Nodes]


class ParallelSeriesSequence(BaseModel):
    parallel: List[SeriesSequence]


class SolutionSequence(BaseModel):
    solution_sequence: ParallelSeriesSequence


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


class SolutionSequenceResponse(JSONAPIResponse):
    data: Optional[SolutionSequence] = None
