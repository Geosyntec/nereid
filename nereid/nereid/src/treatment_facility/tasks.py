from typing import Dict, Any, List

import pandas

from nereid.core.units import update_unit_registry
from nereid.core.io import parse_configuration_logic
from nereid.src.treatment_facility.constructors import build_treatment_facility_nodes
from nereid.api.api_v1.models.treatment_facility_models import (
    validate_treatment_facility_models,
)


@update_unit_registry
def initialize_treatment_facilities(
    treatment_facilities: Dict[str, List[Dict[str, Any]]],
    pre_validated: bool,
    context: Dict[str, Any],
) -> Dict[str, Any]:

    treatment_facility_list = treatment_facilities["treatment_facilities"]
    if not pre_validated:
        tmnt_model = validate_treatment_facility_models(
            treatment_facility_list, context
        )
        treatment_facility_list = [m.dict() for m in tmnt_model]

    df, messages = parse_configuration_logic(
        df=pandas.DataFrame(treatment_facility_list),
        config_section="api_recognize",
        config_object="treatment_facility",
        context=context,
    )

    treatment_facility_nodes = build_treatment_facility_nodes(df=df)

    response: Dict[str, Any] = {"errors": []}

    if len(messages) > 0:
        response["errors"] = messages

    response["treatment_facilities"] = treatment_facility_nodes

    return response
