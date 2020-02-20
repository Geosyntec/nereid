from typing import Dict, Any
from pathlib import Path
from copy import deepcopy

import pandas

from nereid.core.io import load_ref_data


def load_land_surface_data(context: Dict[str, Any]) -> pandas.DataFrame:

    data_path = Path(context["data_path"])

    lst_context = context.get("project_reference_data", {}).get(
        "land_surface_table", {}
    )

    filepath = data_path / lst_context["file"]
    ref_table = load_ref_data(filepath)

    if "expand_fields" in lst_context:
        for field_params in lst_context["expand_fields"]:
            field = field_params.get("field")
            sep = field_params.get("sep", "_")
            cols = field_params.get("new_column_names", [])

            for ix, col in enumerate(cols):
                ref_table[col] = ref_table[field].str.split(sep).str[ix]

    if "joins" in lst_context:
        for j in deepcopy(lst_context["joins"]):
            tablename = j.pop("other")
            filepath = data_path / (
                context.get("project_reference_data", {})
                .get(tablename, {})
                .get("file", None)
            )
            if filepath.exists():
                table = load_ref_data(filepath)
                ref_table = ref_table.merge(table, **j)

    return ref_table
