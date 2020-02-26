from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from copy import deepcopy
import json
from io import StringIO

import yaml
import pandas

from nereid.core.cache import cache_decorator

PathType = Union[Path, str]


@cache_decorator(ex=3600 * 24)  # expires in 24 hours
def _load_file(filepath: PathType) -> str:
    fp = Path(filepath)
    return fp.read_text(encoding="utf-8")


def load_file(filepath: PathType) -> str:
    """wrapper to ensure the cache is called with an absolute path"""
    contents: str = _load_file(Path(filepath).resolve())
    return contents


def load_cfg(filepath: PathType) -> Dict[str, Any]:
    """load cached yaml file"""
    f = load_file(filepath)
    contents: Dict[str, Any] = yaml.safe_load(f)
    return contents


def load_multiple_cfgs(files: List[PathType]) -> Dict[str, Any]:
    """load and combine multiple cached config files"""
    conf: Dict[str, Any] = {}
    for file in files:
        conf.update(load_cfg(file))
    return conf


def load_json(filepath: PathType) -> Dict[str, Any]:
    """load cached json file"""
    f = load_file(filepath)
    contents: Dict[str, Any] = json.loads(f)
    return contents


def load_ref_data(tablename: str, context: dict) -> pandas.DataFrame:

    data_path = Path(context["data_path"])

    table_context = context.get("project_reference_data", {}).get(tablename, {})

    filepath = data_path / table_context["file"]
    ref_table = pandas.read_json(load_file(filepath), orient="table")

    for field_params in table_context.get("expand_fields", [{}]):
        field = field_params.get("field")
        sep = field_params.get("sep", "_")
        cols = field_params.get("new_column_names", [])

        for ix, col in enumerate(cols):
            ref_table[col] = ref_table[field].str.split(sep).str[ix]

    return ref_table


def parse_joins(
    df: pandas.DataFrame,
    api_recognize_key: str,
    context: Dict[str, Any],
    messages: List[str],
) -> Tuple[pandas.DataFrame, List[str]]:

    api_key_context = context.get("api_recognize", {}).get(api_recognize_key)

    if api_key_context is None:
        messages.append(
            f"ERROR: cannot recognize key {api_recognize_key} in config file: {context['data_path']}"
        )
        return df, messages

    if "joins" in api_key_context:
        for j in deepcopy(api_key_context["joins"]):
            try:
                tablename = j.pop("other")
                table = load_ref_data(tablename, context)
                df = df.merge(table, **j)
            except:
                msg = f"unable to merge {tablename} to {api_recognize_key}"
                return df, messages

    if "_merge" in df:
        if not all(df["_merge"] == "both"):
            messages.append(
                "ERROR: unable match all requested join keys to reference data."
            )
        df = df.drop(columns="_merge")

    return df, messages


def parse_remaps(
    df: pandas.DataFrame,
    api_recognize_key: str,
    context: Dict[str, Any],
    messages: List[str],
) -> Tuple[pandas.DataFrame, List[str]]:

    api_key_context = context.get("api_recognize", {}).get(api_recognize_key)

    if api_key_context is None:
        messages.append(
            f"ERROR: cannot recognize key {api_recognize_key} in config file: {context['data_path']}"
        )
        return df, messages

    if "remaps" in api_key_context:
        for remap in deepcopy(api_key_context["remaps"]):
            left = remap["left"]
            if left not in df:
                messages.append(
                    f"ERROR: key {left} not found in config[api_recognize][{api_recognize_key}]"
                )
                continue

            right = remap["right"]
            how = remap["how"]
            mapping = remap["mapping"]
            fillna = remap.get("fillna", pandas.NA)

            try:
                if how == "addend":
                    df["ini_" + right] = df[right]
                    df["addend_" + right] = df[left].map(mapping)
                    df.loc[pandas.notnull(df["addend_" + right]), right] = (
                        df[right] + df["addend_" + right]
                    ).fillna(fillna)

                elif how == "left":
                    df.loc[pandas.notnull(df[left]), right] = (
                        df[left].map(mapping).fillna(fillna)
                    )

                else:
                    messages.append(
                        f"ERROR: unrecognized remap method '{how}' in {api_recognize_key}"
                    )

            except:
                messages.append(
                    f"ERROR: unable to apply mapping '{remap}' to {api_recognize_key}"
                )

    return df, messages


def parse_api_recognize(
    df: pandas.DataFrame, api_recognize_key: str, context: Dict[str, Any]
) -> Tuple[pandas.DataFrame, List[str]]:

    msg: List[str] = []
    df, msg = parse_joins(df, api_recognize_key, context, msg)
    df, msg = parse_remaps(df, api_recognize_key, context, msg)

    return df, msg
