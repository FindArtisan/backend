from datetime import datetime

from fastapi.testclient import TestClient

from api.core.config import settings
from api.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["healthy"] is True
    assert body["service"] == settings.PROJECT_NAME
    assert body["version"] == settings.VERSION
    # timestamp should parse as an ISO datetime
    datetime.fromisoformat(body["timestamp"].replace("Z", "+00:00"))
