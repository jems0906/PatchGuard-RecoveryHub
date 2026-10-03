import hmac
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, SecretStr, StringConstraints

from app.auth import (
    SESSION_COOKIE,
    SESSION_MAX_AGE,
    create_session_token,
    is_valid_session_token,
    valid_request_origin,
)
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    password: Annotated[SecretStr, StringConstraints(max_length=1024)]


@router.get("/session")
def get_session(request: Request) -> dict[str, bool]:
    return {
        "authenticated": (
            not settings.auth_required
            or is_valid_session_token(request.cookies.get(SESSION_COOKIE))
        )
    }


@router.post("/login")
def login(payload: LoginRequest, request: Request, response: Response) -> dict[str, bool]:
    if not settings.auth_required:
        raise HTTPException(status_code=404, detail="Login is not enabled")
    if not valid_request_origin(request):
        raise HTTPException(status_code=403, detail="Request origin is not allowed")

    expected_password = settings.auth_admin_password.get_secret_value()
    supplied_password = payload.password.get_secret_value()
    if not hmac.compare_digest(
        supplied_password.encode("utf-8"),
        expected_password.encode("utf-8"),
    ):
        logger.warning("auth.login result=denied")
        raise HTTPException(status_code=401, detail="Invalid password")

    secure_cookie = settings.auth_cookie_secure or (
        request.url.scheme == "https"
        or request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip() == "https"
    )
    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_token(),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=secure_cookie,
        samesite="strict",
        path="/",
    )
    logger.info("auth.login result=accepted")
    return {"authenticated": True}


@router.post("/logout")
def logout(request: Request, response: Response) -> dict[str, bool]:
    if not valid_request_origin(request):
        raise HTTPException(status_code=403, detail="Request origin is not allowed")
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=settings.auth_cookie_secure
        or (
            request.url.scheme == "https"
            or request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip()
            == "https"
        ),
        samesite="strict",
        path="/",
    )
    logger.info("auth.logout")
    return {"authenticated": False}
