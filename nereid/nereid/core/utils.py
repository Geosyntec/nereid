from typing import Optional, Dict, Any
import copy
from pathlib import Path

from nereid.core.io import load_cfg
from nereid.core.config import APP_CONTEXT


def get_request_context(
    state: str = "state",
    region: str = "region",
    datadir: Optional[str] = None,
    context: Optional[dict] = None,
) -> Dict[str, Any]:

    if context is None:
        context = APP_CONTEXT

    if datadir is None:
        basepath = Path(context.get("data_path", APP_CONTEXT["data_path"]))

        if (state == "state") or (region == "region"):
            datadir = basepath / context.get("default_data_directory", "")
        else:
            datadir = basepath / context.get("project_data_directory", "")

    data_path = Path(datadir) / state / region

    if not data_path.exists():
        return context

    request_context = copy.deepcopy(context)

    request_context.update(load_cfg(data_path / "config.yml"))
    request_context["data_path"] = str(data_path)

    return request_context
