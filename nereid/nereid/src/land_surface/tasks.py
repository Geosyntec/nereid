from typing import List, Dict, Any

import pandas

from nereid.core.io import parse_configuration_logic
from nereid.core.units import update_unit_registry
from nereid.src.wq_parameters import init_wq_parameters
from nereid.src.land_surface.loading import (
    detailed_loading_results,
    summary_loading_results,
)


@update_unit_registry
def land_surface_loading(
    land_surfaces: Dict[str, Any], details: bool, context: Dict[str, Any]
) -> Dict[str, List]:

    df = pandas.DataFrame(land_surfaces["land_surfaces"])
    df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]

    response: Dict[str, Any] = {}
    response["errors"] = []

    df, messages = parse_configuration_logic(
        df=df,
        config_section="api_recognize",
        config_object="land_surfaces",
        context=context,
    )

    if len(messages) > 0:
        response["errors"].extend(messages)

    wet_weather_parameters = init_wq_parameters("land_surface_emc_table", context)
    dry_weather_parameters = init_wq_parameters(
        "dry_weather_land_surface_emc_table", context
    )

    seasons = (
        context.get("project_reference_data", {})
        .get("dry_weather_flow_table", {})
        .get("seasons", {})
    )

    detailed_results = detailed_loading_results(
        df, wet_weather_parameters, dry_weather_parameters, seasons,
    )
    summary_results = summary_loading_results(
        detailed_results,
        wet_weather_parameters,
        dry_weather_parameters,
        season_names=seasons.keys(),
    )

    response["summary"] = summary_results.fillna(0).to_dict(orient="records")

    if details:
        response["details"] = detailed_results.fillna(0).to_dict(orient="records")

    return response
