"""Telegram Webhook & Interactive Approval Callback Router.

Processes button clicks from Telegram inline keyboards ([✅ Approve] / [❌ Reject]),
updates the database approval ticket status, triggers email dispatch via EmailService,
and sends immediate confirmation back to Telegram.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ApprovalRequest, ApprovalStatus, AuditLog, Student
from app.services.telegram_service import telegram_service
from app.services.email_service import email_service

logger = logging.getLogger("telegram_webhook")

router = APIRouter(prefix="/telegram", tags=["telegram"])


class CallbackPayload(BaseModel):
    callback_data: Optional[str] = None
    callback_query_id: Optional[str] = None
    chat_id: Optional[int] = None
    message_id: Optional[int] = None
    action: Optional[str] = None
    request_id: Optional[str] = None
    student_email: Optional[str] = None
    student_name: Optional[str] = None
    course_name: Optional[str] = None


@router.post(
    "/webhook",
    summary="Telegram Bot Webhook endpoint",
    description="Receives Telegram updates including inline button callback queries."
)
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Processes incoming Telegram updates from bot webhook."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Check for callback_query (button click)
    callback_query = body.get("callback_query")
    if callback_query:
        cb_id = callback_query.get("id")
        data = callback_query.get("data", "")
        from_user = callback_query.get("from", {})
        message = callback_query.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")

        return handle_approval_callback(
            callback_data=data,
            callback_query_id=cb_id,
            chat_id=chat_id,
            message_id=message_id,
            reviewer_name=from_user.get("first_name", "Telegram User"),
            db=db
        )

    return {"status": "ignored", "message": "No actionable callback_query in update"}


@router.post(
    "/callback",
    summary="Interactive approval callback trigger",
    description="Direct or simulated callback trigger for Telegram inline approval buttons."
)
def telegram_callback(
    payload: CallbackPayload,
    db: Session = Depends(get_db)
):
    """Direct handler for approval decisions (used by webhooks and test scripts)."""
    cb_data = payload.callback_data
    if not cb_data and payload.action:
        cb_data = f"{payload.action}_{payload.request_id or 'REQ-DEFAULT'}"

    return handle_approval_callback(
        callback_data=cb_data or "approve_REQ-DEFAULT",
        callback_query_id=payload.callback_query_id,
        chat_id=payload.chat_id,
        message_id=payload.message_id,
        student_email=payload.student_email,
        student_name=payload.student_name,
        course_name=payload.course_name,
        reviewer_name="Telegram Reviewer",
        db=db
    )


def handle_approval_callback(
    callback_data: str,
    callback_query_id: Optional[str] = None,
    chat_id: Optional[int] = None,
    message_id: Optional[int] = None,
    student_email: Optional[str] = None,
    student_name: Optional[str] = None,
    course_name: Optional[str] = None,
    reviewer_name: str = "Telegram Reviewer",
    db: Session = None,
) -> Dict[str, Any]:
    """Core logic to process approval/rejection, dispatch emails, and confirm on Telegram."""
    is_approve = callback_data.lower().startswith("approve")
    is_reject = callback_data.lower().startswith("reject")

    # Extract request identifier from callback data (e.g. approve_REQ-EMAIL-2026-09 or approve_d_abc123)
    parts = callback_data.split("_", 1)
    req_id_str = parts[1] if len(parts) > 1 else "REQ-EMAIL"

    # Check if this is a Gmail Live draft approval
    from app.services.gmail_service import get_pending_draft
    if req_id_str.startswith("d_") or get_pending_draft(req_id_str):
        from app.routers.telegram import handle_approval_callback as handle_gmail_callback
        return handle_gmail_callback(
            callback_data=callback_data,
            callback_query_id=callback_query_id,
            chat_id=chat_id,
            message_id=message_id,
            reviewer_name=reviewer_name,
            db=db
        )

    # Acknowledge callback query to Telegram client if ID is present
    if callback_query_id:
        try:
            telegram_service.answer_callback_query(
                callback_query_id=callback_query_id,
                text="✅ Approved & Dispatched!" if is_approve else "❌ Request Rejected.",
                show_alert=False
            )
        except Exception as e:
            logger.warning("Failed to answer callback query: %s", e)

    # Resolve student info from DB or fallback
    target_email = student_email
    target_name = student_name or "Paschal Okpalaugo"
    target_course = course_name or "Full-Stack AI Course"

    if not target_email and db:
        recent_student = db.query(Student).order_by(Student.id.desc()).first()
        if recent_student:
            target_email = recent_student.email
            target_name = recent_student.full_name
            target_course = recent_student.course_name

    if not target_email:
        target_email = "student@nextserve.ai"

    # Update or register Approval Request in Database
    approval_record = None
    if db:
        # Try finding existing approval by ID or payload
        try:
            int_id = int(req_id_str) if req_id_str.isdigit() else None
            if int_id:
                approval_record = db.query(ApprovalRequest).filter(ApprovalRequest.id == int_id).first()
        except Exception:
            pass

        if not approval_record:
            # Create a tracked approval entry
            approval_record = ApprovalRequest(
                requested_by=1,
                action_type="student_notification_email",
                payload={
                    "request_id": req_id_str,
                    "student_email": target_email,
                    "student_name": target_name,
                    "course_name": target_course,
                },
                status=ApprovalStatus.APPROVED if is_approve else ApprovalStatus.REJECTED,
                reviewer_notes=f"Decided via Telegram callback ({reviewer_name})",
                decided_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            db.add(approval_record)
            db.commit()
            db.refresh(approval_record)
        else:
            approval_record.status = ApprovalStatus.APPROVED if is_approve else ApprovalStatus.REJECTED
            approval_record.reviewer_notes = f"Decided via Telegram callback ({reviewer_name})"
            approval_record.decided_at = datetime.now(timezone.utc)
            db.commit()

        # Audit Log
        try:
            audit = AuditLog(
                agent_name="telegram_hitl_service",
                action="approval_decision_submitted",
                task_id=req_id_str,
                status="approved" if is_approve else "rejected",
                details={
                    "request_id": req_id_str,
                    "decision": "approved" if is_approve else "rejected",
                    "reviewer": reviewer_name,
                    "target_email": target_email,
                },
                created_at=datetime.now(timezone.utc)
            )
            db.add(audit)
            db.commit()
        except Exception:
            db.rollback()

    email_result = None
    confirmation_text = ""

    if is_approve:
        # Trigger Email Dispatch
        email_result = email_service.send_student_notification_email(
            student_email=target_email,
            student_name=target_name,
            course_name=target_course,
            orientation_info="Monday at 10:00 AM UTC via Nextserve Student Portal."
        )

        confirmation_text = (
            "✅ <b>Email Approved & Sent!</b>\n\n"
            f"👤 <b>Recipient:</b> {target_name} (<code>{target_email}</code>)\n"
            f"📚 <b>Course:</b> {target_course}\n"
            f"🔑 <b>Request ID:</b> <code>{req_id_str}</code>\n"
            f"📫 <b>Email Message ID:</b> <code>{email_result.get('message_id')}</code>\n\n"
            "⚡ <i>Action successfully finalized by Human-in-the-Loop gate.</i>"
        )
    else:
        confirmation_text = (
            "❌ <b>Request Rejected.</b>\n\n"
            f"Action for Request ID <code>{req_id_str}</code> was cancelled by reviewer."
        )

    # Send confirmation edit/reply back to Telegram
    telegram_response = None
    try:
        if message_id:
            # Edit original message to remove buttons and show confirmation
            telegram_response = telegram_service.edit_message_text(
                text=confirmation_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup={"inline_keyboard": []}  # Clear buttons
            )
        else:
            # Send fresh confirmation message
            telegram_response = telegram_service.send_message(
                text=confirmation_text,
                chat_id=chat_id
            )
    except Exception as exc:
        logger.warning("Failed to send Telegram confirmation update: %s", exc)

    return {
        "status": "success",
        "decision": "approved" if is_approve else "rejected",
        "request_id": req_id_str,
        "approval_id": approval_record.id if approval_record else None,
        "email_dispatched": is_approve,
        "email_result": email_result,
        "telegram_response": telegram_response,
    }
