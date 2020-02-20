from typing import List, Dict, Optional

from fastapi import APIRouter, Body, Query, HTTPException
from fastapi.encoders import jsonable_encoder

from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.templating import Jinja2Templates

from celery.result import AsyncResult

from nereid.api.api_v1.utils import wait_a_sec_and_see_if_we_can_return_some_data
from nereid.core import config
from nereid.api.api_v1.models import network_models
import nereid.bg_worker as bg


router = APIRouter()

templates = Jinja2Templates(directory=r"nereid/api/templates")


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
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
):

    task = bg.background_validate_network_from_dict.apply_async(
        args=(graph.dict(by_alias=True),)
    )

    router_path = router.url_path_for("get_validate_network_result", task_id=task.id)

    result_route = f"{config.API_V1_STR}{router_path}"

    _ = wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=0.2)

    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():
        response["data"] = task.result

    return response


@router.get(
    "/network/validate/{task_id}",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
)
async def get_validate_network_result(task_id: str):
    task = bg.background_validate_network_from_dict.AsyncResult(task_id, app=router)

    router_path = router.url_path_for("get_validate_network_result", task_id=task.id)

    result_route = f"{config.API_V1_STR}{router_path}"

    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():
        response["data"] = task.result

    return response


@router.post(
    "/network/subgraph",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
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
        ..., example=[{"id": "3"}, {"id": "29"}, {"id": "18"}]
    ),
):

    task = bg.background_network_subgraphs.apply_async(
        args=(graph.dict(by_alias=True), jsonable_encoder(nodes))
    )

    router_path = router.url_path_for("get_subgraph_network_result", task_id=task.id)

    result_route = f"{config.API_V1_STR}{router_path}"

    _ = wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=0.2)

    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():  # pragma: no branch
        response["data"] = task.result

    return response


@router.get(
    "/network/subgraph/{task_id}",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
)
async def get_subgraph_network_result(task_id: str):

    task = bg.background_network_subgraphs.AsyncResult(task_id, app=router)
    router_path = router.url_path_for("get_subgraph_network_result", task_id=task.id)

    result_route = f"{config.API_V1_STR}{router_path}"
    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():  # pragma: no branch
        response["data"] = task.result

    return response


@router.get(
    "/network/subgraph/{task_id}/img",
    tags=["network", "visualize"],
    response_model=network_models.SubgraphResponse,
)
async def get_subgraph_network_as_img(
    request: Request,
    task_id: str,
    media_type: str = Query("svg"),
    npi: float = Query(4.0),
):

    task = bg.background_network_subgraphs.AsyncResult(task_id, app=router)
    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():  # pragma: no branch

        result = task.result
        response["data"] = task.result

        if media_type == "svg":

            render_task = bg.background_render_subgraph_svg.delay(result, npi)
            _ = wait_a_sec_and_see_if_we_can_return_some_data(render_task, timeout=0.2)

            svgresponse = dict(task_id=render_task.task_id, status=render_task.status)

            if render_task.successful():

                svg = render_task.result

                return templates.TemplateResponse(
                    "network.html", {"request": request, "svg": svg}
                )
            return svgresponse

        detail = f"media_type not supported: '{media_type}'."
        raise HTTPException(status_code=400, detail=detail)

    return response  # pragma: no cover


@router.post(
    "/network/solution_sequence",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
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
):

    task = bg.background_solution_sequence.apply_async(
        args=(graph.dict(by_alias=True), min_branch_size)
    )

    router_path = router.url_path_for("get_network_solution_sequence", task_id=task.id)

    result_route = f"{config.API_V1_STR}{router_path}"

    _ = wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=0.2)

    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():  # pragma: no branch
        response["data"] = task.result

    return response


@router.get(
    "/network/solution_sequence/{task_id}",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
)
async def get_network_solution_sequence(task_id: str):

    task = bg.background_solution_sequence.AsyncResult(task_id, app=router)
    router_path = router.url_path_for("get_network_solution_sequence", task_id=task.id)

    result_route = f"{config.API_V1_STR}{router_path}"
    response = dict(task_id=task.task_id, status=task.status, result_route=result_route)

    if task.successful():  # pragma: no branch
        response["data"] = task.result

    return response


@router.get(
    "/network/solution_sequence/{task_id}/img",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
)
async def get_network_solution_sequence_as_img(
    request: Request,
    task_id: str,
    media_type: str = Query("svg"),
    npi: float = Query(4.0),
):

    task = bg.background_solution_sequence.AsyncResult(task_id, app=router)
    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():  # pragma: no branch

        result = task.result
        response["data"] = task.result

        if media_type == "svg":

            render_task = bg.background_render_solution_sequence_svg.delay(result, npi)
            _ = wait_a_sec_and_see_if_we_can_return_some_data(render_task, timeout=0.2)

            svgresponse = dict(task_id=render_task.task_id, status=render_task.status)

            if render_task.successful():

                svg = render_task.result

                return templates.TemplateResponse(
                    "network.html", {"request": request, "svg": svg}
                )
            return svgresponse

        detail = f"media_type not supported: '{media_type}'."
        raise HTTPException(status_code=400, detail=detail)

    return response  # pragma: no cover
