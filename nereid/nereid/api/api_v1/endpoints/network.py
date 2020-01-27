from typing import List, Dict, Optional
import tempfile
import json
import logging
from time import time

from fastapi import APIRouter, Body, Query, HTTPException
from fastapi.encoders import jsonable_encoder

from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.templating import Jinja2Templates

import celery
from celery.result import AsyncResult

from nereid.api.api_v1.models import (
    JSONAPIResponse,
    NetworkValidationResponse,
    SubgraphResponse,
)

from nereid.src.network.models import Graph, Node

from nereid.bg_worker import (
    background_validate_network_from_dict,
    background_network_subgraphs,
    background_render_subgraph_svg,
)

from nereid.core import config

logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory=r"nereid/api/templates")


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=NetworkValidationResponse,
)
async def validate_network(
    graph: Graph = Body(
        ...,
        example={
            "directed": True,
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        },
    )
):
    start1 = time()

    task = background_validate_network_from_dict.apply_async(args=(graph.dict(),))

    end1 = time()
    logger.debug(f"elapsed time submit task: {end1-start1:.4f}")

    start2 = time()
    try:
        _ = task.get(timeout=0.2)
    except celery.exceptions.TimeoutError:
        pass
    end2 = time()
    logger.debug(f"elapsed time try to get task: {end2-start2:.4f}")
    logger.debug(f"cumul time: {end2-start1:.4f}")

    response = dict(task_id=task.task_id, status=task.status)

    start3 = time()
    if task.successful():
        response["data"] = task.result

    else:
        result_path = router.url_path_for(
            "get_validate_network_result", task_id=task.id
        )
        response["result_route"] = f"{config.API_V1_STR}{result_path}"
    end3 = time()
    logger.debug(f"elapsed time load task if successful: {end3-start3:.4f}")
    logger.debug(f"cumul time: {end3-start1:.4f}")

    return response


@router.get(
    "/network/validate/{task_id}",
    tags=["network", "validate"],
    response_model=NetworkValidationResponse,
)
async def get_validate_network_result(task_id: str):
    task = background_validate_network_from_dict.AsyncResult(task_id, app=router)

    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():
        response["data"] = task.result

    return response


@router.post(
    "/network/subgraph", tags=["network", "subgraph"], response_model=SubgraphResponse
)
async def subgraph_network(
    graph: Graph = Body(
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
    nodes: List[Node] = Body(..., example=[{"id": "3"}, {"id": "29"}, {"id": "18"}]),
):

    task = background_network_subgraphs.apply_async(
        args=(graph.dict(), jsonable_encoder(nodes))
    )

    try:
        _ = task.get(timeout=0.2)
    except celery.exceptions.TimeoutError:
        pass

    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():
        response["data"] = task.result

    else:
        result_path = router.url_path_for(
            "get_subgraph_network_result", task_id=task.id
        )

        response["result_route"] = f"{config.API_V1_STR}{result_path}"

    return response


@router.get(
    "/network/subgraph/{task_id}",
    tags=["network", "subgraph"],
    response_model=SubgraphResponse,
)
async def get_subgraph_network_result(task_id: str):

    task = background_network_subgraphs.AsyncResult(task_id, app=router)
    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():
        response["data"] = task.result

    return response


@router.get(
    "/network/subgraph/{task_id}/img",
    tags=["network", "visualize"],
    response_model=JSONAPIResponse,
)
async def get_subgraph_network_as_img(
    request: Request, task_id: str, media_type: str = Query("svg")
):

    task = background_network_subgraphs.AsyncResult(task_id, app=router)
    response = dict(task_id=task.task_id, status=task.status)

    if task.successful():

        result = task.result
        response["data"] = task.result

        if media_type == "svg":

            render_task = background_render_subgraph_svg.delay(result)

            try:
                _ = render_task.get(timeout=0.1)
            except celery.exceptions.TimeoutError:
                pass

            svgresponse = dict(task_id=render_task.task_id, status=render_task.status)

            if render_task.successful():

                svg = render_task.result

                return templates.TemplateResponse(
                    "network.html", {"request": request, "svg": svg}
                )
            return svgresponse

        detail = f"media_type not supported '{media_type}'."
        raise HTTPException(status_code=404, detail=detail)

    return response
