from functools import reduce
from pathlib import Path
from typing import Any

import numpy
import pandas
from pydantic import BaseModel, ValidationError


def get_nereid_path():
    return Path(__file__).resolve().parent.parent


def validate_with_discriminator(
    unvalidated_data: dict[str, Any],
    discriminator: str,
    model_mapping: dict[str, Any],
    fallback_mapping: dict[str, Any],
) -> Any:
    class NullModel(BaseModel):
        model_config = {"extra": "allow"}

    attr = unvalidated_data[discriminator]
    model = model_mapping.get(attr, None)
    fallback = fallback_mapping.get(attr, NullModel)  # type: ignore

    if model is None:
        e = (
            f"ERROR: the key '{attr}' is not in `model_mapping`. "
            f"Using `fallback` value: {fallback.model_json_schema()['title']}"
        )

        unvalidated_data["errors"] = str(e).strip()
        model = fallback
    try:
        valid = model(**unvalidated_data)

    except ValidationError as e:
        unvalidated_data["errors"] = "ERROR: " + str(e).strip()
        valid = fallback.model_construct(**unvalidated_data)

    return valid


def safe_divide(x: float, y: float) -> float:
    """This returns zero if the denominator is zero"""
    if y == 0.0:
        return 0.0
    return x / y


def safe_array_divide(
    x: numpy.ndarray | pandas.Series, y: numpy.ndarray | pandas.Series
) -> numpy.ndarray:
    return numpy.divide(x, y, out=numpy.zeros_like(x), where=y != 0)


def dictlist_to_dict(dictlist, key):
    """turn a list of dicts with a common key into a dict. values
    of the key should be unique within the dictlist

    Example
    -------
    ```python
    dict_list = [{"id":"a"}, {"id":"b"}]
    dictlist_to_dict(dict_list, "id")
    {'a': {'id': 'a'}, 'b': {'id': 'b'}}
    ```

    """
    result = {}
    for dct in dictlist:
        k = dct[key]
        result[k] = dct
    return result


def _merge(a: dict, b: dict) -> dict:  # pragma: no cover # used only by main.py
    """Recursive dictionary update of `a` with `b`.

    `a` is modified, `b` is read-only.
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge(a[key], b[key])
        else:
            a[key] = b[key]
    return a


def merge_dicts(*dicts: dict) -> dict:  # pragma: no cover # used only by main.py
    """Deep merge of all dict keys. Later arg values overwrite earlier ones.
    Returns a new dictionary without modifying passed dicts.
    """
    return reduce(_merge, ({}, *dicts))
