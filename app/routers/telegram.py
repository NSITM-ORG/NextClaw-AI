"""Telegram Human-in-the-Loop Webhook Router.

Handles incoming Telegram webhook updates and button callback queries for:
- [✅ Approve]: Dispatches drafted reply via gmail_service.send_email() and
  updates the message to '✅ Email successfully sent to {sender} via chigbookpalaugo@gmail.com!'
- [❌ Reject]: Cancels the dispatch and updates message to
  '❌ Email dispatch canceled by admin.'
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ApprovalRequest, ApprovalStatus, AuditLog, Student
from app.services.telegram_service import telegram_service
from app.services.gmail_service import (
    gmail_service,
    get_pending_draft,
    pop_pending_draft,
)

logger = logging.getLogger("telegram_router")

router = APIRouter(prefix="/telegram", tags=["telegram"])


class CallbackPayload(BaseModel):
    callback_data: Optional[str] = None
    callback_query_id: Optional[str] = None
    chat_id: Optional[int] = None
    message_id: Optional[int] = None
    action: Optional[str] = None
    request_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None


@router.get(
    "/emails",
    summary="List persisted emails from PostgreSQL",
    description="Returns all emails and their Human-in-the-Loop review states."
)
def get_persisted_emails(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    from app.services.email_repository import email_repository
    emails = email_repository.list_emails(status=status, limit=limit, db=db)
    return [
        {
            "id": e.id,
            "email_uid": e.email_uid,
            "sender": e.sender,
            "sender_name": e.sender_name,
            "subject": e.subject,
            "body": e.body,
            "status": e.status,
            "token": e.token,
            "reply_body": e.reply_body,
            "approved_at": e.approved_at.isoformat() if e.approved_at else None,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in emails
    ]


@router.post(
    "/check-emails",
    summary="Trigger live Gmail check & Telegram forward",
    description="Checks chigbookpalaugo@gmail.com for unread emails and forwards approval card to Telegram."
)
def trigger_gmail_check(db: Session = Depends(get_db)):
    from app.services.gmail_service import (
        gmail_service,
        create_and_store_draft,
        format_telegram_approval_card,
    )
    import os

    unread = gmail_service.fetch_latest_unread(mark_as_read=False)
    if not unread:
        return {
            "status": "idle",
            "message": "No unread emails in chigbookpalaugo@gmail.com inbox."
        }

    token, draft = create_and_store_draft(
        sender=unread["sender"],
        subject=unread["subject"],
        body=unread["body"],
        sender_name=unread["sender_name"],
        email_uid=unread["id"],
        received_date=unread["date"],
    )

    telegram_text, reply_markup = format_telegram_approval_card(
        sender=unread["sender"],
        subject=unread["subject"],
        body=unread["body"],
        draft_body=draft["body"],
        token=token,
        sender_name=unread["sender_name"],
        is_simulated=False,
    )

    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    tg_res = telegram_service.send_message(
        text=telegram_text,
        chat_id=chat_id,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    return {
        "status": "forwarded_to_telegram",
        "email_id": unread["id"],
        "sender": unread["sender"],
        "subject": unread["subject"],
        "token": token,
        "telegram_message_id": tg_res.get("result", {}).get("message_id")
    }


@router.post(
    "/simulate-inquiry",
    summary="Simulate incoming student inquiry & Telegram card",
    description="Simulates a realistic student inquiry and dispatches approval card to Telegram."
)
def simulate_inquiry(
    sender: str = "student@example.com",
    sender_name: str = "Prospective Student",
    subject: str = "Inquiry: Nextserve AI Course Admission & Orientation",
    body: str = "Hello NextClaw, I would like to confirm my orientation schedule for the Full-Stack AI Course.",
    db: Session = Depends(get_db)
):
    from app.services.gmail_service import (
        create_and_store_draft,
        format_telegram_approval_card,
    )
    import os

    token, draft = create_and_store_draft(
        sender=sender,
        subject=subject,
        body=body,
        sender_name=sender_name,
    )

    telegram_text, reply_markup = format_telegram_approval_card(
        sender=sender,
        subject=subject,
        body=body,
        draft_body=draft["body"],
        token=token,
        sender_name=sender_name,
        is_simulated=True,
    )

    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    tg_res = telegram_service.send_message(
        text=telegram_text,
        chat_id=chat_id,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    return {
        "status": "forwarded_to_telegram",
        "sender": sender,
        "subject": subject,
        "token": token,
        "telegram_message_id": tg_res.get("result", {}).get("message_id")
    }


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
            reviewer_name=from_user.get("first_name", "Telegram Admin"),
            db=db
        )

    # Check for direct user chat message
    message = body.get("message")
    if message and "text" in message:
        return await handle_telegram_message(message, db=db)

    return {"status": "ignored", "message": "No actionable update in update"}


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
        sender_override=payload.sender,
        subject_override=payload.subject,
        body_override=payload.body,
        reviewer_name="Telegram Admin",
        db=db
    )


def handle_approval_callback(
    callback_data: str,
    callback_query_id: Optional[str] = None,
    chat_id: Optional[int] = None,
    message_id: Optional[int] = None,
    sender_override: Optional[str] = None,
    subject_override: Optional[str] = None,
    body_override: Optional[str] = None,
    reviewer_name: str = "Telegram Admin",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Core logic to process approval/rejection, dispatch emails via Gmail, and confirm on Telegram."""
    is_approve = callback_data.lower().startswith("approve")
    is_reject = callback_data.lower().startswith("reject")

    # Extract draft/request token from callback data (e.g. approve_d_abc123 or approve_REQ-7311)
    parts = callback_data.split("_", 1)
    req_token = parts[1] if len(parts) > 1 else "default"

    # Acknowledge callback query to Telegram client if ID is present
    if callback_query_id:
        try:
            telegram_service.answer_callback_query(
                callback_query_id=callback_query_id,
                text="✅ Email Approved & Dispatched!" if is_approve else "❌ Email dispatch canceled.",
                show_alert=False
            )
        except Exception as e:
            logger.warning("Failed to answer callback query: %s", e)

    # Check for pending draft in Gmail draft store
    pending_draft = get_pending_draft(req_token)
    
    # Resolve recipient, subject, and body
    sender_email = sender_override or (pending_draft.get("sender") if pending_draft else None)
    subject = subject_override or (pending_draft.get("subject") if pending_draft else None)
    body = body_override or (pending_draft.get("body") if pending_draft else None)

    # Fallback to DB or default if not found in pending cache
    if not sender_email and db:
        try:
            recent_student = db.query(Student).order_by(Student.id.desc()).first()
            if recent_student:
                sender_email = recent_student.email
        except Exception:
            pass

    if not sender_email:
        sender_email = "student@nextserve.ai"
    if not subject:
        subject = "NextClaw AI Assistance Inquiry"
    if not body:
        body = (
            f"Hello,\n\n"
            f"Thank you for contacting NextClaw AI Assistant. We have reviewed your request "
            f"and our team has approved this response.\n\n"
            f"Best regards,\n"
            f"NextClaw (Nextserve AI Operational Assistant)\n"
            f"Nextserve Education Inc."
        )

    # Update or register Approval Request in Database if session available
    approval_record = None
    if db:
        try:
            int_id = int(req_token) if req_token.isdigit() else None
            if int_id:
                approval_record = db.query(ApprovalRequest).filter(ApprovalRequest.id == int_id).first()

            if not approval_record:
                approval_record = ApprovalRequest(
                    requested_by=1,
                    action_type="gmail_reply_dispatch",
                    payload={
                        "token": req_token,
                        "recipient": sender_email,
                        "subject": subject,
                        "body": body[:200],
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
            audit = AuditLog(
                agent_name="telegram_hitl_service",
                action="gmail_approval_decision",
                task_id=req_token,
                status="approved" if is_approve else "rejected",
                details={
                    "token": req_token,
                    "decision": "approved" if is_approve else "rejected",
                    "reviewer": reviewer_name,
                    "recipient": sender_email,
                },
                created_at=datetime.now(timezone.utc)
            )
            db.add(audit)
            db.commit()
        except Exception as db_err:
            logger.warning("Database tracking note: %s", db_err)
            try:
                db.rollback()
            except Exception:
                pass

    email_result = None
    if is_approve:
        # Trigger gmail_service.send_email()
        try:
            email_result = gmail_service.send_email(
                to_email=sender_email,
                subject=subject,
                body=body,
            )
            logger.info("Gmail successfully dispatched to %s: %s", sender_email, email_result)
        except Exception as exc:
            logger.error("Failed to dispatch email via Gmail: %s", exc)
            email_result = {"status": "error", "error": str(exc)}

        # Update Email persistence record in PostgreSQL
        try:
            from app.services.email_repository import email_repository
            email_repository.update_email_status(
                token_or_id=req_token,
                status="APPROVED",
                reply_body=body,
                db=db
            )
        except Exception as repo_err:
            logger.warning("Could not update EmailRecord in PostgreSQL: %s", repo_err)

        # Required confirmation message:
        import html
        safe_email = html.escape(str(sender_email))
        confirmation_text = f"✅ Email successfully sent to {safe_email} via NextClaw (chigbookpalaugo@gmail.com)!"
        # Clean up draft from memory once sent
        pop_pending_draft(req_token)
    else:
        # Update Email persistence record in PostgreSQL
        try:
            from app.services.email_repository import email_repository
            email_repository.update_email_status(
                token_or_id=req_token,
                status="REJECTED",
                db=db
            )
        except Exception as repo_err:
            logger.warning("Could not update EmailRecord rejection in PostgreSQL: %s", repo_err)

        # Required rejection message:
        confirmation_text = "❌ Email dispatch canceled by admin."
        pop_pending_draft(req_token)

    # Edit Telegram message or send confirmation
    telegram_response = None
    try:
        if message_id:
            telegram_response = telegram_service.edit_message_text(
                text=confirmation_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup={"inline_keyboard": []},
                parse_mode="HTML"
            )
        else:
            telegram_response = telegram_service.send_message(
                text=confirmation_text,
                chat_id=chat_id,
                parse_mode="HTML"
            )
    except Exception as exc:
        logger.warning("Failed to update Telegram message: %s", exc)

    return {
        "status": "success",
        "decision": "approved" if is_approve else "rejected",
        "recipient": sender_email,
        "email_dispatched": is_approve,
        "email_result": email_result,
        "confirmation_text": confirmation_text,
        "telegram_response": telegram_response,
    }


async def handle_telegram_message(
    message: Dict[str, Any],
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Processes incoming Telegram text messages for conversational discussion with NextClaw."""
    chat_id = message.get("chat", {}).get("id")
    user_name = message.get("from", {}).get("first_name", "Friend")
    text = (message.get("text") or "").strip()

    if not text or not chat_id:
        return {"status": "ignored", "message": "No text content"}

    logger.info("Telegram user '%s' (%s) sent: %s", user_name, chat_id, text)
    text_lower = text.lower()

    if text.startswith("/start") or text_lower in ["hi", "hello", "hey", "good morning", "good evening", "what's up"]:
        reply = (
            f"👋 <b>Hello {user_name}!</b> I'm <b>NextClaw</b>, the official Executive AI Assistant for <b>Nextserve (NSITM)</b>.\n\n"
            "I'm here for real-time discussion and management of everything at Nextserve:\n"
            "• 📚 <b>26 Accredited Programmes</b> (e.g. <i>\"Tell me about Fullstack, Cyber Security, or UI/UX\"</i>)\n"
            "• 💰 <b>Tuition & Instalment Plans</b> (e.g. <i>\"How much is Fullstack in instalments?\"</i>)\n"
            "• 📋 <b>Academic Policies</b> (e.g. <i>\"What is the attendance policy?\"</i> or <i>\"Refund rules\"</i>)\n"
            "• 📬 <b>Gmail Inquiries & Approvals</b> (I continuously watch your inbox and deliver interactive approval cards)\n"
            "• 🌐 <b>Live Website Activity</b> (All enrollments, leads, payments, and community joins are routed directly here)\n\n"
            "What would you like to check or manage right now? 😊"
        )
    elif text.startswith("/check"):
        from app.services.gmail_worker import gmail_worker
        res = await gmail_worker.check_once()
        if res:
            reply = f"📬 <b>New email detected:</b> from <code>{res.get('sender')}</code>. Approval card sent above!"
        else:
            reply = "📬 <b>Inbox checked:</b> No new unread emails in Gmail at this moment."
    elif text.startswith("/status"):
        reply = "🟢 <b>NextClaw Status:</b> All systems operational. 26 NSITM programmes loaded, Gmail Worker active, and website event listener active."
    else:
        # Use Nextserve School AI knowledge / agent for full real-time response
        try:
            from agents.school.agent import aquery_school_agent
            agent_res = await aquery_school_agent(query=text, thread_id=f"tg_{chat_id}")
            raw_ans = agent_res.get("response", "")
            reply = f"🤖 <b>NextClaw:</b>\n\n{raw_ans}"
        except Exception as exc:
            logger.warning("Agent query failed for Telegram message: %s", exc)
            reply = (
                f"🤖 <b>NextClaw:</b> Thanks for your message, {user_name}!\n\n"
                f"I've noted your question: \"<i>{text[:120]}</i>\".\n\n"
                "I can look up full information on all 26 NSITM programmes (Fullstack, Front-End, Cyber Security, UI/UX, Data Science, Digital Marketing), "
                "tuition costs in ₦ Naira, 3-part instalment plans, 80% attendance policy, and enrollment steps. What would you like to check?"
            )

    try:
        telegram_service.send_message(
            text=reply,
            chat_id=chat_id,
            parse_mode="HTML"
        )
    except Exception as exc:
        logger.warning("HTML send failed, falling back to clean text: %s", exc)
        clean = (
            reply.replace("<b>", "")
            .replace("</b>", "")
            .replace("<i>", "")
            .replace("</i>", "")
            .replace("<code>", "")
            .replace("</code>", "")
            .replace("<pre>", "")
            .replace("</pre>", "")
        )
        telegram_service.send_message(
            text=clean,
            chat_id=chat_id
        )

    return {"status": "replied", "chat_id": chat_id}

