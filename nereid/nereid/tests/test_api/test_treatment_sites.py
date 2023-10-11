import pytest

from nereid.models import treatment_site_models


@pytest.mark.parametrize("size", [1, 3, 5])
def test_post_init_tmnt_site_params(client, treatment_site_responses, size):
    post_response = treatment_site_responses[size]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert treatment_site_models.TreatmentSiteResponse(**prjson)
    assert prjson["status"].lower() != "failure"

    result_route = prjson.get("result_route")

    if result_route:
        get_response = client.get(result_route)
        assert get_response.status_code == 200
        grjson = get_response.json()

        assert treatment_site_models.TreatmentSiteResponse(**grjson)
        assert grjson["task_id"] == prjson["task_id"]
        assert grjson["result_route"] == prjson["result_route"]
        assert grjson["status"].lower() != "failure"
