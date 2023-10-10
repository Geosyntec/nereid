from typing import Annotated

from pydantic import BaseModel, Field, StrictStr

from nereid.api.api_v1.models.response_models import JSONAPIResponse

## Network Request Models

Metadata = Annotated[dict, Field(default_factory=dict)]


# https://github.com/jsongraph/json-graph-specification
class Node(BaseModel):
    id_: StrictStr | None = Field(None, alias="id")
    metadata: Metadata


class Edge(BaseModel):
    source: StrictStr
    target: StrictStr
    metadata: Metadata


GraphExamples = {
    "simple": {
        "summary": "A normal simple graph",
        "description": "This should work correctly.",
        "value": {
            "directed": True,
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        },
    },
    "simple edgelist": {
        "summary": "Bare minimum graph definition.",
        "description": "Graph will be both `directed=True` and `multigraph=True` by default.",
        "value": {
            "edges": [{"source": "A", "target": "B"}],
        },
    },
    "duplicate edge": {
        "summary": "Graph with duplicate edge.",
        "description": "This graph will error because of the duplicate edge.",
        "value": {
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "A", "target": "B"},
            ],
        },
    },
    "multiple out edges": {
        "summary": "Graph with multiple out edges.",
        "description": "This graph will error because of A points to both B and C.",
        "value": {
            "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "A", "target": "C"},
            ],
        },
    },
    "cycle": {
        "summary": "Graph with a cycle.",
        "description": "This graph will error because there is a cycle.",
        "value": {
            "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "B", "target": "C"},
                {"source": "C", "target": "A"},
            ],
        },
    },
    "complex": {
        "summary": "A complex example",
        "description": "A complex graph that works correctly.",
        "value": {
            "directed": True,
            "edges": [
                {"source": "3", "target": "1"},
                {"source": "5", "target": "3"},
                {"source": "7", "target": "1"},
                {"source": "9", "target": "1"},
                {"source": "11", "target": "1"},
                {"source": "13", "target": "3"},
                {"source": "15", "target": "9"},
                {"source": "17", "target": "7"},
                {"source": "19", "target": "17"},
                {"source": "21", "target": "15"},
                {"source": "23", "target": "1"},
                {"source": "25", "target": "5"},
                {"source": "27", "target": "11"},
                {"source": "29", "target": "7"},
                {"source": "31", "target": "11"},
                {"source": "33", "target": "25"},
                {"source": "35", "target": "23"},
                {"source": "4", "target": "2"},
                {"source": "6", "target": "2"},
                {"source": "8", "target": "6"},
                {"source": "10", "target": "2"},
                {"source": "12", "target": "2"},
                {"source": "14", "target": "2"},
                {"source": "16", "target": "12"},
                {"source": "18", "target": "12"},
                {"source": "20", "target": "8"},
                {"source": "22", "target": "6"},
                {"source": "24", "target": "12"},
            ],
        },
    },
}


class Graph(BaseModel):
    edges: list[Edge]
    nodes: list[Node] | None = []
    directed: bool | None = True
    multigraph: bool | None = True
    type_: str | None = Field(None, alias="type")
    label: str | None = None
    metadata: Metadata


class Nodes(BaseModel):
    nodes: list[Node]


class SubgraphNodes(BaseModel):
    subgraph_nodes: list[Nodes]


class SubgraphRequest(BaseModel):
    graph: Graph
    nodes: list[Node]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "graph": GraphExamples["complex"]["value"],
                    "nodes": [{"id": "3"}, {"id": "29"}, {"id": "18"}],
                }
            ],
        }
    }


class SeriesSequence(BaseModel):
    series: list[Nodes]


class ParallelSeriesSequence(BaseModel):
    parallel: list[SeriesSequence]


class SolutionSequence(BaseModel):
    solution_sequence: ParallelSeriesSequence


class NetworkValidation(BaseModel):
    isvalid: bool
    node_cycles: list[list[str]] | None = []
    edge_cycles: list[list[str]] | None = []
    multiple_out_edges: list[list[str]] | None = []
    duplicate_edges: list[list[str]] | None = []


## Network Response Models


class NetworkValidationResponse(JSONAPIResponse):
    data: NetworkValidation | None = None


class SubgraphResponse(JSONAPIResponse):
    data: SubgraphNodes | None = None


class SolutionSequenceResponse(JSONAPIResponse):
    data: SolutionSequence | None = None
