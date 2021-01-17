from typing import Any, Dict, List, Union

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates

import nereid.bg_worker as bg
from nereid.api.api_v1.models import network_models
from nereid.api.api_v1.utils import (
    run_task,
    standard_json_response,
    wait_a_sec_and_see_if_we_can_return_some_data,
)

router = APIRouter()

templates = Jinja2Templates(directory="nereid/api/templates")


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def validate_network(
    graph: network_models.Graph = Body(
        ...,
        example={
            "directed": True,
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        },
    )
) -> Dict[str, Any]:

    task = bg.background_validate_network.s(graph=graph.dict(by_alias=True))
    return run_task(task=task, router=router, get_route="get_validate_network_result")


@router.get(
    "/network/validate/{task_id}",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def get_validate_network_result(task_id: str) -> Dict[str, Any]:

    task = bg.background_validate_network.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_validate_network_result")


@router.post(
    "/network/subgraph",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def subgraph_network(
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
    nodes: List[network_models.Node] = Body(
        ..., example=[{"id": "3"}, {"id": "29"}, {"id": "18"}],
    ),
) -> Dict[str, Any]:

    task = bg.background_network_subgraphs.s(
        graph=graph.dict(by_alias=True), nodes=jsonable_encoder(nodes)
    )

    return run_task(task=task, router=router, get_route="get_subgraph_network_result")


@router.get(
    "/network/subgraph/{task_id}",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def get_subgraph_network_result(task_id: str) -> Dict[str, Any]:

    task = bg.background_network_subgraphs.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_subgraph_network_result")


@router.get(
    "/network/subgraph/{task_id}/img",
    tags=["network", "visualize"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def get_subgraph_network_as_img(
    request: Request,
    task_id: str,
    media_type: str = Query("svg"),
    npi: float = Query(4.0),
) -> Union[Dict[str, Any], Any]:

    task = bg.background_network_subgraphs.AsyncResult(task_id, app=router)
    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():  # pragma: no branch

        result = task.result
        response["data"] = task.result
        render_task_id = task.task_id + f"-{media_type}-{npi}"

        if media_type == "svg":
            render_task = bg.background_render_subgraph_svg.AsyncResult(
                render_task_id, app=router
            )
            if render_task.status.lower() != "started":  # pragma: no branch
                render_task = bg.background_render_subgraph_svg.apply_async(
                    args=(result, npi), task_id=render_task_id
                )
                _ = wait_a_sec_and_see_if_we_can_return_some_data(
                    render_task, timeout=0.2
                )

            svgresponse = dict(task_id=render_task.task_id, status=render_task.status)

            if render_task.successful():

                svg = render_task.result

                return templates.TemplateResponse(
                    "display_svg.html", {"request": request, "svg": svg}
                )
            return svgresponse

        detail = f"media_type not supported: '{media_type}'."
        raise HTTPException(status_code=400, detail=detail)

    return response  # pragma: no cover


@router.post(
    "/network/solution_sequence",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def network_solution_sequence(
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

    task = bg.background_solution_sequence.s(
        graph=graph.dict(by_alias=True), min_branch_size=min_branch_size
    )

    return run_task(task=task, router=router, get_route="get_network_solution_sequence")


@router.get(
    "/network/solution_sequence/{task_id}",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def get_network_solution_sequence(task_id: str) -> Dict[str, Any]:

    task = bg.background_solution_sequence.AsyncResult(task_id, app=router)
    return standard_json_response(task, router, "get_network_solution_sequence")


@router.get(
    "/network/solution_sequence/{task_id}/img",
    tags=["network", "sequence", "visualize"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def get_network_solution_sequence_as_img(
    request: Request,
    task_id: str,
    media_type: str = Query("svg"),
    npi: float = Query(4.0),
) -> Union[Dict[str, Any], Any]:

    task = bg.background_solution_sequence.AsyncResult(task_id, app=router)
    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():  # pragma: no branch

        result = task.result
        response["data"] = task.result
        render_task_id = task.task_id + f"-{media_type}-{npi}"

        if media_type == "svg":

            render_task = bg.background_render_solution_sequence_svg.AsyncResult(
                render_task_id, app=router
            )
            if render_task.status.lower() != "started":  # pragma: no branch
                render_task = bg.background_render_solution_sequence_svg.apply_async(
                    args=(result, npi), task_id=render_task_id
                )
                _ = wait_a_sec_and_see_if_we_can_return_some_data(
                    render_task, timeout=0.2
                )

            svgresponse = dict(task_id=render_task.task_id, status=render_task.status)

            if render_task.successful():

                svg = render_task.result

                return templates.TemplateResponse(
                    "display_svg.html", {"request": request, "svg": svg}
                )
            return svgresponse

        detail = f"media_type not supported: '{media_type}'."
        raise HTTPException(status_code=400, detail=detail)

    return response  # pragma: no cover
