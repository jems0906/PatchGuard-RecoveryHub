import base64
import hashlib
import hmac
import secrets
import time
from urllib.parse import urlsplit

from fastapi import Request

from app.config import settings

SESSION_COOKIE = "patchguard_session"
SESSION_MAX_AGE = 12 * 60 * 60
_ALLOWED_UNSIGNED_PATHS = {"/api/health", "/api/auth/login", "/api/auth/session"}


def _sign(payload: str) -> str:
    secret = settings.auth_session_secret.get_secret_value().encode("utf-8")
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


def create_session_token(now: int | None = None) -> str:
    issued_at = int(time.time()) if now is None else now
    payload = f"v1.{issued_at}.{secrets.token_urlsafe(24)}"
    return f"{payload}.{_sign(payload)}"


def is_valid_session_token(token: str | None, now: int | None = None) -> bool:
    if not token or not settings.auth_session_secret.get_secret_value():
        return False
    parts = token.split(".")
    if len(parts) != 4 or parts[0] != "v1":
        return False
    version, issued_at_text, nonce, supplied_signature = parts
    if not nonce:
        return False
    payload = f"{version}.{issued_at_text}.{nonce}"
    if not hmac.compare_digest(
        _sign(payload).encode("ascii"),
        supplied_signature.encode("utf-8"),
    ):
        return False
    try:
        issued_at = int(issued_at_text)
    except ValueError:
        return False
    current_time = int(time.time()) if now is None else now
    return issued_at <= current_time + 60 and current_time - issued_at <= SESSION_MAX_AGE


def valid_request_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    if not origin:
        return False
    configured_origins = {
        item.strip().rstrip("/")
        for item in settings.cors_origins.split(",")
        if item.strip()
    }
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
    scheme = forwarded_proto or request.url.scheme
    expected_origin = f"{scheme}://{request.headers.get('host', '')}".rstrip("/")
    parsed_origin = urlsplit(origin)
    if parsed_origin.scheme not in {"http", "https"} or not parsed_origin.netloc:
        return False
    return origin.rstrip("/") == expected_origin or origin.rstrip("/") in configured_origins


def is_unsigned_path(path: str) -> bool:
    return path in _ALLOWED_UNSIGNED_PATHS
