from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.security import JWTAuthMiddleware
from app.api.router import api_router
from app.services.gmail_worker import gmail_worker
from app.services.telegram_bot_worker import telegram_bot_worker
from core.scheduler import scheduler as nextclaw_scheduler
from core.router import interactive_dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start NextClaw continuous worker and background tasks."""
    await gmail_worker.start()
    await telegram_bot_worker.start()
    await nextclaw_scheduler.start()
    yield
    """Gracefully stop NextClaw continuous worker and background tasks."""
    await gmail_worker.stop()
    await telegram_bot_worker.stop()
    await nextclaw_scheduler.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Next Claw Personal Assistant API — academic advising, course catalog retrieval, persistent session memory, and automated workflows.",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Authentication Middleware
app.add_middleware(JWTAuthMiddleware)


@app.get("/health", tags=["system"])
def health_check():
    """Basic health-check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }


@app.get("/dashboard", tags=["NextClaw OS"])
def dashboard_view():
    """Interactive NextClaw OS Dashboard and Academic Calendar."""
    return interactive_dashboard()


@app.get("/", tags=["system"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "dashboard": "/dashboard",
        "web_ui": "/app/",
        "docs": "/docs",
        "health": "/health"
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)



# Mount frontend static files with no-cache headers for live development
import os
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

class NoCacheStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs) -> Response:
        resp = super().file_response(*args, **kwargs)
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/app", NoCacheStaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
