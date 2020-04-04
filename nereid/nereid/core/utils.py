from typing import Optional, Dict, Any, List, Tuple
from copy import deepcopy
from pathlib import Path

import pandas
from pydantic import BaseModel, ValidationError

from nereid.core.io import load_cfg
from nereid.core.config import APP_CONTEXT


def validate_request_context(context: Dict[str, Any]) -> Tuple[bool, str]:

    dp = context.get("data_path")
    state = context["state"]
    region = context["region"]

    if not dp:
        message = f"No configuration exists for the requested state: '{state}' and/or region: '{region}'."
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
            if not filename:

                message = (
                    "Section 'project_reference_data' > "
                    f"'{tablename}' has no 'file' specified"
                )
                return False, message

            filepath = data_path / filename
            if not filepath.exists():
                message = (
                    f"Requested path to reference file: {filepath} does not exist."
                )
                return False, message

        except Exception as e:
            message = (
                f"Error in section '{tablename}' with entries: '{attrs}' "
                f"Exception: {e}"
            )
            return False, message

    return True, "valid"


def get_request_context(
    state: str = "state",
    region: str = "region",
    datadir: Optional[str] = None,
    context: Optional[dict] = None,
) -> Dict[str, Any]:

    if context is None:
        context = APP_CONTEXT

    context["state"] = state
    context["region"] = region

    if datadir is None:
        default_path = Path(__file__).parent.parent / "data"
        basepath = Path(context.get("data_path", default_path))

        if (state == "state") or (region == "region"):
            datadir = basepath / context.get("default_data_directory", "")
        else:
            datadir = basepath / context.get("project_data_directory", "")

    data_path = Path(datadir) / state / region

    if not data_path.exists():
        return context

    request_context = deepcopy(context)

    request_context.update(load_cfg(data_path / "config.yml"))
    request_context["data_path"] = str(data_path)

    return request_context


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
            e = (
                f"ERROR: the key '{attr}' is not in `model_mapping`. "
                f"Using `fallback` value: {fallback.schema()['title']}"
            )

            dct["errors"] = str(e) + "  \n"
            model = fallback
        try:
            valid = model(valid_model=model.schema()["title"], **dct)

        except ValidationError as e:
            dct["errors"] = "ERROR: " + str(e) + "  \n"
            model = fallback
            valid = model(valid_model=model.schema()["title"], **dct)

        validated.append(valid)

    return validated


def safe_divide(x: float, y: float) -> float:
    """This returns zero if the denominator is zero
    """
    if y == 0.0:
        return 0.0
    return x / y


def dictlist_to_dict(dictlist, key):
    """turn a list of dicts with a common key into a dict. values
    of the key should be unique within the dictlist

    Example
    -------
    >>>dict_list = [{"id":"a"}, {"id":"b"}]
    >>>dictlist_to_dict(dict_list, "id")
    {'a': {'id': 'a'}, 'b': {'id': 'b'}}

    """
    result = {}
    for dct in dictlist:
        k = dct[key]
        result[k] = dct
    return result
