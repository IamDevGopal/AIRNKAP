import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.config.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.middlewares import RateLimitMiddleware, SecurityHeadersMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging()
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.app_debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
    app.add_middleware(
        RateLimitMiddleware,
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    register_exception_handlers(app)

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} is running"}

    logger.info("Application initialized with config: %s", settings.safe_summary())

    return app


app = create_app()
