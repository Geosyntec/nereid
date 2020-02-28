import ujson as json
from typing import Any

from fastapi import APIRouter, HTTPException

from nereid.api.api_v1.models.reference_models import ReferenceDataResponse
from nereid.core.utils import get_request_context
from nereid.core.io import load_json

router = APIRouter()


@router.get(
    "/reference_data", tags=["reference_data"], response_model=ReferenceDataResponse
)
async def get_reference_data_json(
    state: str = "state", region: str = "region", filename: str = ""
):

    filepath = ""
    req_ctxt = get_request_context(state=state, region=region)
    filepath = f"{req_ctxt['data_path']}/{filename}.json"

    try:
        filedata = load_json(filepath)

    except FileNotFoundError as e:
        detail = f"state '{state}', region '{region}', or filename '{filename}' not found. {filepath}"
        raise HTTPException(status_code=404, detail=detail)

    return ReferenceDataResponse(
        status="success",
        data=dict(state=state, region=region, file=filename, filedata=filedata),
    )
