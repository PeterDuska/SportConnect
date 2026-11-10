import os
import tempfile
from pathlib import Path

test_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(test_dir.name) / "test.db")

from fastapi.testclient import TestClient
from main import app, engine


def test_auth_lifecycle():
    with TestClient(app) as client:
        headers = {"X-Requested-With": "WTaM"}
        account = {"name": "Test User", "email": "test@example.com", "password": "long-password-123"}
        assert client.get("/api/auth/me").status_code == 401
        assert client.post("/api/auth/register", json=account).status_code == 403
        response = client.post("/api/auth/register", json=account, headers=headers)
        assert response.status_code == 201
        assert "httponly" in response.headers["set-cookie"].lower()
        csrf = response.json()["csrf_token"]
        token = client.cookies.get("wtam_session")
        assert "password" not in response.json()["user"]
        assert client.get("/api/auth/me").json()["user"]["email"] == account["email"]
        assert client.post("/api/auth/register", json=account, headers=headers).status_code == 409
        assert client.post("/api/auth/logout", headers=headers).status_code == 403
        assert client.post("/api/auth/logout", headers={**headers, "X-CSRF-Token": csrf}).status_code == 204
        client.cookies.set("wtam_session", token)
        assert client.get("/api/auth/me").status_code == 401
        client.cookies.clear()
        assert client.post("/api/auth/login", json={**account, "password": "wrong"}, headers=headers).status_code == 401
        assert client.post("/api/auth/login", json=account, headers=headers).status_code == 200
        assert client.get("/api/auth/me").status_code == 200
    engine.dispose()
