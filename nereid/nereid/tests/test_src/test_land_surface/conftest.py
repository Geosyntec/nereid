from copy import deepcopy
import pytest

from nereid.core.utils import get_request_context


@pytest.fixture
def land_surface_data_contexts():

    cx1 = get_request_context()

    cx2 = deepcopy(cx1)
    cx2["project_reference_data"]["land_surface_table"].pop("joins")

    cx3 = deepcopy(cx2)
    cx3["project_reference_data"]["land_surface_table"].pop("expand_fields")

    cx4 = deepcopy(cx1)
    cx4["project_reference_data"]["land_surface_emc_table"]["file"] = r"¯\_(ツ)_/¯"

    cx5 = deepcopy(cx1)
    cx5["project_reference_data"]["land_surface_emc_table"].pop("parameters")

    keys = [
        "default",
        "land_surface_table_no_joins",
        "land_surface_table_no_joins_no_expanded_fields",
        "land_surface_emc_table_dne",
        "land_surface_emc_table_no_params",
    ]

    values = [cx1, cx2, cx3, cx4, cx5]

    return {k: v for k, v in zip(keys, values)}
