from uuid import UUID

import pytest

from api.core.security import create_access_token

pytestmark = pytest.mark.anyio

REGISTER_PAYLOAD = {
    "email": "musah@example.com",
    "password": "s3crete-pass",
    "full_name": "Musah the Electrician",
    "phone": "+2348012345678",
    "role": "artisan",
}


async def test_register_creates_user(client) -> None:
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["email"] == "musah@example.com"
    assert body["data"]["full_name"] == REGISTER_PAYLOAD["full_name"]
    assert body["data"]["role"] == "artisan"
    assert body["data"]["is_active"] is True
    assert "password" not in body["data"] and "password_hash" not in body["data"]
    assert set(body.keys()) == {"status", "data"}


async def test_register_rejects_duplicate_email(client) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    duplicate = {**REGISTER_PAYLOAD, "email": "musah@example.com", "phone": "+2348012345679"}

    response = await client.post("/auth/register", json=duplicate)

    assert response.status_code == 409
    body = response.json()
    assert body["status"] == "error"
    assert "already registered" in body["message"]


async def test_register_rejects_duplicate_phone(client) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    duplicate = {**REGISTER_PAYLOAD, "email": "other@example.com"}

    response = await client.post("/auth/register", json=duplicate)

    assert response.status_code == 409
    assert "already registered" in response.json()["message"]


async def test_register_rejects_short_password(client) -> None:
    weak = {**REGISTER_PAYLOAD, "password": "short"}

    response = await client.post("/auth/register", json=weak)

    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert body["message"] == "Validation failed."
    assert len(body["errors"]) == 1
    assert "input" not in body["errors"][0]  # never echo submitted fields


async def test_login_returns_token(client) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/auth/login",
        json={"email": "musah@example.com", "password": "s3crete-pass"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["expires_in"] > 0
    assert isinstance(body["data"]["access_token"], str) and body["data"]["access_token"]


async def test_login_rejects_wrong_password(client) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/auth/login", json={"email": "musah@example.com", "password": "wrong-pass-1"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["message"] == "Incorrect email or password."


async def test_login_rejects_unknown_email(client) -> None:
    response = await client.post(
        "/auth/login", json={"email": "ghost@example.com", "password": "whatever-123"}
    )

    assert response.status_code == 401


async def test_me_returns_current_user(client) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    token = (
        await client.post(
            "/auth/login",
            json={"email": "musah@example.com", "password": "s3crete-pass"},
        )
    ).json()["data"]["access_token"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["data"]["email"] == "musah@example.com"


async def test_me_requires_token(client) -> None:
    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["message"] == "Not authenticated."


async def test_me_rejects_invalid_token(client) -> None:
    response = await client.get("/auth/me", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401


async def test_me_rejects_token_of_deleted_user(client) -> None:
    """A validly-signed token for a user id that does not exist must be rejected."""
    phantom_token = create_access_token(UUID("00000000-0000-0000-0000-000000000009"))

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {phantom_token}"})

    assert response.status_code == 401
