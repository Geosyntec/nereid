from typing import Any, Callable

from nereid.core import io
from nereid.core.units import update_reg_from_context
from nereid.src.tmnt_performance.tmnt import build_effluent_function_map


def effluent_function_map(
    tablename: str, context: dict[str, Any]
) -> dict[Any, Callable]:
    update_reg_from_context(context=context)

    tmnt_context = context.get("project_reference_data", {}).get(tablename, {})
    _default = {}

    if not tmnt_context:
        return _default

    df, msg = io.load_ref_data(tablename, context)

    if df is None:  # pragma: no cover
        return _default

    facility_column = tmnt_context.get("facility_column", "facility_type")
    pollutant_column = tmnt_context.get("pollutant_column", "pollutant")

    eff_conc_map = build_effluent_function_map(df, facility_column, pollutant_column)

    return eff_conc_map
