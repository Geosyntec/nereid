from typing import Dict, Any
from pathlib import Path
import pandas

from nereid.core.io import load_file


def _load_land_surface_reference_file(filepath: str) -> pandas.DataFrame:

    ls_json = load_file(filepath)

    ref_table = pandas.read_json(ls_json, orient="table")

    return ref_table


def load_land_surface_data(context: Dict[str, Any]) -> pandas.DataFrame:

    lst_context = context.get("project_reference_data", {}).get(
        "land_surface_table", {}
    )

    filepath = Path(context["data_path"]) / lst_context["file"]

    ref_table = _load_land_surface_reference_file(filepath)

    for field_params in lst_context.get("expand_fields", []):
        field = field_params.get("field")
        sep = field_params.get("sep", "_")
        cols = field_params.get("new_column_names", [])

        for ix, col in enumerate(cols):
            ref_table[col] = ref_table[field].str.split(sep).str[ix]

    return ref_table
