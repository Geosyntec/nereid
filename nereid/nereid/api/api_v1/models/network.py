from typing import List, Optional

from pydantic import BaseModel, validator

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
    type: Optional[str]
    label: Optional[str]
    metadata: Optional[dict]
    nodes: Optional[List[Node]]


# class Network(BaseModel):
#     graph: Graph


class Nodes(BaseModel):
    nodes: List[Node]


class SubgraphNodes(BaseModel):
    subgraph_nodes: List[Nodes]


class SubgraphRequest(BaseModel):
    graph: Graph
    nodes: List[Node]
