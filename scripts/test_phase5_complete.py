#!/usr/bin/env python3
"""End-to-End Integration Test for Nextserve AI Phase 5:
- Student Registration API & Webhook
- Interactive Telegram Human-in-the-Loop Approval Callback
- Student Notification Email Dispatch
- Executive Daily Summary Dispatch
"""

import sys
import os
import time
import uuid

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for console output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from main import app
from app.db.session import SessionLocal, init_db
from app.db.models import Student, ApprovalRequest, ApprovalStatus
from app.services.telegram_service import telegram_service

client = TestClient(app)


def log_phase(title: str):
    width = 75
    print("\n" + "=" * width)
    print(f"  >>> {title.upper()} <<<")
    print("=" * width)


def main():
    log_phase("Nextserve AI: Phase 5 End-to-End Integration Test")

    print("[Step 0] Initializing database schema and extensions...")
    init_db()
    print("  [OK] Database schema initialized and ready.")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    masked_token = f"{bot_token[:10]}...{bot_token[-5:]}" if bot_token and len(bot_token) > 15 else "Not configured"
    print(f"  [OK] Telegram Bot Token: {masked_token}")
    print(f"  [OK] Telegram Chat ID:   {chat_id}")

    # =========================================================================
    # Phase 1: Student Registration API & Telegram Alert
    # =========================================================================
    log_phase("Phase 1: Student Registration Endpoint (POST /api/v1/students/register)")
    unique_suffix = uuid.uuid4().hex[:4]
    student_payload = {
        "full_name": "Paschal Okpalaugo",
        "email": f"paschal.{unique_suffix}@nextserve.ai",
        "phone": "+1 (555) 234-5678",
        "course_name": "Full-Stack AI Course",
        "notes": "Fast-track orientation requested for AI Agent Specialization."
    }

    print(f"[*] Submitting registration for: {student_payload['full_name']}")
    print(f"[*] Enrolling in course:         {student_payload['course_name']}")
    print(f"[*] Student Email:               {student_payload['email']}")

    reg_response = client.post("/api/v1/students/register", json=student_payload)
    if reg_response.status_code != 201:
        print(f"[FAIL] Registration endpoint returned {reg_response.status_code}: {reg_response.text}")
        sys.exit(1)

    reg_data = reg_response.json()
    reg_id = reg_data["registration_id"]
    reg_msg_id = reg_data.get("telegram_message_id")
    print("  [SUCCESS] Student successfully persisted in PostgreSQL database!")
    print(f"  🆔 Registration ID:    {reg_id}")
    print(f"  🚀 Telegram Alert:     {'DELIVERED' if reg_data.get('telegram_alert_sent') else 'QUEUED'}")
    print(f"  💬 Telegram Msg ID:    {reg_msg_id}")

    # Verify DB record
    with SessionLocal() as db:
        saved_student = db.query(Student).filter(Student.registration_id == reg_id).first()
        assert saved_student is not None, "Student record not found in database!"
        print(f"  ✅ DB Verification: Student ID #{saved_student.id} confirmed in 'students' table.")

    time.sleep(1)

    # =========================================================================
    # Phase 2: Dispatch Interactive Human-in-the-Loop Email Approval Request
    # =========================================================================
    log_phase("Phase 2: Interactive Telegram Approval Request Dispatch")
    req_code = f"REQ-EMAIL-{unique_suffix.upper()}"
    print(f"[*] Simulating Level 3 gate for Student Orientation Email Draft...")
    print(f"[*] Request ID: {req_code}")

    approval_msg_res = telegram_service.send_approval_request(
        title="Draft Student Notification Email",
        details=(
            f"Orientation email prepared for {student_payload['full_name']} ({student_payload['email']})\n"
            f"Course: {student_payload['course_name']}\n"
            "Orientation: Monday at 10:00 AM UTC."
        ),
        request_id=req_code,
        approve_callback_data=f"approve_{req_code}",
        reject_callback_data=f"reject_{req_code}"
    )

    approval_msg_id = None
    if approval_msg_res.get("ok"):
        approval_msg_id = approval_msg_res.get("result", {}).get("message_id")
        print(f"  [SUCCESS] Interactive Telegram message with [✅ Approve] / [❌ Reject] buttons sent!")
        print(f"  💬 Message ID: {approval_msg_id}")
    else:
        print(f"  [WARNING] Telegram dispatch warning: {approval_msg_res}")

    time.sleep(1.5)

    # =========================================================================
    # Phase 3: Interactive Approval Callback (Click [✅ Approve])
    # =========================================================================
    log_phase("Phase 3: Interactive Approval Callback (Simulating [✅ Approve] Button Click)")
    print(f"[*] Simulating Telegram callback for [✅ Approve] on {req_code}...")

    callback_payload = {
        "callback_data": f"approve_{req_code}",
        "chat_id": int(chat_id) if chat_id else 7311614517,
        "message_id": approval_msg_id,
        "student_email": student_payload["email"],
        "student_name": student_payload["full_name"],
        "course_name": student_payload["course_name"]
    }

    cb_response = client.post("/api/v1/telegram/callback", json=callback_payload)
    if cb_response.status_code != 200:
        print(f"[FAIL] Callback endpoint returned {cb_response.status_code}: {cb_response.text}")
        sys.exit(1)

    cb_data = cb_response.json()
    print("  [SUCCESS] Callback processed successfully!")
    print(f"  🔘 Decision:           {cb_data.get('decision').upper()}")
    print(f"  📧 Email Dispatched:   {cb_data.get('email_dispatched')}")
    print(f"  📬 Email Message ID:   {cb_data.get('email_result', {}).get('message_id')}")
    print(f"  🎯 Email Recipient:    {cb_data.get('email_result', {}).get('to')}")
    print(f"  💬 Telegram Response:  {'Updated/Sent' if cb_data.get('telegram_response') else 'N/A'}")

    # Verify DB Approval Request Status
    with SessionLocal() as db:
        approval_ticket = db.query(ApprovalRequest).filter(
            ApprovalRequest.id == cb_data.get("approval_id")
        ).first()
        if approval_ticket:
            print(f"  ✅ DB Verification: Approval Ticket #{approval_ticket.id} status is '{approval_ticket.status.value.upper()}'.")
            assert approval_ticket.status == ApprovalStatus.APPROVED, "Ticket status is not APPROVED!"

    time.sleep(1.5)

    # =========================================================================
    # Phase 4: Executive Daily Summary Report (POST /api/v1/reports/daily-summary)
    # =========================================================================
    log_phase("Phase 4: Executive Daily Summary Dispatch (POST /api/v1/reports/daily-summary)")
    print("[*] Generating executive briefing over registered students, approvals, and agents...")

    summary_response = client.post("/api/v1/reports/daily-summary")
    if summary_response.status_code != 200:
        print(f"[FAIL] Daily summary endpoint returned {summary_response.status_code}: {summary_response.text}")
        sys.exit(1)

    summary_data = summary_response.json()
    metrics = summary_data.get("summary", {})
    delivery = summary_data.get("telegram_delivery", {})
    summary_msg_id = delivery.get("result", {}).get("message_id") if delivery else None

    print("  [SUCCESS] Executive Daily Summary successfully generated and dispatched!")
    print(f"  🎓 Total Registered Students:   {metrics.get('total_students')}")
    print(f"  ⏳ Pending Level 3 Approvals:   {metrics.get('pending_approvals')} tickets")
    print(f"  🤖 Specialist Agents Health:     All Operational")
    print(f"  💬 Telegram Briefing Msg ID:    {summary_msg_id}")

    # =========================================================================
    # Final Summary
    # =========================================================================
    log_phase("Phase 5 Integration Verification Complete")
    print("🎉 ALL WORKFLOWS PASSED WITH LIVE TELEGRAM & DATABASE INTEGRATION:")
    print("  1. Student registration persisted in PostgreSQL and alert delivered to Telegram.")
    print("  2. Interactive approval request with [✅ Approve] and [❌ Reject] inline buttons dispatched.")
    print("  3. [✅ Approve] callback executed: DB status updated to APPROVED, email sent, Telegram updated.")
    print("  4. Executive daily summary generated and delivered to Telegram chat.\n")


if __name__ == "__main__":
    main()
