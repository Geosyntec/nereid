from typing import Dict, Any, Mapping, Tuple, Callable

from nereid.core import io
from nereid.src.tmnt_performance.tmnt import build_effluent_function_map
from nereid.core.units import update_unit_registry


@update_unit_registry
def effluent_function_map(
    tablename: str, context: Dict[str, Any]
) -> Mapping[Tuple[str, str], Callable]:

    df, msg = io.load_ref_data(tablename, context)

    tmnt_context = context.get("project_reference_data", {}).get(tablename, {})

    facility_column = tmnt_context.get("facility_column", "facility_type")
    pollutant_column = tmnt_context.get("pollutant_column", "pollutant")

    eff_conc_map = build_effluent_function_map(df, facility_column, pollutant_column)

    return eff_conc_map
