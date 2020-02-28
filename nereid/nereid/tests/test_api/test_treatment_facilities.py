import pytest

from nereid.api.api_v1.models import treatment_facility_models
from nereid.core import config


names = [
    i.schema()["title"] for i in treatment_facility_models.TREATMENT_FACILITY_MODELS
]


@pytest.mark.parametrize("key", names)
def test_post_init_tmnt_facility_params(treatment_facility_responses, key):

    post_response = treatment_facility_responses[key]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert treatment_facility_models.TreatmentFacilitiesResponse(**prjson)
    assert prjson["status"].lower() != "failure"


@pytest.mark.skipif(config.NEREID_FORCE_FOREGROUND, reason="tasks ran in foreground")
@pytest.mark.parametrize("key", names)
def test_get_init_tmnt_facility_params(client, treatment_facility_responses, key):

    post_response = treatment_facility_responses[key]

    prjson = post_response.json()
    result_route = prjson["result_route"]

    get_response = client.get(result_route)
    assert get_response.status_code == 200

    grjson = get_response.json()
    assert treatment_facility_models.TreatmentFacilitiesResponse(**prjson)
    assert grjson["task_id"] == prjson["task_id"]
    assert grjson["result_route"] == prjson["result_route"]
    assert grjson["status"].lower() != "failure"

    if grjson["status"].lower() == "success":  # pragma: no branch
        for msg in grjson["data"].get("errors") or []:
            assert "ERROR" not in msg
