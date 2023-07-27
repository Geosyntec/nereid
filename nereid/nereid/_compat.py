from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel
from pydantic.version import VERSION as PYDANTIC_VERSION

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

M = TypeVar("M", bound="BaseModel")

if TYPE_CHECKING:
    PYDANTIC_V2 = True

if PYDANTIC_V2:
    from pydantic_settings import BaseSettings as BaseSettings

    def model_copy(model: M, **kwargs) -> M:
        return model.model_copy(**kwargs)

    def model_dump(model: BaseModel, **kwargs) -> dict[str, Any]:
        return model.model_dump(**kwargs)

    def model_construct(model: type[M], *args, **unvalidated_data) -> M:
        return model.model_construct(*args, **unvalidated_data)

    def model_json_schema(model: type[BaseModel], *args, **kwargs) -> dict[str, Any]:
        return model.model_json_schema(*args, **kwargs)

else:
    from pydantic import BaseSettings as BaseSettings

    def model_copy(model: M, **kwargs) -> M:
        return model.copy(**kwargs)

    def model_dump(model: BaseModel, **kwargs) -> dict[str, Any]:
        return model.dict(**kwargs)

    def model_construct(model: type[M], *args, **unvalidated_data) -> M:
        return model.construct(*args, **unvalidated_data)

    def model_json_schema(model: type[BaseModel], *args, **kwargs) -> dict[str, Any]:
        return model.schema(*args, **kwargs)
