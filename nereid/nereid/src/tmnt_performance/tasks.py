from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from nereid.core import io
from nereid.core.units import update_unit_registry
from nereid.src.tmnt_performance.tmnt import build_effluent_function_map


@update_unit_registry
def effluent_function_map(
    tablename: str, context: Dict[str, Any]
) -> Optional[Mapping[Tuple[str, str], Callable]]:

    tmnt_context = context.get("project_reference_data", {}).get(tablename, {})

    if not tmnt_context:
        return None

    df, msg = io.load_ref_data(tablename, context)

    if df is None:  # pragma: no cover
        return None

    facility_column = tmnt_context.get("facility_column", "facility_type")
    pollutant_column = tmnt_context.get("pollutant_column", "pollutant")

    eff_conc_map = build_effluent_function_map(df, facility_column, pollutant_column)

    return eff_conc_map
