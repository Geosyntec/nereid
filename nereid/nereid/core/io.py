import logging
from collections import defaultdict
from copy import deepcopy
from functools import cache
from pathlib import Path
from typing import Any, TypeAlias

import numpy
import orjson as json
import pandas
import yaml

logger = logging.getLogger("nereid.core")

PathType: TypeAlias = Path | str


@cache
def _load_file(filepath: PathType) -> bytes:
    """returns bytes for redis cache compatibility"""
    fp = Path(filepath)
    return fp.read_bytes()


def load_file(filepath: PathType) -> str:
    """wrapper to ensure the cache is called with an absolute path"""
    contents: str = _load_file(Path(filepath).resolve()).decode()
    return contents


def load_cfg(filepath: PathType) -> dict[str, Any]:
    """load cached yaml file"""
    f = load_file(filepath)
    contents: dict[str, Any] = yaml.safe_load(f)
    return contents


def load_multiple_cfgs(files: list[PathType]) -> dict[str, Any]:
    """load and combine multiple cached config files"""
    conf: dict[str, Any] = {}
    for file in files:
        conf.update(load_cfg(file))
    return conf


def load_json(filepath: PathType) -> dict[str, Any]:
    """load cached json file"""
    f = load_file(filepath)
    contents: dict[str, Any] = json.loads(f)
    return contents


@cache
def _load_table(filepath: PathType) -> pandas.DataFrame:
    ref_table = pandas.read_json(filepath, orient="table", typ="frame")
    return ref_table


def load_table(filepath: PathType) -> pandas.DataFrame:
    return _load_table(Path(filepath).resolve()).copy()


def load_ref_data(
    tablename: str, context: dict
) -> tuple[pandas.DataFrame | None, list[str]]:
    data_path = Path(context["data_path"])
    project_reference_data = context.get("project_reference_data", {})

    if tablename not in project_reference_data:
        return None, [
            f"Warning: no '{tablename}' in context[project_reference_data] section"
        ]

    table_context = project_reference_data.get(tablename, {})

    if "file" not in table_context:  # pragma: no cover
        return None, [
            f"Warning: no file to load from {tablename} in context[project_reference_data] section"
        ]

    filepath = data_path / table_context["file"]
    ref_table = load_table(filepath)

    df, msg = parse_configuration_logic(
        df=ref_table,
        config_section="project_reference_data",
        config_object=tablename,
        context=context,
    )

    return df, msg


def parse_expand_fields(
    df: pandas.DataFrame,
    params: list[dict[str, Any]],
    config_section: str,
    config_object: str,
    context: dict[str, Any],
    messages: list[str],
) -> tuple[pandas.DataFrame, list[str]]:
    for f in deepcopy(params):
        try:
            field = f.get("field")
            if field is None:  # pragma: no cover
                messages.append(
                    f"no field in {config_section}:{config_object} for instructions {f}"
                )
                continue
            sep = f.get("sep", "_")
            cols = f.get("new_column_names", [])

            for ix, col in enumerate(cols):
                df[col] = df[field].str.split(sep).str[ix]
        except Exception:
            _msg = (
                f"unable to expand fields in {config_section}:{config_object} "
                f"for instructions {f}"
            )
            messages.append(_msg)
            logger.exception(_msg, stack_info=True)

    return df, messages


def parse_collapse_fields(
    df: pandas.DataFrame,
    params: list[dict[str, Any]],
    config_section: str,
    config_object: str,
    context: dict[str, Any],
    messages: list[str],
) -> tuple[pandas.DataFrame, list[str]]:
    for f in deepcopy(params):
        try:
            field = f.get("new_column_name")
            sep = f.get("sep", "_")
            cols = f.get("fields", [])

            if field is None:  # pragma: no cover
                messages.append(
                    f"unable to expand fields in {config_section}:{config_object} "
                    f"for instructions {f}"
                )
                continue

            df[field] = df[cols[0]].astype(str)
            for col in cols[1:]:
                df[field] = df[field] + sep + df[col].astype(str)

        except Exception:
            messages.append(
                f"unable to expand fields in {config_section}:{config_object} "
                f"for instructions {f}"
            )

    return df, messages


def parse_joins(
    df: pandas.DataFrame,
    params: list[dict[str, Any]],
    config_section: str,
    config_object: str,
    context: dict[str, Any],
    messages: list[str],
) -> tuple[pandas.DataFrame, list[str]]:
    df_input = df.copy()

    for j in deepcopy(params):
        tablename = j.pop("other", "ERROR: key 'other' is required")
        fuzzy_on = j.pop("fuzzy_on", None)

        try:
            table, msg = load_ref_data(tablename, context)
            messages.extend(msg)
            if table is None:
                continue

            df = df.merge(table, **j)

            if (fuzzy_on is not None) and (not all(df["_merge"] == "both")):
                matched = df.loc[df["_merge"] == "both"].copy()
                matched["_on"] = j.get("left_on")

                missing = (
                    df_input.loc[df["_merge"] != "both"].copy().reset_index(drop=True)
                )

                patches = [matched]
                for fuzzy_key in fuzzy_on:
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
                        f"Warning: Some data from {tablename} failed the requested join '{j}' to "
                        f"reference data in {config_section}:{config_object}."
                    )
                    if "warnings" not in df:
                        df["warnings"] = ""
                    df.loc[df["_merge"] != "both", "warnings"] += (
                        f"Warning: unable join '{j['left_on']}' from {tablename} to '{j['right_on']}' "
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
    params: list[dict[str, Any]],
    config_section: str,
    config_object: str,
    context: dict[str, Any],
    messages: list[str],
) -> tuple[pandas.DataFrame, list[str]]:
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
        fillna = remap.get("fillna", numpy.nan)

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

                def default(d=fillna):  # use def for linter rather than lambda
                    return d

                m = defaultdict(default, mapping)
                new_c = df[left].map(m)
                df[right] = numpy.where(pandas.notnull(df[left]), new_c, df[right])

            elif how == "replace":
                df[left] = df[left].replace(mapping)

            else:
                messages.append(
                    f"ERROR: unrecognized remap method '{how}' "
                    f"in {config_section}:{config_object}."
                )

        except Exception:
            _msg = (
                f"ERROR: unable to apply method '{how}' while mapping '{remap}' in "
                f"{config_section}:{config_object}."
            )
            messages.append(_msg)
            logger.exception(_msg, stack_info=True)

    return df, messages


def parse_configuration_logic(
    df: pandas.DataFrame,
    config_section: str,
    config_object: str,
    context: dict[str, Any],
) -> tuple[pandas.DataFrame, list[str]]:
    obj_context = context.get(config_section, {}).get(config_object)

    if obj_context is None:
        messages = [
            (
                f"ERROR: cannot find {config_section}:{config_object} "
                f"in config file: {context['data_path']}"
            )
        ]
        return df, messages

    msg: list[str] = []
    if obj_context.get("preprocess") is None:
        return df, msg

    sections = obj_context["preprocess"]

    ops = {
        "joins": parse_joins,
        "remaps": parse_remaps,
        "expand_fields": parse_expand_fields,
        "collapse_fields": parse_collapse_fields,
    }

    for section in sections:
        for directive, params in section.items():
            func = ops.get(directive)
            if func:  # pragma: no branch
                df, msg = func(df, params, config_section, config_object, context, msg)

    return df, msg
