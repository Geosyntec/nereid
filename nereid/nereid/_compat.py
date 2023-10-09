from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic.version import VERSION as PYDANTIC_VERSION

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

M = TypeVar("M", bound="BaseModel")

if PYDANTIC_V2:
    from pydantic_settings import BaseSettings as BaseSettings

    def model_copy(model: M, **kwargs) -> M:
        return model.model_copy(**kwargs)  # type: ignore[attr-defined]

    def model_dump(model: BaseModel, **kwargs) -> dict[str, Any]:
        return model.model_dump(**kwargs)  # type: ignore[attr-defined]

    def model_construct(model: type[M], *args, **unvalidated_data) -> M:
        return model.model_construct(*args, **unvalidated_data)  # type: ignore[attr-defined]

    def model_json_schema(model: type[BaseModel], *args, **kwargs) -> dict[str, Any]:
        return model.model_json_schema(*args, **kwargs)  # type: ignore[attr-defined]

else:  # pragma: no cover
    from pydantic import (  # type: ignore[no-redef, assignment]
        BaseSettings as BaseSettings,
    )

    def model_copy(model: M, **kwargs) -> M:
        return model.copy(**kwargs)

    def model_dump(model: BaseModel, **kwargs) -> dict[str, Any]:
        return model.dict(**kwargs)

    def model_construct(model: type[M], *args, **unvalidated_data) -> M:
        return model.construct(*args, **unvalidated_data)

    def model_json_schema(model: type[BaseModel], *args, **kwargs) -> dict[str, Any]:
        return model.schema(*args, **kwargs)
