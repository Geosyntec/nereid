import pytest

from nereid.core.config import API_LATEST


@pytest.mark.parametrize(
    "query, isvalid",
    [
        ("", False),
        ("?filename=bmp_params", True),
        ("?state=state&region=region&filename=bmp_params", True),
        ("?state=state&filename=bmp_params", True),
        ("?state=state&region=sea", False),
        ("?state=wa&region=sea", False),
    ],
)
def test_endpoints(client, query, isvalid):
    url = API_LATEST + "/reference_data" + query

    response = client.get(url)

    if isvalid:
        assert response.status_code == 200
        rjson = response.json()
        assert rjson["status"].lower() == "success"

        rjsondata = rjson["data"]
        assert "state" in rjsondata
        assert "region" in rjsondata
        assert "schema" in rjsondata["filedata"]
        assert "data" in rjsondata["filedata"]

    else:
        assert response.status_code == 404
