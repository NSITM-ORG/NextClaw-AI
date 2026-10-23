#!/usr/bin/env python3
"""Live Telegram Integration Test Script for Nextserve AI.

Tests:
1. send_registration_alert():
   Simulates logging a new student registration ("Paschal Okpalaugo - Full-Stack AI Course")
   and sends an instant Telegram alert message.
2. send_approval_request():
   Simulates drafting a student notification email and sends an interactive
   Telegram message with [✅ Approve] and [❌ Reject] inline buttons.
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for console output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from dotenv import load_dotenv

# Explicitly ensure .env is loaded via python-dotenv
load_dotenv()

from app.services.telegram_service import (
    TelegramService,
    telegram_service,
)


def log_banner(title: str):
    width = 75
    print("\n" + "=" * width)
    print(f"  >>> {title.upper()} <<<")
    print("=" * width)


def send_registration_alert():
    """Simulates logging a new student registration and sends an alert to Telegram."""
    student_name = "Paschal Okpalaugo"
    course = "Full-Stack AI Course"
    registration_id = "REG-2026-AI01"

    print("\n[Step 1] Simulating Student Registration Event...")
    print(f"  👤 Student: {student_name}")
    print(f"  📚 Course: {course}")
    print(f"  🆔 Registration ID: {registration_id}")
    print("  🚀 Dispatching live Telegram registration alert...")

    response = telegram_service.send_registration_alert(
        student_name=student_name,
        course=course,
        registration_id=registration_id,
    )

    if response.get("ok"):
        message_id = response.get("result", {}).get("message_id")
        chat_title = response.get("result", {}).get("chat", {}).get("first_name") or response.get("result", {}).get("chat", {}).get("title")
        print("  [SUCCESS] Telegram Alert Delivered!")
        print(f"  💬 Message ID: {message_id}")
        print(f"  🎯 Recipient Chat: {chat_title}")
    else:
        print(f"  [ERROR] Failed to send Telegram alert: {response}")

    return response


def send_approval_request():
    """Simulates drafting a student notification email and sends an interactive approval request."""
    title = "Draft Student Notification Email"
    details = (
        "Draft email to Paschal Okpalaugo (Full-Stack AI Course):\n"
        "\"Welcome to the Full-Stack AI Course! Your orientation session is scheduled "
        "for Monday at 10:00 AM UTC. Please review the syllabus.\""
    )
    request_id = "REQ-EMAIL-2026-09"

    print("\n[Step 2] Simulating Email Draft & Approval Request Event...")
    print(f"  📋 Action: {title}")
    print(f"  🔑 Request ID: {request_id}")
    print("  📝 Email Body Preview: 'Welcome to the Full-Stack AI Course! Your orientation...'")
    print("  🔘 Attaching Inline Keyboard: [✅ Approve] | [❌ Reject]")
    print("  🚀 Dispatching interactive Telegram approval request...")

    response = telegram_service.send_approval_request(
        title=title,
        details=details,
        request_id=request_id,
    )

    if response.get("ok"):
        message_id = response.get("result", {}).get("message_id")
        chat_title = response.get("result", {}).get("chat", {}).get("first_name") or response.get("result", {}).get("chat", {}).get("title")
        print("  [SUCCESS] Interactive Approval Request Delivered!")
        print(f"  💬 Message ID: {message_id}")
        print(f"  🎯 Recipient Chat: {chat_title}")
        print("  ✅ Inline Buttons: [✅ Approve] and [❌ Reject] active")
    else:
        print(f"  [ERROR] Failed to send approval request: {response}")

    return response


def main():
    log_banner("Nextserve AI: Telegram Integration Live Workflow Test")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    masked_token = f"{bot_token[:10]}...{bot_token[-5:]}" if bot_token and len(bot_token) > 15 else "Not set"
    print(f"[*] Loaded Bot Token: {masked_token}")
    print(f"[*] Loaded Chat ID:   {chat_id}")

    if not bot_token or not chat_id:
        print("\n[FAIL] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")
        sys.exit(1)

    print("\nStarting integration test suite...")
    time.sleep(0.5)

    # 1. Registration alert
    res1 = send_registration_alert()

    time.sleep(1)

    # 2. Approval request
    res2 = send_approval_request()

    log_banner("Test Summary & Verification")
    if res1.get("ok") and res2.get("ok"):
        print("🎉 ALL TELEGRAM INTEGRATION TESTS PASSED SUCCESSFULLY!")
        print(f"  • Test 1 (Registration Alert): Message ID {res1.get('result', {}).get('message_id')} sent.")
        print(f"  • Test 2 (Approval Request):    Message ID {res2.get('result', {}).get('message_id')} sent.")
        print("  • Interactive inline buttons are live in the Telegram chat.\n")
    else:
        print("⚠️ Some tests did not return 'ok: true'. Check above logs.\n")


if __name__ == "__main__":
    main()
