from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import SESSION_COOKIE, is_unsigned_path, is_valid_session_token, valid_request_origin
from app.api.routes.api import api_router
from app.config import settings
from app.database import SessionLocal, engine
from app.models import Base
from app.seed import seed_demo_data

@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auth_required:
        if len(settings.auth_admin_password.get_secret_value()) < 32:
            raise RuntimeError(
                "AUTH_ADMIN_PASSWORD must contain at least 32 characters when authentication is enabled"
            )
        if len(settings.auth_session_secret.get_secret_value()) < 32:
            raise RuntimeError(
                "AUTH_SESSION_SECRET must contain at least 32 characters when authentication is enabled"
            )
    Base.metadata.create_all(bind=engine)
    if settings.seed_demo_data:
        with SessionLocal() as db:
            seed_demo_data(db)
    yield


app = FastAPI(
    title="PatchGuard RecoveryHub API",
    description="Infrastructure compliance tracking for patching, vulnerabilities, Active Directory, VMware, and backups.",
    version="1.0.0",
    lifespan=lifespan,
)
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def require_authenticated_session(request: Request, call_next):
    if not settings.auth_required or is_unsigned_path(request.url.path):
        if (
            request.url.path == "/api/auth/login"
            and request.method == "POST"
            and not valid_request_origin(request)
        ):
            return JSONResponse(
                status_code=403,
                content={"detail": "Request origin is not allowed"},
            )
        return await call_next(request)

    if not is_valid_session_token(request.cookies.get(SESSION_COOKIE)):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"},
        )
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not valid_request_origin(request):
        return JSONResponse(
            status_code=403,
            content={"detail": "Request origin is not allowed"},
        )
    return await call_next(request)


app.include_router(api_router)
