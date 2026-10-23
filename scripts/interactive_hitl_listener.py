#!/usr/bin/env python3
"""Interactive Telegram Live Human-in-the-Loop Tester.

1. Checks chigbookpalaugo@gmail.com for unread emails (or uses a live test inquiry).
2. Generates an AI reply draft.
3. Dispatches the interactive approval card to your Telegram chat with [✅ Approve] and [❌ Reject] buttons.
4. Listens in real-time for YOU to tap either button on your phone or desktop Telegram!
5. When you tap:
   - [✅ Approve]: Dispatches reply via Gmail SMTP and edits message to
     '✅ Email successfully sent to {sender} via chigbookpalaugo@gmail.com!'
   - [❌ Reject]: Cancels dispatch and edits message to
     '❌ Email dispatch canceled by admin.'
"""

import os
import sys
import time
import html
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for Windows console output
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

from app.services.gmail_service import (
    gmail_service,
    create_and_store_draft,
    get_pending_draft,
)
from app.services.telegram_service import telegram_service
from app.routers.telegram import handle_approval_callback


def log_banner(title: str):
    width = 75
    print("\n" + "=" * width)
    print(f"  >>> {title.upper()} <<<")
    print("=" * width)


def main():
    log_banner("Interactive Telegram HITL Live Demo")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    gmail_user = os.getenv("GMAIL_USER")

    print(f"[*] Live Gmail User:        {gmail_user}")
    print(f"[*] Telegram Admin Chat ID: {chat_id}")

    # Check webhook status and backup existing webhook if any
    webhook_info = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo").json()
    prev_webhook = webhook_info.get("result", {}).get("url", "")
    if prev_webhook:
        print(f"[*] Preserving existing webhook: {prev_webhook}")
        # Clear webhook temporarily so getUpdates can listen for your live button clicks
        requests.get(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        print("[*] Webhook temporarily cleared for local live listening.")

    try:
        # Step 1: Check Gmail for unread email
        print(f"\n[Step 1] Checking Gmail ({gmail_user}) for unread emails...")
        unread = gmail_service.fetch_latest_unread(mark_as_read=False)

        if unread:
            sender = unread["sender"]
            sender_name = unread["sender_name"]
            subject = unread["subject"]
            body = unread["body"]
            is_live = True
            print(f"  • Found unread email from: {sender} | Subject: {subject}")
        else:
            sender = gmail_user
            sender_name = "Paschal Okpalaugo"
            subject = "Inquiry: Nextserve Full-Stack AI Course Orientation"
            body = (
                "Hello Admissions,\n\n"
                "I would like to verify my orientation session for the Full-Stack AI Course.\n\n"
                "Thanks,\nPaschal"
            )
            is_live = False
            print(f"  • No unread email in inbox. Prepared live test inquiry to: {sender}")

        # Step 2: Generate Draft & Persist to PostgreSQL
        print("\n[Step 2] NextClaw AI Reply Draft Generation & DB Persistence...")
        token, draft = create_and_store_draft(
            sender=sender,
            subject=subject,
            body=body,
            sender_name=sender_name,
            email_uid=unread["id"] if unread else None,
            received_date=unread["date"] if unread else None,
        )
        print(f"  • Token: {token}")
        print(f"  • Reply Subject: {draft['subject']}")

        # Step 3: Send Telegram Approval Card
        print("\n[Step 3] Dispatching interactive card to your Telegram as NextClaw...")
        safe_sender_name = html.escape(str(sender_name))
        safe_sender = html.escape(str(sender))
        safe_subject = html.escape(str(subject))
        safe_body_preview = html.escape(str(body[:250]))
        safe_draft_body = html.escape(str(draft["body"]))

        source_tag = "🔴 LIVE UNREAD EMAIL" if is_live else "🧪 LIVE TEST INQUIRY"
        telegram_text = (
            f"📬 <b>{source_tag}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>From:</b> {safe_sender_name} (<code>{safe_sender}</code>)\n"
            f"📌 <b>Subject:</b> <i>{safe_subject}</i>\n\n"
            f"💬 <b>Message Preview:</b>\n"
            f"<i>{safe_body_preview}</i>\n\n"
            "🤖 <b>Proposed NextClaw (Nextserve AI Operational Assistant) Reply:</b>\n"
            f"<pre>{safe_draft_body}</pre>\n\n"
            f"🔑 <b>Approval Token:</b> <code>{token}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👉 <b>Open Telegram on your phone/desktop and tap an option below:</b>"
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve & Send Email", "callback_data": f"approve_{token}"},
                    {"text": "❌ Reject / Cancel", "callback_data": f"reject_{token}"},
                ]
            ]
        }

        tg_res = telegram_service.send_message(
            text=telegram_text,
            chat_id=chat_id,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

        sent_msg_id = tg_res.get("result", {}).get("message_id")
        print(f"  [DELIVERED!] Message ID: {sent_msg_id}")
        log_banner("ACTION REQUIRED: GO TO TELEGRAM NOW")
        print(f"Open your Telegram app (Bot: @GodlypaschalBot).")
        print(f"You will see the card with buttons [✅ Approve] and [❌ Reject].")
        print("Waiting for you to click a button... (Listening for 90 seconds)")

        # Step 4: Long-polling listener for your button click
        start_time = time.time()
        last_offset = 0
        handled = False

        while time.time() - start_time < 90:
            updates_res = requests.get(
                f"https://api.telegram.org/bot{bot_token}/getUpdates",
                params={"offset": last_offset, "timeout": 3},
                timeout=10,
            ).json()

            for update in updates_res.get("result", []):
                last_offset = update["update_id"] + 1
                cb_query = update.get("callback_query")
                if not cb_query:
                    continue

                cb_data = cb_query.get("data", "")
                cb_id = cb_query.get("id")
                cb_msg = cb_query.get("message", {})
                cb_msg_id = cb_msg.get("message_id")
                from_user = cb_query.get("from", {}).get("first_name", "Admin")

                if token in cb_data:
                    print(f"\n⚡ Button Click Detected in Telegram!")
                    print(f"  • Clicked by: {from_user}")
                    print(f"  • Button Data: {cb_data}")

                    result = handle_approval_callback(
                        callback_data=cb_data,
                        callback_query_id=cb_id,
                        chat_id=int(chat_id),
                        message_id=cb_msg_id,
                        reviewer_name=from_user,
                    )

                    print(f"  • Result Status: {result.get('status')}")
                    print(f"  • Decision:      {result.get('decision')}")
                    print(f"  • Dispatched:    {result.get('email_dispatched')}")
                    print(f"  • Final Text:    {result.get('confirmation_text')}")
                    handled = True
                    break

            if handled:
                break
            time.sleep(1)

        if not handled:
            print("\n[TIMEOUT] No button click received within 90 seconds.")
        else:
            print("\n🎉 Live interaction test completed successfully!")

    finally:
        # Restore previous webhook if it was set
        if prev_webhook:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                json={"url": prev_webhook, "allowed_updates": ["message", "callback_query"]},
            )
            print(f"[*] Restored previous webhook: {prev_webhook}")


if __name__ == "__main__":
    main()
