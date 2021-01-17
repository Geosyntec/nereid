import base64
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates

from nereid.api.api_v1.models.reference_models import ReferenceDataResponse
from nereid.api.api_v1.utils import get_valid_context
from nereid.core.io import load_file, load_json, load_ref_data
from nereid.src.nomograph.nomo import load_nomograph_mapping

router = APIRouter()

templates = Jinja2Templates(directory="nereid/api/templates")


@router.get(
    "/reference_data",
    tags=["reference_data"],
    response_model=ReferenceDataResponse,
    response_class=ORJSONResponse,
)
async def get_reference_data_json(
    context: dict = Depends(get_valid_context), filename: str = ""
) -> Dict[str, Any]:

    filepath = Path(context.get("data_path", "")) / filename
    state, region = context["state"], context["region"]

    if filepath.is_file():
        if "json" in filepath.suffix.lower():
            filedata: Dict[str, Any] = load_json(filepath)
        else:
            filedata: str = load_file(filepath)  # type: ignore

    else:
        detail = f"state '{state}', region '{region}', or filename '{filename}' not found. {filepath}"
        raise HTTPException(status_code=400, detail=detail)

    response = dict(
        status="SUCCESS",
        data=dict(state=state, region=region, file=filename, filedata=filedata),
    )

    return response


@router.get(
    "/reference_data/nomograph",
    tags=["reference_data"],
    # response_model=ReferenceDataResponse,
    # response_class=ORJSONResponse,
)
async def get_nomograph(
    request: Request,
    context: dict = Depends(get_valid_context),
    filename: str = "",
    type: Optional[str] = None,
) -> Union[Dict[str, Any], Any]:
    mapping = load_nomograph_mapping(context)
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

        return templates.TemplateResponse(
            "display_svg.html", {"request": request, "svg": img}
        )

    else:
        detail = (
            f"state '{state}', region '{region}', or filename '{filename}' not found."
        )
        raise HTTPException(status_code=400, detail=detail)


@router.get(
    "/reference_data/{table}", tags=["reference_data"], response_class=ORJSONResponse,
)
async def get_reference_data_table(
    table: str, context: dict = Depends(get_valid_context)
) -> Dict[str, Any]:

    state, region = context["state"], context["region"]
    tables = context.get("project_reference_data", {}).keys()
    if table in tables:
        df, msg = load_ref_data(table, context)
        data = df.to_dict(orient="records")

    else:
        detail = f"No such table. Options are {tables}"
        raise HTTPException(status_code=400, detail=detail)

    response = dict(
        status="SUCCESS",
        data=dict(state=state, region=region, table=table, data=data, msg=msg),
    )
    return response
