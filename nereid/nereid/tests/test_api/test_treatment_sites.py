import pytest

from nereid.api.api_v1.models import treatment_site_models


@pytest.mark.parametrize("size", [1, 3, 5])
def test_post_init_tmnt_site_params(treatment_site_responses, size):

    post_response = treatment_site_responses[size]
    assert post_response.status_code == 200
    prjson = post_response.json()
    assert treatment_site_models.TreatmentSiteResponse(**prjson)
    assert prjson["status"].lower() != "failure"
