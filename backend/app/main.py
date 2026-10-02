from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.api import api_router
from app.config import settings
from app.database import SessionLocal, engine
from app.models import Base
from app.seed import seed_demo_data

@asynccontextmanager
async def lifespan(_: FastAPI):
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
app.include_router(api_router)
