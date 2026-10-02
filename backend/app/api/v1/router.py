"""API v1 router — aggregates all route modules."""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.projects import router as projects_router
from app.api.v1.endpoints.sources import router as sources_router
from app.api.v1.endpoints.visualizations import router as visualizations_router
from app.api.v1.endpoints.agents import router as agents_router
from app.api.v1.endpoints.collaboration import router as collaboration_router
from app.api.v1.endpoints.exports import router as exports_router
from app.api.v1.endpoints.gods_eye import router as gods_eye_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_v1_router.include_router(sources_router, prefix="/sources", tags=["sources"])
api_v1_router.include_router(visualizations_router, prefix="/visualizations", tags=["visualizations"])
api_v1_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_v1_router.include_router(collaboration_router, prefix="/collaboration", tags=["collaboration"])
api_v1_router.include_router(exports_router, prefix="/exports", tags=["exports"])
api_v1_router.include_router(gods_eye_router, prefix="/gods-eye", tags=["gods-eye"])
