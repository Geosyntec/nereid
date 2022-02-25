from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import orjson as json
import pandas
import yaml

PathType = Union[Path, str]


@lru_cache
def _load_file(filepath: PathType) -> bytes:
    """returns bytes for redis cache compatability"""
    fp = Path(filepath)
    return fp.read_bytes()


def load_file(filepath: PathType) -> str:
    """wrapper to ensure the cache is called with an absolute path"""
    contents: str = _load_file(Path(filepath).resolve()).decode()
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

    df, msg = parse_configuration_logic(
        df=ref_table,
        config_section="project_reference_data",
        config_object=tablename,
        context=context,
    )

    return df, msg


def parse_expand_fields(
    df: pandas.DataFrame,
    params: List[Dict[str, Any]],
    config_section: str,
    config_object: str,
    context: Dict[str, Any],
    messages: List[str],
) -> Tuple[pandas.DataFrame, List[str]]:

    for f in deepcopy(params):
        try:
            field = f.get("field")
            sep = f.get("sep", "_")
            cols = f.get("new_column_names", [])

            for ix, col in enumerate(cols):
                df[col] = df[field].str.split(sep).str[ix]
        except:
            messages.append(
                f"unable to expand fields in {config_section}:{config_object} "
                f"for instructions {f}"
            )

    return df, messages


def parse_collapse_fields(
    df: pandas.DataFrame,
    params: List[Dict[str, Any]],
    config_section: str,
    config_object: str,
    context: Dict[str, Any],
    messages: List[str],
) -> Tuple[pandas.DataFrame, List[str]]:

    for f in deepcopy(params):
        try:
            field = f.get("new_column_name")
            sep = f.get("sep", "_")
            cols = f.get("fields", [])

            df[field] = df[cols[0]].astype(str)
            for col in cols[1:]:
                df[field] = df[field] + sep + df[col].astype(str)
        except:
            messages.append(
                f"unable to expand fields in {config_section}:{config_object} "
                f"for instructions {f}"
            )

    return df, messages


def parse_joins(
    df: pandas.DataFrame,
    params: List[Dict[str, Any]],
    config_section: str,
    config_object: str,
    context: Dict[str, Any],
    messages: List[str],
) -> Tuple[pandas.DataFrame, List[str]]:

    df_input = df.copy()

    for j in deepcopy(params):
        tablename = j.pop("other", "ERROR: key 'other' is required")
        fuzzy_on = j.pop("fuzzy_on", None)

        try:
            table, msg = load_ref_data(tablename, context)
            messages.extend(msg)
            df = df.merge(table, **j)

            if (fuzzy_on is not None) and (not all(df["_merge"] == "both")):
                matched = df.loc[df["_merge"] == "both"].copy()
                matched["_on"] = j.get("left_on")

                missing = (
                    df_input.loc[df["_merge"] != "both"].copy().reset_index(drop=True)
                )

                patches = [matched]
                for fuzzy_key in fuzzy_on:
                    table, msg = load_ref_data(tablename, context)
                    messages.extend(msg)
                    fuzzy_j = deepcopy(j)
                    fuzzy_j["left_on"] = fuzzy_key
                    fuzzy_df = missing.merge(table, **fuzzy_j)

                    found = fuzzy_df.loc[fuzzy_df["_merge"] == "both"].copy()
                    found["_on"] = fuzzy_key

                    missing = (
                        missing.loc[fuzzy_df["_merge"] != "both"]
                        .copy()
                        .reset_index(drop=True)
                    )

                    patches.append(found)

                patches.append(missing)
                df = pandas.concat(patches, ignore_index=True)

            if "_merge" in df:
                if not all(df["_merge"] == "both"):
                    messages.append(
                        f"ERROR: Some data from {tablename} failed the requested join '{j}' to "
                        f"reference data in {config_section}:{config_object}."
                    )
                    if not "errors" in df:
                        df["errors"] = ""
                    df.loc[df["_merge"] != "both", "errors"] += (
                        f"ERROR: unable join '{j['left_on']}' from {tablename} to '{j['right_on']}' "
                        f"for reference data in {config_section}:{config_object}.\n"
                    )
                df = df.drop(columns="_merge")
        except Exception as e:
            messages.append(
                f"unable to merge {tablename} in {config_section}:{config_object}\n{e}"
            )

    assert len(df) == len(df_input)

    return df, messages


def parse_remaps(
    df: pandas.DataFrame,
    params: List[Dict[str, Any]],
    config_section: str,
    config_object: str,
    context: Dict[str, Any],
    messages: List[str],
) -> Tuple[pandas.DataFrame, List[str]]:

    for remap in deepcopy(params):
        left = remap["left"]
        if left not in df:
            messages.append(
                f"WARNING: REMAP key {left} not found in columns '{df.columns}' "
                f"from {config_section}:{config_object}."
            )
            continue

        how = remap["how"]
        mapping = remap["mapping"]
        fillna = remap.get("fillna", pandas.NA)

        try:
            if how == "addend":
                right = remap["right"]
                df["ini_" + right] = df[right]
                df["addend_" + right] = df[left].map(mapping)
                df.loc[pandas.notnull(df["addend_" + right]), right] = (
                    df[right] + df["addend_" + right]
                ).fillna(fillna)

            elif how == "left":
                right = remap["right"]
                if right not in df:
                    df[right] = None
                df.loc[pandas.notnull(df[left]), right] = (
                    df[left].map(mapping).fillna(fillna)
                )

            elif how == "replace":
                df[left] = df[left].replace(mapping)

            else:
                messages.append(
                    f"ERROR: unrecognized remap method '{how}' "
                    f"in {config_section}:{config_object}."
                )

        except:
            messages.append(
                f"ERROR: unable to apply mapping '{remap}' in "
                f"{config_section}:{config_object}."
            )

    return df, messages


def parse_configuration_logic(
    df: pandas.DataFrame,
    config_section: str,
    config_object: str,
    context: Dict[str, Any],
) -> Tuple[pandas.DataFrame, List[str]]:

    obj_context = context.get(config_section, {}).get(config_object)

    if obj_context is None:
        messages = [
            (
                f"ERROR: cannot find {config_section}:{config_object} "
                f"in config file: {context['data_path']}"
            )
        ]
        return df, messages

    msg: List[str] = []
    if obj_context.get("preprocess") is None:
        return df, msg

    sections = obj_context["preprocess"]

    for section in sections:
        for directive, params in section.items():

            if directive == "joins":
                df, msg = parse_joins(
                    df, params, config_section, config_object, context, msg
                )

            if directive == "remaps":
                df, msg = parse_remaps(
                    df, params, config_section, config_object, context, msg
                )

            if directive == "expand_fields":
                df, msg = parse_expand_fields(
                    df, params, config_section, config_object, context, msg
                )

            if directive == "collapse_fields":
                df, msg = parse_collapse_fields(
                    df, params, config_section, config_object, context, msg
                )
    return df, msg
