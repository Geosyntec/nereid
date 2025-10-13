from typing import Any

import networkx as nx
from fastapi import APIRouter, Body, Query
from fastapi.responses import ORJSONResponse, StreamingResponse

from nereid.models import network_models
from nereid.src import tasks
from nereid.src.network.algorithms import parallel_sequential_subgraph_nodes
from nereid.src.network.utils import graph_factory, thin_graph_dict

router = APIRouter()


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def validate_network(
    graph: network_models.Graph = Body(
        ...,
        openapi_examples=network_models.GraphExamples,
    ),
) -> dict[str, Any]:
    g: dict[str, Any] = graph.model_dump(by_alias=True)
    data = tasks.validate_network(graph=g)
    return {"data": data}


@router.post(
    "/network/subgraph",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def subgraph_network(
    subgraph_req: network_models.SubgraphRequest = Body(...),
) -> dict[str, Any]:
    kwargs = subgraph_req.model_dump(by_alias=True)
    data = tasks.network_subgraphs(**kwargs)
    return {"data": data}


@router.post(
    "/network/subgraph/img",
    tags=["network", "subgraph"],
)
async def subgraph_network_as_img(
    subgraph_req: network_models.SubgraphRequest = Body(...),
    npi: float = Query(4.0),
) -> StreamingResponse:
    kwargs = subgraph_req.model_dump(by_alias=True)
    graph_dict = kwargs["graph"]
    nodes = kwargs["nodes"]

    res = tasks.network_subgraphs(graph_dict, nodes)
    g = graph_factory(res["graph"])

    fig = tasks.render_subgraphs(
        g,
        request_nodes=res["requested_nodes"],
        subgraph_nodes=res["subgraph_nodes"],
        npi=npi,
    )

    svg = tasks.fig_to_image(fig, format="jpg")
    return StreamingResponse(svg, media_type="image/jpg")


@router.post(
    "/network/solution_sequence",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def network_solution_sequence(
    graph: network_models.ValidGraph = Body(
        ...,
        openapi_examples=network_models.GraphExamples,
    ),
    min_branch_size: int = Query(4),
) -> dict[str, Any]:
    g = graph.model_dump(by_alias=True)
    data = tasks.solution_sequence(graph=g, min_branch_size=min_branch_size)
    return {"data": data}


@router.post("/network/solution_sequence/img", tags=["network", "sequence"])
async def network_solution_sequence_as_img(
    graph: network_models.ValidGraph = Body(
        ...,
        openapi_examples=network_models.GraphExamples,
    ),
    min_branch_size: int = Query(4),
    npi: float = Query(4.0),
) -> StreamingResponse:
    _g = thin_graph_dict(graph.model_dump(by_alias=True))
    g = nx.DiGraph(graph_factory(_g))

    solution_sequence = parallel_sequential_subgraph_nodes(g, min_branch_size)

    fig = tasks.render_solution_sequence(
        g, solution_sequence=solution_sequence, npi=npi
    )

    svg = tasks.fig_to_image(fig, format="jpg")
    return StreamingResponse(svg, media_type="image/jpg")
