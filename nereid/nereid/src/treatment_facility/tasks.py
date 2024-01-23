from typing import Any

import pandas

from nereid.core.io import parse_configuration_logic
from nereid.core.units import update_reg_from_context
from nereid.models.treatment_facility_models import (
    validate_treatment_facility_models,
)
from nereid.src.treatment_facility.constructors import build_treatment_facility_nodes


def initialize_treatment_facilities(
    treatment_facilities: dict[str, list[dict[str, Any]]],
    pre_validated: bool,
    context: dict[str, Any],
) -> dict[str, Any]:
    update_reg_from_context(context=context)
    response: dict[str, Any] = {"errors": []}

    try:
        treatment_facility_list = treatment_facilities.get("treatment_facilities") or []
        if not pre_validated:
            treatment_facility_list = validate_treatment_facility_models(
                treatment_facility_list, context
            )

        df, messages = parse_configuration_logic(
            df=pandas.DataFrame(treatment_facility_list),
            config_section="api_recognize",
            config_object="treatment_facility",
            context=context,
        )

        treatment_facility_nodes = build_treatment_facility_nodes(df=df)

        if len(messages) > 0:
            response["errors"] = messages

        response["treatment_facilities"] = treatment_facility_nodes

    except Exception as e:  # pragma: no cover
        response["errors"].append(str(e))

    return response
