"""Smoke tests for health check endpoints of the Commercial API."""


class TestHealthLive:
    """GET /health/live — Liveness probe (no DB required)."""

    def test_returns_200(self, client):
        response = client.get("/health/live")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "cicor-commercial-api"


class TestHealthReady:
    """GET /health/ready — Readiness probe (requires DB)."""

    def test_returns_200_when_db_healthy(self, client, mock_db_health):
        response = client.get("/health/ready")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["db_connected"] is True

    def test_returns_503_when_db_unhealthy(self, client):
        import database

        database.check_db_health.return_value = False

        response = client.get("/health/ready")

        assert response.status_code == 503
        assert response.json()["detail"] == "Base de datos no disponible"


class TestHealthStartup:
    """GET /health/startup — Startup probe."""

    def test_returns_200_when_db_healthy(self, client, mock_db_health):
        response = client.get("/health/startup")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["db_connected"] is True
