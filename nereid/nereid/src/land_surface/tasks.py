from typing import Any, Dict, List

import pandas

from nereid.core.io import parse_configuration_logic
from nereid.core.units import update_unit_registry
from nereid.src.land_surface.loading import (
    detailed_loading_results,
    summary_loading_results,
)
from nereid.src.wq_parameters import init_wq_parameters


@update_unit_registry
def land_surface_loading(
    land_surfaces: Dict[str, Any], details: bool, context: Dict[str, Any]
) -> Dict[str, List]:
    """computes loading for volume runoff and pollutants for each land
    surface 'sliver' and aggregates values for each node. Returning results
    for the slivers is toggled by the `details` kwarg. if 'true' the resonse
    includes a 'details' key with the sliver loading. the 'summary' values
    aggregate the load to each node_id, and are always returned.
    """

    response: Dict[str, Any] = {"errors": []}

    land_surface_list = land_surfaces.get("land_surfaces") or []

    try:
        if land_surface_list:  # pragma: no branch
            df = pandas.DataFrame(land_surface_list)
            df["imp_pct"] = 100 * df["imp_area_acres"] / df["area_acres"]

            df, messages = parse_configuration_logic(
                df=df,
                config_section="api_recognize",
                config_object="land_surfaces",
                context=context,
            )

            # TODO: add validator function to ensure config & request are complete.

            if len(messages) > 0:
                response["errors"].extend(messages)

            wet_weather_parameters = init_wq_parameters(
                "land_surface_emc_table", context
            )
            dry_weather_parameters = init_wq_parameters(
                "dry_weather_land_surface_emc_table", context
            )

            seasons = (
                context.get("project_reference_data", {})
                .get("dry_weather_flow_table", {})
                .get("seasons", {})
            )

            detailed_results = detailed_loading_results(
                df,
                wet_weather_parameters,
                dry_weather_parameters,
                seasons,
            )
            summary_results = summary_loading_results(
                detailed_results,
                wet_weather_parameters,
                dry_weather_parameters,
                season_names=seasons.keys(),
            )

            response["summary"] = summary_results.fillna(0).to_dict(orient="records")

            if details:
                response["details"] = detailed_results.fillna(0).to_dict(
                    orient="records"
                )
        else:  # pragma: no cover
            response["errors"].append("ERROR: no land surface input data provided.")

    except Exception as e:  # pragma: no cover
        response["errors"].append(str(e))

    return response
