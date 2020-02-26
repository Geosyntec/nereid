from typing import Optional, Dict, Any, Tuple
from copy import deepcopy
from pathlib import Path

from nereid.core.io import load_cfg
from nereid.core.config import APP_CONTEXT


def validate_request_context(context: Dict[str, Any]) -> Tuple[bool, str]:

    dp = context.get("data_path")
    state = context["state"]
    region = context["region"]

    if not dp:
        message = f"No configuration exists for the requested state: '{state}' and/or region: '{region}'."
        return False, message

    data_path = Path(dp)

    if not data_path.exists():
        message = f"Requested path to reference data:{data_path} does not exist."
        return False, message

    if not context.get("project_reference_data"):
        return False, "Configuration has no 'project_reference_data' section"

    for tablename, attrs in context.get("project_reference_data", {}).items():
        try:
            filename = attrs.get("file")
            if not filename:

                message = (
                    "Section 'project_reference_data' > "
                    f"'{tablename}' has no 'file' specified"
                )
                return False, message

            filepath = data_path / filename
            if not filepath.exists():
                message = (
                    f"Requested path to reference file: {filepath} does not exist."
                )
                return False, message

        except Exception as e:
            message = (
                f"Error in section '{tablename}' with entries: '{attrs}' "
                f"Exception: {e}"
            )
            return False, message

    return True, "valid"


def get_request_context(
    state: str = "state",
    region: str = "region",
    datadir: Optional[str] = None,
    context: Optional[dict] = None,
) -> Dict[str, Any]:

    if context is None:
        context = APP_CONTEXT

    context["state"] = state
    context["region"] = region

    if datadir is None:
        default_path = Path(__file__).parent.parent / "data"
        basepath = Path(context.get("data_path", default_path))

        if (state == "state") or (region == "region"):
            datadir = basepath / context.get("default_data_directory", "")
        else:
            datadir = basepath / context.get("project_data_directory", "")

    data_path = Path(datadir) / state / region

    if not data_path.exists():
        return context

    request_context = deepcopy(context)

    request_context.update(load_cfg(data_path / "config.yml"))
    request_context["data_path"] = str(data_path)

    return request_context
