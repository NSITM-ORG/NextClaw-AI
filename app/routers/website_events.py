"""Website Real-Time Event & Activity Webhook Router.

Relays all live activities from the Nextserve website/server directly
into the owner's Telegram bot:
- New Student Registrations & Enrollments
- Tuition Payments & Instalment Receipts Uploaded
- Step 1 Partial Enrollment Lead Capture
- Developer Community Join Applications
- Website Chatbot Visitor Inquiries
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.telegram_service import telegram_service

logger = logging.getLogger("website_events")

router = APIRouter(prefix="/events", tags=["website-events"])


class PaymentEventPayload(BaseModel):
    student_name: str = Field(..., json_schema_extra={"example": "Emeka Okafor"})
    email: str = Field(..., json_schema_extra={"example": "emeka@example.com"})
    programme: str = Field(..., json_schema_extra={"example": "Fullstack Web Development"})
    amount: float = Field(..., json_schema_extra={"example": 152000.0})
    plan_type: str = Field(default="Instalment Plan", json_schema_extra={"example": "Instalment Plan"})
    tranche: Optional[int] = Field(default=1, json_schema_extra={"example": 1})
    receipt_url: Optional[str] = Field(default=None, json_schema_extra={"example": "https://storage.nextserve.edu/receipts/rec_123.jpg"})


class EnrollmentEventPayload(BaseModel):
    student_name: str = Field(..., json_schema_extra={"example": "Adaeze Nwosu"})
    email: str = Field(..., json_schema_extra={"example": "adaeze@example.com"})
    phone: Optional[str] = Field(default=None, json_schema_extra={"example": "+2348012345678"})
    programme: str = Field(..., json_schema_extra={"example": "UI/UX Design"})
    delivery_format: Optional[str] = Field(default="Online", json_schema_extra={"example": "Online"})
    step: int = Field(default=1, json_schema_extra={"example": 1})  # 1 = partial lead, 4 = completed


class CommunityJoinPayload(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Tunde Bakare"})
    email: str = Field(..., json_schema_extra={"example": "tunde@example.com"})
    role: str = Field(..., json_schema_extra={"example": "Frontend Developer (React)"})
    portfolio_or_github: Optional[str] = Field(default=None, json_schema_extra={"example": "https://github.com/tundebakare"})


class ChatInquiryPayload(BaseModel):
    visitor_query: str = Field(..., json_schema_extra={"example": "How much is the deposit for Fullstack Web Dev?"})
    bot_response: str = Field(..., json_schema_extra={"example": "The deposit is ₦152,000 (40% of the ₦380,000 instalment fee)."})
    user_ip: Optional[str] = None


class UniversalActivityPayload(BaseModel):
    activity_type: str = Field(..., json_schema_extra={"example": "Course Syllabus Downloaded"})
    title: str = Field(..., json_schema_extra={"example": "Fullstack Curriculum Downloaded"})
    description: str = Field(..., json_schema_extra={"example": "Visitor emeka@example.com downloaded the PDF syllabus."})
    metadata: Optional[Dict[str, Any]] = None


@router.post("/payment", summary="Relay student tuition payment to Telegram")
async def handle_payment_event(payload: PaymentEventPayload, background_tasks: BackgroundTasks):
    """Dispatches instant payment alert to owner's Telegram."""
    logger.info("Received Payment Event: %s, %s, %s", payload.student_name, payload.programme, payload.amount)
    try:
        res = telegram_service.send_payment_alert(
            student_name=payload.student_name,
            email=payload.email,
            programme=payload.programme,
            amount=payload.amount,
            plan_type=payload.plan_type,
            tranche=payload.tranche,
            receipt_url=payload.receipt_url,
        )
        return {"status": "success", "message": "Payment notification delivered to Telegram", "telegram_result": res}
    except Exception as exc:
        logger.error("Failed to forward payment alert to Telegram: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/enrollment", summary="Relay enrollment / partial lead to Telegram")
async def handle_enrollment_event(payload: EnrollmentEventPayload):
    """Dispatches enrollment alert to owner's Telegram (Step 1 lead or Step 4 completed)."""
    logger.info("Received Enrollment Event: %s, Step %s, %s", payload.student_name, payload.step, payload.programme)
    try:
        if payload.step == 1:
            res = telegram_service.send_partial_enrollment_alert(
                student_name=payload.student_name,
                email=payload.email,
                phone=payload.phone,
                programme=payload.programme,
                delivery_format=payload.delivery_format,
            )
        else:
            res = telegram_service.send_registration_alert(
                student_name=payload.student_name,
                course=payload.programme,
            )
        return {"status": "success", "message": "Enrollment notification delivered to Telegram", "telegram_result": res}
    except Exception as exc:
        logger.error("Failed to forward enrollment alert to Telegram: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/community-join", summary="Relay developer community application to Telegram")
async def handle_community_event(payload: CommunityJoinPayload):
    """Dispatches community join application alert to owner's Telegram."""
    logger.info("Received Community Application: %s, %s", payload.name, payload.role)
    try:
        res = telegram_service.send_community_join_alert(
            name=payload.name,
            email=payload.email,
            role=payload.role,
            portfolio_or_github=payload.portfolio_or_github,
        )
        return {"status": "success", "message": "Community application delivered to Telegram", "telegram_result": res}
    except Exception as exc:
        logger.error("Failed to forward community alert to Telegram: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/chat-inquiry", summary="Relay website chatbot interaction to Telegram")
async def handle_chat_inquiry_event(payload: ChatInquiryPayload):
    """Dispatches website chatbot conversation snippet to owner's Telegram."""
    try:
        res = telegram_service.send_website_chat_alert(
            visitor_query=payload.visitor_query,
            bot_response=payload.bot_response,
        )
        return {"status": "success", "message": "Chat inquiry delivered to Telegram", "telegram_result": res}
    except Exception as exc:
        logger.error("Failed to forward chat inquiry to Telegram: %s", exc)
        return {"status": "error", "message": str(exc)}


@router.post("/activity", summary="Relay generic website activity to Telegram")
async def handle_universal_activity(payload: UniversalActivityPayload):
    """Dispatches formatted activity card to owner's Telegram."""
    text = (
        f"🌐 <b>Website Activity: {payload.activity_type}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Title:</b> {payload.title}\n"
        f"ℹ️ <b>Details:</b> {payload.description}\n"
    )
    if payload.metadata:
        details_list = [f"  • <b>{k}:</b> {v}" for k, v in payload.metadata.items()]
        text += "\n" + "\n".join(details_list)

    try:
        res = telegram_service.send_message(text=text)
        return {"status": "success", "message": "Activity notification delivered to Telegram", "telegram_result": res}
    except Exception as exc:
        logger.error("Failed to forward activity to Telegram: %s", exc)
        return {"status": "error", "message": str(exc)}
