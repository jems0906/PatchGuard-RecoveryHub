from pydantic import SecretStr

from app.auth import SESSION_MAX_AGE, create_session_token, is_valid_session_token
from app.config import settings


def enable_auth(monkeypatch):
    monkeypatch.setattr(settings, "auth_required", True)
    monkeypatch.setattr(settings, "auth_admin_username", "admin")
    monkeypatch.setattr(settings, "auth_admin_password", SecretStr("a" * 40))
    monkeypatch.setattr(settings, "auth_session_secret", SecretStr("b" * 64))


def test_api_requires_login_and_logout_revokes_cookie(client, monkeypatch):
    enable_auth(monkeypatch)
    assert client.get("/api/assets").status_code == 401
    assert client.get("/openapi.json").status_code == 401
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/auth/session").json() == {"authenticated": False}

    denied = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        headers={"Origin": "http://testserver"},
    )
    assert denied.status_code == 401
    oversized = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "x" * 1025},
        headers={"Origin": "http://testserver"},
    )
    assert oversized.status_code == 422

    logged_in = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "a" * 40},
        headers={"Origin": "http://testserver"},
    )
    assert logged_in.status_code == 200
    cookie = logged_in.cookies.get("patchguard_session")
    assert cookie
    set_cookie = logged_in.headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "samesite=strict" in set_cookie
    assert f"max-age={SESSION_MAX_AGE}" in set_cookie
    assert client.get("/api/auth/session").json() == {"authenticated": True}
    assert client.get("/api/assets").status_code == 200

    logged_out = client.post(
        "/api/auth/logout",
        headers={"Origin": "http://testserver"},
    )
    assert logged_out.status_code == 200
    assert client.get("/api/assets").status_code == 401


def test_login_rejects_untrusted_origin(client, monkeypatch):
    enable_auth(monkeypatch)
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "a" * 40},
        headers={"Origin": "https://attacker.example"},
    )
    assert response.status_code == 403


def test_login_marks_proxy_https_cookie_secure(client, monkeypatch):
    enable_auth(monkeypatch)
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "a" * 40},
        headers={
            "Origin": "https://testserver",
            "X-Forwarded-Proto": "https",
        },
    )
    assert response.status_code == 200
    assert "secure" in response.headers["set-cookie"].lower()


def test_live_frontend_origin_is_allowed_when_proxy_uses_internal_http(client, monkeypatch):
    enable_auth(monkeypatch)
    monkeypatch.setattr(settings, "auth_cookie_secure", True)
    monkeypatch.setattr(
        settings,
        "cors_origins",
        "https://frontend-production-724d2.up.railway.app",
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "a" * 40},
        headers={"Origin": "https://frontend-production-724d2.up.railway.app"},
    )
    assert response.status_code == 200
    assert "secure" in response.headers["set-cookie"].lower()


def test_login_requires_matching_username(client, monkeypatch):
    enable_auth(monkeypatch)
    wrong_username = client.post(
        "/api/auth/login",
        json={"username": "operator", "password": "a" * 40},
        headers={"Origin": "http://testserver"},
    )
    assert wrong_username.status_code == 401

    missing_username = client.post(
        "/api/auth/login",
        json={"password": "a" * 40},
        headers={"Origin": "http://testserver"},
    )
    assert missing_username.status_code == 422


def test_authenticated_mutations_require_same_origin(client, monkeypatch):
    enable_auth(monkeypatch)
    client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "a" * 40},
        headers={"Origin": "http://testserver"},
    )

    blocked = client.post("/api/assets", json={"hostname": "WEB01"})
    assert blocked.status_code == 403

    accepted = client.post(
        "/api/assets",
        json={"hostname": "WEB01"},
        headers={"Origin": "http://testserver"},
    )
    assert accepted.status_code == 201


def test_session_tokens_are_signed_and_expire(monkeypatch):
    enable_auth(monkeypatch)
    issued_at = 1_700_000_000
    token = create_session_token(now=issued_at)
    assert is_valid_session_token(token, now=issued_at + SESSION_MAX_AGE)
    assert not is_valid_session_token(token, now=issued_at + SESSION_MAX_AGE + 1)
    assert not is_valid_session_token(token + "x", now=issued_at)
    assert not is_valid_session_token(create_session_token(now=issued_at + 61), now=issued_at)
