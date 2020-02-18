from pathlib import Path

from nereid.core.io import load_cfg


API_V1_STR = "/api/v1"
API_LATEST = API_V1_STR
APP_CONTEXT = load_cfg(Path(__file__).parent / "base_config.yml")
APP_CONTEXT["data_path"] = (
    Path(__file__).parent.parent.parent / APP_CONTEXT["data_path"]
)
