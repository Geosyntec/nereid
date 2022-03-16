import matplotlib
import pytest

from nereid.core.config import settings

matplotlib.use("agg")


@pytest.mark.parametrize(
    "query, isvalid",
    [
        ("", False),
        ("?filename=bmp_params.json", True),
        ("?state=state&region=region&filename=bmp_params.json", True),
        (
            "?state=state&region=region&filename=nomographs/100_LAGUNABEACH_volume_nomo.csv",
            True,
        ),
        ("?state=state&filename=bmp_params.json", True),
        ("?state=state&region=sea", False),
        ("?state=wa&region=sea", False),
    ],
)
def test_ref_data(client, query, isvalid):
    url = settings.API_LATEST + "/reference_data" + query

    response = client.get(url)

    if isvalid:
        assert response.status_code == 200
        rjson = response.json()
        assert rjson["status"].lower() == "success"

        rjsondata = rjson["data"]
        assert "state" in rjsondata
        assert "region" in rjsondata
        # assert "schema" in rjsondata["filedata"]
        assert len(rjsondata["filedata"]) > 0

    else:
        assert response.status_code == 400


@pytest.mark.parametrize(
    "query, isvalid",
    [
        ("", False),
        ("?filename=bmp_params.json", True),
        ("?state=state&region=region&filename=bmp_params.json", True),
        (
            "?state=state&region=region&filename=nomographs/100_LAGUNABEACH_volume_nomo.csv",
            True,
        ),
        ("?state=state&filename=bmp_params.json", True),
        ("?state=state&region=sea", False),
        ("?state=wa&region=sea", False),
    ],
)
def test_ref_data_file(client, query, isvalid):
    url = settings.API_LATEST + "/reference_data_file" + query

    response = client.get(url)

    if isvalid:
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@pytest.mark.parametrize(
    "table, isvalid",
    [
        ("", False),
        ("met_table", True),
        ("met_tables", False),
    ],
)
def test_ref_data_table(client, table, isvalid):
    url = settings.API_LATEST + f"/reference_data/{table}"

    response = client.get(url)

    if isvalid:
        assert response.status_code == 200
        rjson = response.json()
        assert rjson["status"].lower() == "success"

        rjsondata = rjson["data"]
        assert "state" in rjsondata
        assert "region" in rjsondata
        assert "data" in rjsondata
        assert table == rjsondata["table"]

    else:
        assert response.status_code == 400


@pytest.mark.parametrize(
    "nomo, type, status_code",
    [
        ("", "", 400),
        ("nomographs/100_LAGUNABEACH_volume_nomo.csv", "surface", 200),
        ("nomographs/100_LAGUNABEACH_flow_nomo.csv", "surface", 200),
        ("nomographs/100_LAGUNABEACH_volume_nomo.csv", "other", 200),
        ("nomographs/100_LAGUNABEACH_flow_nomo.csv", "other", 200),
    ],
)
def test_ref_data_nomograph(client, nomo, type, status_code):
    url = settings.API_LATEST + f"/reference_data/nomograph?filename={nomo}&type={type}"
    response = client.get(url)
    assert response.status_code == status_code
