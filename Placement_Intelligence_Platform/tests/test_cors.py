from app.main import app
from tests.asgi_client import ASGIClient


def test_cors_allows_configured_local_frontend_origin():
    response = ASGIClient(app).options(
        "/api/v1/search",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_does_not_allow_arbitrary_origins():
    response = ASGIClient(app).options(
        "/api/v1/search",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert "access-control-allow-origin" not in response.headers
