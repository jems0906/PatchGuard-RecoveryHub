from fastapi import APIRouter

from app.api.routes import active_directory, assets, auth, backups, compliance, health, imports, patches, vulnerabilities, virtualization

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(assets.router)
api_router.include_router(patches.router)
api_router.include_router(vulnerabilities.router)
api_router.include_router(active_directory.router)
api_router.include_router(virtualization.router)
api_router.include_router(backups.router)
api_router.include_router(compliance.router)
api_router.include_router(imports.router)
