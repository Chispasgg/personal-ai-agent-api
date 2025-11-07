"""
FastAPI application server.
"""
from __init__ import __pgg_version__
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from routes.chat.v1 import ep_chat
from routes.admin.v1 import ep_admin
from routes.health import ep_health


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="PGG AI Conversational Agent",
        description="Intelligent conversational agent with RAG, extraction, and multi-turn memory",
        version=__pgg_version__,
        docs_url="/" if settings.app_env == "dev" else None,
        redoc_url="/redoc" if settings.app_env == "dev" else None
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app_env == "dev" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(ep_chat.router)
    app.include_router(ep_admin.router)
    app.include_router(ep_health.router)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"Unhandled exception path: {request.url.path}, method {request.method}, error{str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        print(f"Starting PGG AI server: version: {__pgg_version__}, env: {settings.app_env}")

        # Validate API keys
        try:
            settings.validate_api_keys()
            print("API keys validated")
        except ValueError as e:
            print(f"API key validation failed , extra: error : {str(e)}")

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        print("Shutting down PGG AI server")

    return app


# Create app instance
app = create_app()
