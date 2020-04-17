from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse

from nereid.api.api_v1.models.reference_models import ReferenceDataResponse
from nereid.api.api_v1.utils import get_valid_context
from nereid.core.io import load_json

router = APIRouter()


@router.get(
    "/reference_data",
    tags=["reference_data"],
    response_model=ReferenceDataResponse,
    response_class=ORJSONResponse,
)
async def get_reference_data_json(
    context: dict = Depends(get_valid_context), filename: str = ""
) -> Dict[str, Any]:

    filepath = ""
    filepath = f"{context.get('data_path', '')}/{filename}.json"
    state, region = context["state"], context["region"]

    try:
        filedata = load_json(filepath)

    except FileNotFoundError as e:
        detail = f"state '{state}', region '{region}', or filename '{filename}' not found. {filepath}"
        raise HTTPException(status_code=400, detail=detail)

    response = dict(
        status="SUCCESS",
        data=dict(state=state, region=region, file=filename, filedata=filedata),
    )

    return response
