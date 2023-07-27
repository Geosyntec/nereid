from typing import Any, Dict, List, Literal, Optional, Union

import nereid
from nereid._compat import PYDANTIC_V2, BaseSettings
from nereid.core.io import load_cfg
from nereid.core.utils import get_nereid_path

if PYDANTIC_V2:
    from pydantic import AnyHttpUrl, field_validator
else:
    from pydantic import AnyHttpUrl, validator

nereid_path = get_nereid_path()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    API_LATEST: str = API_V1_STR
    APP_CONTEXT: Dict[str, Any] = load_cfg(nereid_path / "core" / "base_config.yml")
    APP_CONTEXT.update({"version": nereid.__version__})
    VERSION: str = nereid.__version__
    DATA_DIRECTORY: Optional[str] = None
    LOGLEVEL: str = "INFO"

    FORCE_FOREGROUND: bool = False
    ENABLE_ASYNC_ROUTES: bool = False
    ASYNC_ROUTE_PREFIX: str = "/async"
    ASYNC_MODE: Literal["none", "add", "replace"] = "none"

    # ALLOW_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    ALLOW_CORS_ORIGINS: List[Union[AnyHttpUrl, Literal["*"]]] = ["*"]
    ALLOW_CORS_ORIGIN_REGEX: Optional[str] = None

    if PYDANTIC_V2:

        @field_validator("ALLOW_CORS_ORIGINS", mode="before")
        @classmethod
        def assemble_cors_origins(
            cls, v: Union[str, List[str]]
        ) -> Union[List[str], str]:
            if isinstance(v, str) and not v.startswith("["):  # pragma: no cover
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
            raise ValueError(v)  # pragma: no cover

        model_config = {"env_prefix": "NEREID_", "env_file": ".env", "extra": "allow"}

    else:

        @validator("ALLOW_CORS_ORIGINS", pre=True)
        def assemble_cors_origins(
            cls, v: Union[str, List[str]]
        ) -> Union[List[str], str]:
            if isinstance(v, str) and not v.startswith("["):  # pragma: no cover
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
            raise ValueError(v)  # pragma: no cover

        class Config:  # pragma: no cover
            env_prefix = "NEREID_"
            env_file = ".env"
            extra = "allow"

    def update(self, other: dict) -> None:  # pragma: no cover
        for key, value in other.items():
            setattr(self, key, value)


settings = Settings()
