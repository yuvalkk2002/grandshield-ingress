from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import audio, debug, health
from app.config import settings
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("application_startup")
    try:
        settings.load_aws_secrets()
    except Exception as e:
        logger.critical("startup_failed", error=str(e))
        # Depending on strictness, we might want to let it crash or continue
        raise e
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="GrandShield Backend",
        description="Backend service for processing audio and detecting scams.",
        version="0.1.0",
        lifespan=lifespan
    )

    # Middleware
    # In a real production environment, allow_origins should be specific domains.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, tags=["System"])
    # Versioned API routes
    app.include_router(audio.router, prefix="/api/v1", tags=["Audio"])
    app.include_router(debug.router, prefix="/api/v1/debug", tags=["Debug"])

    return app
