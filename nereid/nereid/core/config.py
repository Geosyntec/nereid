from pathlib import Path
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
    LOG_FILENAME: str | None = None  # ".logs/logs.jsonl"

    @field_validator("LOG_FILENAME")
    @classmethod
    def create_logfile_path(cls, v: str | None) -> str | None:  # pragma: no cover
        if v:
            p = Path(v).resolve().parent
            p.mkdir(parents=True, exist_ok=True)
        return v

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
    def assemble_cors_origins(
        cls, v: str | list[str]
    ) -> list[str] | str:  # pragma: no cover
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = {
        "env_prefix": "NEREID_",
        "env_file": ".env",
        "extra": "allow",
    }

    def update(self, other: dict) -> None:  # pragma: no cover
        for key, value in other.items():
            setattr(self, key, value)


settings = Settings()

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "nereid_simple": {
            "format": "%(levelname)-9s %(name)s: %(message)s",
        },
        "nereid_detailed": {
            "format": "[%(levelname)s|%(name)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "nereid_json": {
            "()": "nereid.core.log.JSONLogFormatter",
            "fmt_keys": {
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "path": "pathname",
                "function": "funcName",
                "line": "lineno",
                "thread_name": "threadName",
            },
        },
    },
    "handlers": {
        "nereid_stderr": {
            "formatter": "nereid_simple",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "nereid": {
            "handlers": ["nereid_stderr"],
            "level": settings.LOG_LEVEL,
        },
    },
}

if settings.LOG_FILENAME:  # pragma: no cover
    LOGGING_CONFIG["handlers"].update(
        {
            "nereid_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "WARNING",
                "formatter": "nereid_json",
                "filename": settings.LOG_FILENAME,
                "maxBytes": 100_000,
                "backupCount": 5,
            },
            "nereid_queue": {
                "()": "nereid.core.log.QueueHandler",
                "handlers": ["nereid_file"],
                "respect_handler_level": True,
                "auto_run": True,
            },
        }
    )
    LOGGING_CONFIG["loggers"]["nereid"]["handlers"].append("nereid_queue")
