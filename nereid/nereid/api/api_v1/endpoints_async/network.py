from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

import nereid.bg_worker as bg
from nereid.api.async_utils import (
    run_task,
    standard_json_response,
    wait_a_sec_and_see_if_we_can_return_some_data,
)
from nereid.api.utils import templates
from nereid.models import network_models

router = APIRouter()


@router.post(
    "/network/validate",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def validate_network(
    request: Request,
    graph: network_models.Graph = Body(
        ...,
        openapi_examples=network_models.GraphExamples,  # type: ignore[arg-type]
    ),
) -> dict[str, Any]:
    task = bg.validate_network.s(graph=graph.model_dump(by_alias=True))
    return await run_task(request, task, "get_validate_network_result")


@router.get(
    "/network/validate/{task_id}",
    tags=["network", "validate"],
    response_model=network_models.NetworkValidationResponse,
    response_class=ORJSONResponse,
)
async def get_validate_network_result(request: Request, task_id: str) -> dict[str, Any]:
    task = bg.validate_network.AsyncResult(task_id, app=router)
    return await standard_json_response(request, task, "get_validate_network_result")


@router.post(
    "/network/subgraph",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def subgraph_network(
    request: Request,
    subgraph_req: network_models.SubgraphRequest = Body(...),
) -> dict[str, Any]:
    task = bg.network_subgraphs.s(**subgraph_req.model_dump(by_alias=True))

    return await run_task(request, task, "get_subgraph_network_result")


@router.get(
    "/network/subgraph/{task_id}",
    tags=["network", "subgraph"],
    response_model=network_models.SubgraphResponse,
    response_class=ORJSONResponse,
)
async def get_subgraph_network_result(request: Request, task_id: str) -> dict[str, Any]:
    task = bg.network_subgraphs.AsyncResult(task_id, app=router)
    return await standard_json_response(request, task, "get_subgraph_network_result")


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
) -> dict[str, Any] | Any:
    if media_type != "svg":
        detail = f"media_type not supported: '{media_type}'."
        raise HTTPException(status_code=400, detail=detail)

    task = bg.network_subgraphs.AsyncResult(task_id, app=router)
    response = {"task_id": task.task_id, "status": task.status}

    if task.successful():
        result = task.result
        response["data"] = task.result
        render_task_id = task.task_id + f"-{media_type}-{npi}"

        render_task = bg.render_subgraph_svg.AsyncResult(render_task_id, app=router)
        if not render_task.ready() and render_task.status.lower() != "started":
            render_task = bg.render_subgraph_svg.apply_async(
                args=(result, npi), task_id=render_task_id
            )
            _ = await wait_a_sec_and_see_if_we_can_return_some_data(
                render_task, timeout=10
            )

        if render_task.successful():
            svg = render_task.result
            return templates.TemplateResponse(request, "display_svg.html", {"svg": svg})
        return {"task_id": render_task.task_id, "status": render_task.status}

    return response


@router.post(
    "/network/solution_sequence",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def network_solution_sequence(
    request: Request,
    graph: network_models.ValidGraph = Body(
        ...,
        openapi_examples=network_models.GraphExamples,  # type: ignore[arg-type]
    ),
    min_branch_size: int = Query(4),
) -> dict[str, Any]:
    task = bg.solution_sequence.s(
        graph=graph.model_dump(by_alias=True), min_branch_size=min_branch_size
    )

    return await run_task(request, task, "get_network_solution_sequence")


@router.get(
    "/network/solution_sequence/{task_id}",
    tags=["network", "sequence"],
    response_model=network_models.SolutionSequenceResponse,
    response_class=ORJSONResponse,
)
async def get_network_solution_sequence(
    request: Request, task_id: str
) -> dict[str, Any]:
    task = bg.solution_sequence.AsyncResult(task_id, app=router)
    return await standard_json_response(request, task, "get_network_solution_sequence")


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
) -> dict[str, Any] | Any:
    if media_type != "svg":
        detail = f"media_type not supported: '{media_type}'."
        raise HTTPException(status_code=400, detail=detail)

    task = bg.solution_sequence.AsyncResult(task_id, app=router)
    response = {"task_id": task.task_id, "status": task.status}

    if task.successful():
        result = task.result
        response["data"] = task.result
        render_task_id = task.task_id + f"-{media_type}-{npi}"

        render_task = bg.render_solution_sequence_svg.AsyncResult(
            render_task_id, app=router
        )
        if not render_task.ready() and render_task.status.lower() != "started":
            render_task = bg.render_solution_sequence_svg.apply_async(
                args=(result, npi), task_id=render_task_id
            )
            _ = await wait_a_sec_and_see_if_we_can_return_some_data(
                render_task, timeout=10
            )

        if render_task.successful():
            svg = render_task.result
            return templates.TemplateResponse(request, "display_svg.html", {"svg": svg})
        return {"task_id": render_task.task_id, "status": render_task.status}

    return response
