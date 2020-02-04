from typing import List, Dict, Optional
import tempfile
import json

from fastapi import APIRouter, Body, Query
from fastapi.encoders import jsonable_encoder

from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.templating import Jinja2Templates

import celery
from celery.result import AsyncResult

from ..models.network import Graph, Node, SubgraphRequest
from nereid.bg_worker import (
    background_validate_network_from_dict,
    background_network_subgraphs,
)
from nereid.core import config
from nereid.network.utils import graph_factory
from nereid.network.render import render, fig_to_image


router = APIRouter()

templates = Jinja2Templates(directory=r"nereid/api/templates")


@router.post("/network/validate", tags=["network", "validate"])
async def validate_network(
    graph: Graph = Body(
        ...,
        example={
            "directed": True,
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        },
        examples={}
        # {
        #     "valid":{
        #         "graph": {
        #             "directed": True,
        #             "nodes": [{"id": "A"}, {"id": "B"}],
        #             "edges": [{"source": "A", "target": "B"}],
        #         }
        #     },
        #     "invalid":{
        #         "graph": {
        #             "directed": True,
        #             "nodes": [{"id": "A"}, {"id": "B"}],
        #             "edges": [{"source": "A", "target": "B"}],
        #         }
        #     },
        # }
        # ]
    )
):

    task = background_validate_network_from_dict.apply_async(
        args=(jsonable_encoder(graph),)
    )

    try:
        result = task.get(timeout=0.5)
    except celery.exceptions.TimeoutError:
        pass

    if task.successful():
        return dict(task_id=task.task_id, status=task.status, result=result)

    else:
        result_path = router.url_path_for("get_network_result", task_id=task.id)

        return dict(
            task_id=task.id,
            status=task.status,
            result_route=f"{config.API_V1_STR}{result_path}",
        )


@router.get("/network/validate/{task_id}", tags=["network", "validate"])
async def get_network_result(task_id: str):
    res = background_validate_network_from_dict.AsyncResult(task_id, app=router)

    if res.successful():
        return res.result
    else:
        return {"id": res.task_id, "status": res.status}


@router.post("/network/subgraphs", tags=["network", "subgraphs"])
async def get_subgraphs_background(
    subg_req: SubgraphRequest = Body(
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
):
    graph = subg_req.graph
    nodes = subg_req.nodes

    task = background_network_subgraphs.apply_async(
        args=(jsonable_encoder(graph), jsonable_encoder(nodes))
    )

    try:
        result = task.get(timeout=0.5)
    except celery.exceptions.TimeoutError:
        pass

    if task.successful():
        return dict(task_id=task.task_id, status=task.status, result=result)

    else:
        result_path = router.url_path_for(
            "get_network_subgraph_result", task_id=task.id
        )

        return dict(
            task_id=task.id,
            status=task.status,
            result_route=f"{config.API_V1_STR}{result_path}",
        )


@router.get("/network/subgraphs/{task_id}", tags=["network", "subgraphs"])
async def get_network_subgraph_result(task_id: str):

    res = background_network_subgraphs.AsyncResult(task_id, app=router)

    if res.successful():
        return res.result
    else:
        return {"task_id": res.task_id, "status": res.status}


@router.get("/network/subgraphs/{task_id}/img", tags=["network", "visualize"])
async def get_subgraphs_as_img(
    request: Request, task_id: str, media_type: str = Query("svg")
):

    res = background_network_subgraphs.AsyncResult(task_id, app=router)

    if res.successful():

        result = res.result

        if media_type == "svg":

            g = graph_factory(result["graph"])
            fig = render(g, result["requested_nodes"], result["subgraph_nodes"])
            svg = fig_to_image(fig)

            return templates.TemplateResponse(
                "network.html", {"request": request, "svg": svg.read().decode("utf-8")}
            )

        else:
            return result
    else:
        return {"id": res.task_id, "status": res.status}
