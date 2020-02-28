import pytest


@pytest.mark.parametrize(
    "route, title_contents",
    [("/docs", "swagger"), ("/redoc", "redoc"), ("/config", "test")],
)
def test_docs(client, route, title_contents):
    response = client.get(route)
    assert response.status_code == 200
    assert title_contents in response.content.decode().lower()
