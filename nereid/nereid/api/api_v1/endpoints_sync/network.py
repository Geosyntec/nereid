from typing import Any, Dict

from fastapi import APIRouter, Body, Query
from fastapi.responses import ORJSONResponse

from nereid._compat import model_dump
from nereid.api.api_v1.models import network_models
from nereid.src import tasks

router = APIRouter()


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def validate_network(
    graph: network_models.Graph = Body(
        ..., examples=network_models.GraphExamples  # type: ignore[arg-type]
    ),
) -> Dict[str, Any]:
    g: Dict[str, Any] = model_dump(graph, by_alias=True)
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
) -> Dict[str, Any]:
    kwargs = model_dump(subgraph_req, by_alias=True)
    data = tasks.network_subgraphs(**kwargs)
    return {"data": data}


@router.post(
    "/network/solution_sequence",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def network_solution_sequence(
    graph: network_models.Graph = Body(
        ..., examples=network_models.GraphExamples  # type: ignore[arg-type]
    ),
    min_branch_size: int = Query(4),
) -> Dict[str, Any]:
    g = model_dump(graph, by_alias=True)
    data = tasks.solution_sequence(graph=g, min_branch_size=min_branch_size)
    return {"data": data}
