from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.security import verify_password
from app.database import SessionLocal
from app.models.user import User
from main import app


def test_register_and_login():
    username = f"test_{uuid4().hex}"
    password = "IntegrationTest123!"
    registration = {
        "username": username,
        "email": f"{username}@example.com",
        "password": password,
    }

    with TestClient(app) as client:
        response = client.post("/users/register", json=registration)
        assert response.status_code == 201, response.text
        user_id = response.json()["id"]
        expected_user = {
            "id": user_id,
            "username": username,
            "email": registration["email"],
        }
        assert response.json() == expected_user

        with SessionLocal() as db:
            user = db.get(User, user_id)
            assert user is not None
            assert user.email == registration["email"]
            assert user.password_hash != password
            assert verify_password(password, user.password_hash)

        duplicate = client.post("/users/register", json=registration)
        assert duplicate.status_code == 409, duplicate.text

        login = client.post(
            "/users/login", json={"username": username, "password": password}
        )
        assert login.status_code == 200, login.text
        assert login.json() == expected_user

        failed_login = client.post(
            "/users/login",
            json={"username": username, "password": "WrongPassword123!"},
        )
        assert failed_login.status_code == 401
        assert failed_login.json()["detail"] == "Invalid username or password."