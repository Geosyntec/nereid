from typing import Any, Dict, Union

from fastapi import APIRouter, Body, Query, Request
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates

from nereid.api.api_v1.models import network_models

router = APIRouter()
templates = Jinja2Templates(directory="nereid/api/templates")


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def validate_network(
    req: Request,
    graph: network_models.Graph = Body(
        ...,
        example={
            "directed": True,
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        },
    ),
) -> Dict[str, Any]:

    g: Dict[str, Any] = graph.dict(by_alias=True)
    data = req.app.tasks.validate_network(graph=g)
    return {"data": data}


@router.post(
    "/network/subgraph",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def subgraph_network(
    req: Request,
    subgraph_req: network_models.SubgraphRequest = Body(
        ...,
        example={
            "graph": {
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
            "nodes": [{"id": "3"}, {"id": "29"}, {"id": "18"}],
        },
    ),
) -> Dict[str, Any]:

    kwargs = subgraph_req.dict(by_alias=True)
    data = req.app.tasks.network_subgraphs(**kwargs)
    return {"data": data}


@router.post(
    "/network/solution_sequence",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def network_solution_sequence(
    request: Request,
    graph: network_models.Graph = Body(
        ...,
        example={
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
    ),
    min_branch_size: int = Query(4),
) -> Dict[str, Any]:

    g = graph.dict(by_alias=True)

    data = request.app.tasks.solution_sequence(graph=g, min_branch_size=min_branch_size)

    return {"data": data}

