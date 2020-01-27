from typing import List, Optional

from pydantic import BaseModel

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


class NetworkValidation(BaseModel):
    isvalid: bool
    node_cycles: Optional[List]
    edge_cycles: Optional[List]
    multiple_out_edges: Optional[List]
    duplicate_edges: Optional[List]
