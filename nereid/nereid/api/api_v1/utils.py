from typing import Any, Dict

from fastapi import HTTPException
from fastapi.templating import Jinja2Templates

from nereid.core.config import nereid_path
from nereid.core.context import get_request_context, validate_request_context

templates = Jinja2Templates(directory=f"{nereid_path}/static/templates")


def get_valid_context(state: str = "state", region: str = "region") -> Dict[str, Any]:
    context = get_request_context(state, region)
    isvalid, msg = validate_request_context(context)
    if not isvalid:
        raise HTTPException(status_code=400, detail=msg)

    return context
