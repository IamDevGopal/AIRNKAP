from fastapi import APIRouter

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.document_routes import router as document_router
from app.api.v1.health_routes import router as health_router
from app.api.v1.knowledge_routes import router as knowledge_router
from app.api.v1.project_routes import router as project_router
from app.api.v1.research_routes import router as research_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.workspace_routes import router as workspace_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(document_router)
api_router.include_router(health_router)
api_router.include_router(knowledge_router)
api_router.include_router(project_router)
api_router.include_router(research_router)
api_router.include_router(user_router)
api_router.include_router(workspace_router)
