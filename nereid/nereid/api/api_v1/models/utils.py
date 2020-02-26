from typing import Any, Dict, List, Optional, Callable
import string
import numpy

from pydantic import BaseModel, ValidationError


def validate_models_with_discriminator(
    unvalidated_data: List[Dict[str, Any]],
    discriminator: str,
    model_mapping: Dict[str, Any],
    fallback_mapping: Dict[str, Any],
) -> List[Any]:
    class NullModel(BaseModel):
        class Config:
            extra = "allow"

    validated = []
    for dct in unvalidated_data:
        attr = dct[discriminator]
        model = model_mapping.get(attr, None)
        fallback = fallback_mapping.get(attr, NullModel)

        if model is None:
            e = f"the key '{attr}' is not in `model_mapping`. Using `fallback` value: {fallback.schema()['title']}"
            dct["errors"] = [str(e)]
            model = fallback
        try:
            valid = model(valid_model=model.schema()["title"], **dct)

        except ValidationError as e:
            dct["errors"] = [str(e)]
            model = fallback
            valid = model(valid_model=model.schema()["title"], **dct)

        validated.append(valid)

    return validated


def create_random_model_dict(model: BaseModel, can_fail: bool = True) -> Dict[str, Any]:
    def random_string(nchars: int) -> str:
        letters = [l for l in string.ascii_letters]
        return "".join([numpy.random.choice(letters) for i in range(nchars)])

    schema = model.schema()
    reqds = schema["required"]
    props = schema["properties"]
    optionalprops = list(set(props.keys()) - set(reqds))

    extras: List = []
    if can_fail:  # pragma: no cover
        if len(optionalprops) > 1:
            extras = [numpy.random.choice(optionalprops)]
        elif numpy.random.random() > 0.5:
            extras = optionalprops
    else:
        extras = optionalprops

    keys_subset = reqds + extras

    dct = {}
    for k in keys_subset:  # pragma: no cover
        v = props[k]
        value: Any = None

        if v.get("default") is not None:
            value = v["default"]
        elif v["type"] == "string":
            value = random_string(12)
        elif v["type"] == "boolean":
            value = numpy.random.choice([True, False])
        elif v["type"] == "number":
            value = numpy.random.random() * 1000

        dct[k] = value

    return dct
