import ujson as json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from nereid.core.startup_redis import redis_cache, load_reference_data


router = APIRouter()


class ReferenceData(BaseModel):
    path: str
    state: str
    region: str
    data: Any


@router.get("/reference_data/refresh", tags=["reference_data"])
async def refresh_data():

    status = "failed"

    if redis_cache.ping():
        load_reference_data()
        status = "success"

    return dict(status=status)


@router.get("/reference_data", tags=["reference_data"], response_model=ReferenceData)
async def get_bmp_performance_data(
    state: str = "state", region: str = "region", filename: str = ""
):

    dirname = "project_data"

    if state == "state" and region == "region":
        dirname = "default_data"

    key = rf"nereid/data/{dirname}/{state}/{region}/{filename}"

    json_blob = redis_cache.get(key)

    if json_blob is None:
        detail = (
            f"state '{state}', region '{region}', or filename '{filename}' not found."
        )
        raise HTTPException(status_code=404, detail=detail)

    data = json.loads(json_blob)

    return ReferenceData(path=key, state=state, region=region, data=data)
