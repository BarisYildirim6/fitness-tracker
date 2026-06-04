from fastapi.testclient import TestClient


def test_register_login_and_current_user_flow(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "Test@Example.com", "password": "strong-password"},
    )
    assert register_response.status_code == 201
    user = register_response.json()
    assert user["email"] == "test@example.com"
    assert "hashed_password" not in user
    assert user["profile"] is None

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strong-password"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token
    assert login_response.json()["token_type"] == "bearer"

    me_response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "test@example.com"


def test_register_rejects_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )

    assert response.status_code == 422


def test_login_rejects_wrong_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong-password@example.com", "password": "strong-password"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong-password@example.com", "password": "different-password"},
    )

    assert response.status_code == 401


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "strong-password"}

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_register_with_profile_and_create_profile_after_registration(client: TestClient) -> None:
    register_with_profile_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile@example.com",
            "password": "strong-password",
            "profile": {
                "height_cm": "184.00",
                "current_weight_kg": "115.00",
                "goal": "fat loss and strength",
                "training_level": "beginner",
                "preferred_mode": "home",
                "target_weekly_weight_loss_kg": "0.50",
            },
        },
    )
    assert register_with_profile_response.status_code == 201
    assert register_with_profile_response.json()["profile"]["preferred_mode"] == "home"

    client.post(
        "/api/v1/auth/register",
        json={"email": "onboarding@example.com", "password": "strong-password"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "onboarding@example.com", "password": "strong-password"},
    )
    token = login_response.json()["access_token"]

    profile_response = client.post(
        "/api/v1/me/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "height_cm": "184.00",
            "current_weight_kg": "115.00",
            "goal": "sustainable fat loss",
            "training_level": "beginner",
            "preferred_mode": "home",
            "target_weekly_weight_loss_kg": "0.50",
        },
    )

    assert profile_response.status_code == 201
    assert profile_response.json()["goal"] == "sustainable fat loss"


def test_me_requires_valid_token(client: TestClient) -> None:
    response = client.get("/api/v1/me")

    assert response.status_code == 401
