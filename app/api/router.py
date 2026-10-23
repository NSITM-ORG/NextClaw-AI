from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.approvals import router as approvals_router
from app.api.audit import router as audit_router
from api.routes.school import router as school_router
from api.routes.website import router as website_router
from api.routes.coding import router as coding_router
from app.api.students import router as students_router
from app.routers.telegram import router as telegram_router
from app.api.reports import router as reports_router
from app.routers.website_events import router as events_router
from core.router import gateway_router
from api.routes.composite import router as composite_router
from api.routes.voice import router as voice_router
from api.routes.social import router as social_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(tasks_router)
api_router.include_router(approvals_router)
api_router.include_router(audit_router)
api_router.include_router(school_router)
api_router.include_router(website_router)
api_router.include_router(coding_router)
api_router.include_router(students_router)
api_router.include_router(telegram_router)
api_router.include_router(reports_router)
api_router.include_router(events_router)
api_router.include_router(gateway_router)
api_router.include_router(composite_router)
api_router.include_router(voice_router)
api_router.include_router(social_router)

