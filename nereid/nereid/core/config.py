from typing import Any, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

import nereid
from nereid.core.io import load_cfg
from nereid.core.utils import get_nereid_path

nereid_path = get_nereid_path()


class Settings(BaseSettings):
    APP_CONTEXT: dict[str, Any] = load_cfg(nereid_path / "core" / "base_config.yml")
    APP_CONTEXT.update({"version": nereid.__version__})
    VERSION: str = nereid.__version__
    DATA_DIRECTORY: str | None = None
    LOG_LEVEL: str = "WARNING"

    STATIC_DOCS: bool = False

    FORCE_FOREGROUND: bool = False
    ENABLE_ASYNC_ROUTES: bool = False
    ASYNC_ROUTE_PREFIX: str = "/async"
    ASYNC_MODE: Literal["none", "add", "replace"] = "none"

    # ALLOW_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    ALLOW_CORS_ORIGINS: list[AnyHttpUrl | Literal["*"]] = ["*"]
    ALLOW_CORS_ORIGIN_REGEX: str | None = None

    @field_validator("ALLOW_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):  # pragma: no cover
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)  # pragma: no cover

    model_config = {
        "env_prefix": "NEREID_",
        "env_file": ".env",
        "extra": "allow",
    }

    def update(self, other: dict) -> None:  # pragma: no cover
        for key, value in other.items():
            setattr(self, key, value)


settings = Settings()
