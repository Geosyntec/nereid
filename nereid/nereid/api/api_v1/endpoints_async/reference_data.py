import base64
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse, ORJSONResponse

from nereid.api.utils import get_valid_context, templates
from nereid.core.io import load_file, load_json, load_ref_data
from nereid.models.reference_models import ReferenceDataResponse
from nereid.src.nomograph.nomo import load_nomograph_mapping

router = APIRouter()


@router.get("/reference_data_file", tags=["reference_data"])
async def get_reference_data_file(
    context: dict = Depends(get_valid_context), filename: str = ""
) -> FileResponse:
    filepath = Path(context.get("data_path", "")) / filename
    state, region = context["state"], context["region"]

    if filepath.is_file():
        return FileResponse(filepath)

    else:
        detail = f"state '{state}', region '{region}', or filename '{filename}' not found. {filepath}"
        raise HTTPException(status_code=400, detail=detail)


@router.get(
    "/reference_data",
    tags=["reference_data"],
    response_model=ReferenceDataResponse,
    response_class=ORJSONResponse,
)
async def get_reference_data_json(
    context: dict = Depends(get_valid_context), filename: str = ""
) -> dict[str, Any]:
    filepath = Path(context.get("data_path", "")) / filename
    state, region = context["state"], context["region"]

    if filepath.is_file():
        filedata: dict[str, Any] | str = ""
        loader: Callable[[Path | str], dict[str, Any] | str] = load_file
        if "json" in filepath.suffix.lower():
            loader = load_json
        filedata = loader(filepath)

    else:
        detail = f"state '{state}', region '{region}', or filename '{filename}' not found. {filepath}"
        raise HTTPException(status_code=400, detail=detail)

    response = {
        "status": "SUCCESS",
        "data": {
            "state": state,
            "region": region,
            "file": filename,
            "filedata": filedata,
        },
    }

    return response


@router.get("/reference_data/nomograph", tags=["reference_data"])
async def get_nomograph(
    request: Request,
    context: dict = Depends(get_valid_context),
    filename: str = "",
    type: str | None = None,
) -> dict[str, Any] | Any:
    mapping = load_nomograph_mapping(context) or {}
    state, region = context["state"], context["region"]
    nomo = mapping.get(filename) or None
    if nomo:
        if type == "surface":
            fig = nomo.surface_plot().get_figure()  # type: ignore
            f = BytesIO()
            fig.savefig(f, bbox_inches="tight", format="png", dpi=300)
            f.seek(0)
            encoded = base64.b64encode(f.getvalue()).decode("utf-8")
            img: str = f"<img width='600' src='data:image/png;base64,{encoded}'>"

        else:
            fig = nomo.plot().get_figure()  # type: ignore
            f = BytesIO()
            fig.savefig(f, bbox_inches="tight", format="svg")
            f.seek(0)
            img = f.read().decode()

        return templates.TemplateResponse(request, "display_svg.html", {"svg": img})

    else:
        detail = (
            f"state '{state}', region '{region}', or filename '{filename}' not found."
        )
        raise HTTPException(status_code=400, detail=detail)


@router.get(
    "/reference_data/{table}",
    tags=["reference_data"],
    response_class=ORJSONResponse,
)
async def get_reference_data_table(
    table: str, context: dict = Depends(get_valid_context)
) -> dict[str, Any]:
    state, region = context["state"], context["region"]
    tables = context.get("project_reference_data", {}).keys()
    if table in tables:
        data = None
        df, msg = load_ref_data(table, context)
        if df is not None:  # pragma: no branch
            data = df.to_dict(orient="records")

    else:
        detail = f"No such table. Options are {tables}"
        raise HTTPException(status_code=400, detail=detail)

    response = {
        "status": "SUCCESS",
        "data": {
            "state": state,
            "region": region,
            "table": table,
            "data": data,
            "msg": msg,
        },
    }
    return response
