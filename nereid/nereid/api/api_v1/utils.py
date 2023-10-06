from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates

from nereid.core.config import nereid_path
from nereid.core.context import get_request_context, validate_request_context

templates = Jinja2Templates(directory=f"{nereid_path}/static/templates")


def get_valid_context(
    request: Request,
    state: str = "state",
    region: str = "region",
) -> Dict[str, Any]:
    """This will redirect the context data directory according to the application instantiation."""

    key = f"{state}/{region}"
    if key in request.app._context_cache:
        return request.app._context_cache[key]

    datadir = request.app._settings.DATA_DIRECTORY
    context: Dict[str, Any] = request.app._settings.APP_CONTEXT
    context = get_request_context(state, region, datadir=datadir, context=context)
    isvalid, msg = validate_request_context(context)
    if not isvalid:
        raise HTTPException(status_code=400, detail=msg)

    request.app._context_cache[key] = context

    return context
