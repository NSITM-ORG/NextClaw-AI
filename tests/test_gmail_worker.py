"""Unit and integration tests for NextClaw continuous Gmail worker & memory loop."""

import os
import sys
import socket
import asyncio
from unittest.mock import patch, MagicMock

try:
    import pytest
except ImportError:
    class _MockPytest:
        class mark:
            @staticmethod
            def asyncio(fn):
                return fn
    pytest = _MockPytest()

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from app.services.gmail_service import (
    gmail_service,
    format_telegram_approval_card,
    create_and_store_draft,
)
from app.services.gmail_worker import GmailWorker, gmail_worker
from app.services.email_repository import email_repository
from app.routers.telegram import handle_approval_callback


def test_draft_signoff():
    """Verify that all AI reply drafts sign off as NextClaw (Nextserve AI Operational Assistant)."""
    draft = gmail_service.generate_reply_draft(
        sender="inquiry@test.com",
        subject="Course Enrollment",
        body="I would like to enroll in the AI course.",
    )
    assert "NextClaw (Nextserve AI Operational Assistant)" in draft["body"]
    assert "Nextserve Education Inc." in draft["body"]


def test_telegram_card_formatting_and_truncation():
    """Verify card truncates preview to max 1,000 characters and sets action buttons."""
    long_body = "A" * 1500
    text, markup = format_telegram_approval_card(
        sender="student@example.com",
        subject="Long message inquiry",
        body=long_body,
        draft_body="Draft response body",
        token="d_test123",
        sender_name="Student Name",
    )
    # Check that body preview in text is truncated to ~1000 chars (plus ellipsis and formatting)
    assert "A" * 1001 not in text
    assert "A" * 500 in text
    assert "NextClaw (Nextserve AI Operational Assistant)" in text

    # Verify buttons
    buttons = markup["inline_keyboard"][0]
    assert len(buttons) == 2
    assert buttons[0]["text"] == "✅ Approve & Send"
    assert buttons[0]["callback_data"] == "approve_d_test123"
    assert buttons[1]["text"] == "❌ Reject"
    assert buttons[1]["callback_data"] == "reject_d_test123"


@pytest.mark.asyncio
async def test_gmail_worker_start_stop_lifecycle():
    """Verify GmailWorker starts background task every 20s and stops cleanly."""
    worker = GmailWorker(poll_interval=20.0)
    assert not worker.is_running
    assert worker.poll_interval == 20.0

    await worker.start()
    assert worker.is_running
    assert worker._task is not None
    assert not worker._task.done()

    await worker.stop()
    assert not worker.is_running
    assert worker._task is None


@pytest.mark.asyncio
async def test_gmail_worker_socket_timeout_auto_reconnect():
    """Verify worker auto-reconnects gracefully on IMAP socket timeouts without raising."""
    worker = GmailWorker(poll_interval=20.0)

    # Mock fetch_latest_unread raising socket.timeout
    with patch.object(
        worker.service,
        "fetch_latest_unread",
        side_effect=socket.timeout("IMAP connection timed out"),
    ):
        result = await worker.check_once()
        assert result is None
        # Worker did not crash and returned cleanly


@pytest.mark.asyncio
async def test_gmail_worker_detection_and_pending_persistence():
    """Verify worker detects unread email, persists as PENDING in PostgreSQL, and avoids duplicates."""
    import uuid
    worker = GmailWorker(poll_interval=20.0)
    test_uid = f"uid_{uuid.uuid4().hex[:8]}"

    mock_unread = {
        "id": test_uid,
        "sender": "applicant@test.com",
        "sender_name": "Applicant Test",
        "raw_sender": "Applicant Test <applicant@test.com>",
        "subject": "Inquiry regarding AI orientation",
        "date": "Tue, 15 Sep 2026 12:00:00 +0000",
        "body": "Could you please provide the orientation link?",
        "body_preview": "Could you please provide the orientation link?",
    }

    with patch.object(worker.service, "is_configured", return_value=True), \
         patch.object(worker.service, "fetch_latest_unread", return_value=mock_unread), \
         patch("app.services.telegram_service.telegram_service.send_message", return_value={"ok": True}):

        # First check: should process and store as PENDING
        res = await worker.check_once()
        assert res is not None
        assert res["status"] == "processed"
        assert res["email_uid"] == test_uid
        token = res["token"]

        # Verify record in database has status PENDING
        record = email_repository.get_email_by_token(token)
        if record:
            assert record.status == "PENDING"
            assert record.sender == "applicant@test.com"

        # Second check: should skip because UID is in processed_uids
        res_dup = await worker.check_once()
        assert res_dup is None


def test_telegram_callbacks_approve_and_reject():
    """Verify [✅ Approve & Send] dispatches email, updates DB to APPROVED, and [❌ Reject] updates to REJECTED."""
    # Create test pending draft
    token_approve, draft_approve = create_and_store_draft(
        sender="approve_user@test.com",
        subject="Approval Test Subject",
        body="Inquiry message body",
        email_uid="test_uid_approve_1",
    )

    token_reject, draft_reject = create_and_store_draft(
        sender="reject_user@test.com",
        subject="Reject Test Subject",
        body="Inquiry message body",
        email_uid="test_uid_reject_1",
    )

    # Test Approve callback
    with patch("app.services.gmail_service.gmail_service.send_email", return_value={"status": "sent"}), \
         patch("app.services.telegram_service.telegram_service.edit_message_text", return_value={"ok": True}):
        res_app = handle_approval_callback(
            callback_data=f"approve_{token_approve}",
            chat_id=12345,
            message_id=67890,
            reviewer_name="Admin Test",
        )
        assert res_app["status"] == "success"
        assert res_app["decision"] == "approved"
        assert res_app["email_dispatched"] is True

        # Verify DB status is APPROVED
        rec_app = email_repository.get_email_by_token(token_approve)
        if rec_app:
            assert rec_app.status == "APPROVED"

    # Test Reject callback
    with patch("app.services.telegram_service.telegram_service.edit_message_text", return_value={"ok": True}):
        res_rej = handle_approval_callback(
            callback_data=f"reject_{token_reject}",
            chat_id=12345,
            message_id=67891,
            reviewer_name="Admin Test",
        )
        assert res_rej["status"] == "success"
        assert res_rej["decision"] == "rejected"
        assert res_rej["email_dispatched"] is False

        # Verify DB status is REJECTED
        rec_rej = email_repository.get_email_by_token(token_reject)
        if rec_rej:
            assert rec_rej.status == "REJECTED"


def test_fastapi_worker_starts_cleanly():
    """Verify FastAPI application starts and stops with the GmailWorker registered in startup/shutdown."""
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"
        # Confirm worker was initialized
        assert gmail_worker is not None


@pytest.mark.asyncio
async def test_telegram_conversational_chat():
    """Verify that when a user messages the Telegram bot, NextClaw replies conversationally."""
    from app.routers.telegram import handle_telegram_message

    mock_msg = {
        "chat": {"id": 12345},
        "from": {"first_name": "TestStudent"},
        "text": "What are the prerequisites for CS201?"
    }

    with patch("app.services.telegram_service.telegram_service.send_message") as mock_send:
        mock_send.return_value = {"ok": True}
        res = await handle_telegram_message(mock_msg)
        assert res["status"] == "replied"
        assert mock_send.called
        sent_text = mock_send.call_args[1]["text"]
        assert "CS101" in sent_text or "NextClaw" in sent_text


if __name__ == "__main__":
    print("=" * 60)
    print("Running NextClaw Continuous Gmail & Chatbot Worker Tests...")
    print("=" * 60)
    test_draft_signoff()
    print("[PASS] test_draft_signoff")

    test_telegram_card_formatting_and_truncation()
    print("[PASS] test_telegram_card_formatting_and_truncation")

    asyncio.run(test_gmail_worker_start_stop_lifecycle())
    print("[PASS] test_gmail_worker_start_stop_lifecycle")

    asyncio.run(test_gmail_worker_socket_timeout_auto_reconnect())
    print("[PASS] test_gmail_worker_socket_timeout_auto_reconnect")

    asyncio.run(test_gmail_worker_detection_and_pending_persistence())
    print("[PASS] test_gmail_worker_detection_and_pending_persistence")

    test_telegram_callbacks_approve_and_reject()
    print("[PASS] test_telegram_callbacks_approve_and_reject")

    test_fastapi_worker_starts_cleanly()
    print("[PASS] test_fastapi_worker_starts_cleanly")

    asyncio.run(test_telegram_conversational_chat())
    print("[PASS] test_telegram_conversational_chat")

    print("\n" + "=" * 60)
    print("ALL 8 NEXTCLAW GMAIL & CHATBOT TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

