"""
Tests for Phase 1 authentication + role guard.

No live MySQL or Redis required — everything runs in-process via the
`fake_db` / `fake_redis` fixtures in conftest.py.
"""

import pytest


# --------------------------------------------------------------------- #
# /api/auth/register                                                    #
# --------------------------------------------------------------------- #

class TestRegister:
    def test_student_register_returns_201(self, client):
        r = client.post("/api/auth/register", json={
            "username": "alice",
            "email": "alice@test.com",
            "password": "pw12345",
            "role": "student",
        })
        assert r.status_code == 201
        body = r.get_json()
        assert body["data"]["role"] == "student"
        assert body["data"]["username"] == "alice"
        assert "password_hash" not in body["data"]

    def test_missing_fields_returns_400(self, client):
        r = client.post("/api/auth/register", json={"username": "x"})
        assert r.status_code == 400
        assert r.get_json()["error"] == "missing_fields"

    def test_admin_role_rejected(self, client):
        r = client.post("/api/auth/register", json={
            "username": "x", "email": "x@x.com",
            "password": "pw", "role": "admin",
        })
        assert r.status_code == 400
        assert r.get_json()["error"] == "invalid_role"

    def test_duplicate_username_returns_409(self, client):
        payload = {
            "username": "bob", "email": "bob@test.com",
            "password": "pw12345", "role": "student",
        }
        assert client.post("/api/auth/register", json=payload).status_code == 201
        dup = client.post("/api/auth/register", json={**payload, "email": "b2@test.com"})
        assert dup.status_code == 409


# --------------------------------------------------------------------- #
# /api/auth/login                                                       #
# --------------------------------------------------------------------- #

class TestLogin:
    def _register(self, client):
        return client.post("/api/auth/register", json={
            "username": "carol", "email": "carol@test.com",
            "password": "pw12345", "role": "lecturer",
        })

    def test_login_success_returns_token(self, client):
        self._register(client)
        r = client.post("/api/auth/login", json={
            "username": "carol", "password": "pw12345",
        })
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["token"]
        assert data["user"]["role"] == "lecturer"

    def test_login_wrong_password_returns_401(self, client):
        self._register(client)
        r = client.post("/api/auth/login", json={
            "username": "carol", "password": "wrong",
        })
        assert r.status_code == 401

    def test_login_unknown_user_returns_401(self, client):
        r = client.post("/api/auth/login", json={
            "username": "ghost", "password": "pw12345",
        })
        assert r.status_code == 401


# --------------------------------------------------------------------- #
# JWT middleware + role guard                                           #
# --------------------------------------------------------------------- #

class TestJWTAndRoleGuard:
    def test_missing_token_returns_401(self, client):
        r = client.get("/api/users/me")
        assert r.status_code == 401

    def test_malformed_token_returns_401(self, client):
        r = client.get("/api/users/me", headers={"Authorization": "Bearer not-a-jwt"})
        assert r.status_code == 401

    def test_me_returns_profile(self, client, auth_header):
        client.post("/api/auth/register", json={
            "username": "dave", "email": "d@t.com",
            "password": "pw12345", "role": "student",
        })
        # Registered user gets id=1 in the fake DB.
        r = client.get("/api/users/me", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"]["username"] == "dave"

    def test_student_cannot_list_all_users(self, client, auth_header):
        r = client.get("/api/users", headers=auth_header(1, "student"))
        assert r.status_code == 403

    def test_admin_can_list_all_users(self, client, auth_header, fake_db):
        # Seed an admin row so get_all() returns something.
        fake_db.users[1] = {
            "id": 1, "username": "root", "email": "r@t.com",
            "password_hash": "x", "role": "admin",
            "created_at": "2026-04-10T00:00:00",
        }
        fake_db.next_id = 2
        r = client.get("/api/users", headers=auth_header(1, "admin"))
        assert r.status_code == 200
        body = r.get_json()
        assert any(u["role"] == "admin" for u in body["data"])


# --------------------------------------------------------------------- #
# Admin create-user                                                     #
# --------------------------------------------------------------------- #

class TestAdminCreateUser:
    def test_non_admin_forbidden(self, client, auth_header):
        r = client.post(
            "/api/auth/admin/create-user",
            headers=auth_header(1, "student"),
            json={"username": "x", "email": "x@x.com", "password": "pw", "role": "admin"},
        )
        assert r.status_code == 403

    def test_admin_can_create_any_role(self, client, auth_header):
        r = client.post(
            "/api/auth/admin/create-user",
            headers=auth_header(1, "admin"),
            json={
                "username": "newadmin", "email": "na@t.com",
                "password": "pw12345", "role": "admin",
            },
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["role"] == "admin"
