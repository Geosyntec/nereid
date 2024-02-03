import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

from nereid.core.config import settings
from nereid.core.io import load_cfg

logger = logging.getLogger("nereid.core")


def validate_request_context(context: dict[str, Any]) -> tuple[bool, str]:
    dp = context.get("data_path")
    state = context["state"]
    region = context["region"]

    if not dp:
        message = (
            "No configuration exists for the requested state: "
            f"'{state}' and/or region: '{region}'."
        )
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
            if filename:
                filepath = data_path / filename
                if not filepath.exists():
                    message = (
                        f"Requested path to reference file: {filepath} does not exist."
                    )
                    logger.error(message)
                    return False, message

        except Exception as e:  # noqa: PERF203
            message = f"Error in section '{tablename}' with entries: '{attrs}' "
            logger.exception(message, stack_info=True)
            return False, message + f"Exception: {e}"

    return True, "valid"


def get_request_context(
    state: str = "state",
    region: str = "region",
    datadir: str | Path | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if context is None:
        context = settings.APP_CONTEXT

    context["state"] = state
    context["region"] = region

    if datadir is None:
        default_path = Path(__file__).parent.parent / "data"
        basepath = Path(context.get("data_path", default_path))

        p: str = context.get("project_data_directory", "")
        if (state == "state") or (region == "region"):
            p = context.get("default_data_directory", "")

        datadir = basepath / p

    data_path = Path(datadir) / state / region

    if not data_path.exists():
        return context

    request_context = deepcopy(context)

    request_context.update(load_cfg(data_path / "config.yml"))
    request_context["data_path"] = str(data_path)

    return request_context
