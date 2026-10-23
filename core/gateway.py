"""NextClaw OS - Multi-Channel Request Gateway (core/gateway.py).

Unified entry point normalizing incoming messages from:
- Meta WhatsApp Cloud API
- Telegram Bot API (messages & button callbacks)
- Webhooks / REST API
- Inbound Email (Gmail / SMTP / Webhook)

Routes normalized requests to NextClaw Engine and dispatches replies
back through the originating channel.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from core.engine import engine
from core.approval_gate import security_gate
from skills.skill_messaging import MessagingSkill

logger = logging.getLogger("nextclaw.gateway")


class InboundMessage(BaseModel):
    """Standardized multi-channel inbound payload format."""
    channel: str = Field(..., description="whatsapp, telegram, webhook, email, or chat")
    sender_id: str = Field(..., description="Phone number, Telegram chat ID, email, or user ID")
    sender_name: Optional[str] = Field(None, description="Sender display name")
    text: str = Field(..., description="Inbound text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw channel-specific headers/metadata")


class OutboundMessage(BaseModel):
    """Standardized outbound response payload."""
    channel: str
    recipient: str
    text: str
    tier: int = 1
    status: str = "success"
    extra: Dict[str, Any] = Field(default_factory=dict)


class ChannelGateway:
    """Normalizes and routes multi-channel traffic to the NextClaw OS core."""

    def __init__(self):
        self.messaging = MessagingSkill()

    def process_inbound(self, msg: InboundMessage, dispatch_outbound: bool = True) -> OutboundMessage:
        """Processes a normalized inbound message and dispatches the response."""
        logger.info(f"Gateway received [{msg.channel.upper()}] message from {msg.sender_id}: '{msg.text[:60]}...'")

        # Route through engine
        engine_res = engine.process_request(
            query=msg.text,
            channel=msg.channel,
            sender_id=msg.sender_id,
            sender_name=msg.sender_name,
            context=msg.metadata
        )

        response_text = engine_res.get("response", "Thank you for contacting Nextserve.")
        tier = engine_res.get("tier", 1)

        outbound = OutboundMessage(
            channel=msg.channel,
            recipient=msg.sender_id,
            text=response_text,
            tier=tier,
            status=engine_res.get("status", "success"),
            extra=engine_res
        )

        # Dispatch back through originating channel
        if dispatch_outbound:
            self.messaging.dispatch_reply(
                channel=msg.channel,
                recipient=msg.sender_id,
                text=response_text,
                extra=engine_res
            )

        return outbound

    # ── Channel Normalizers ───────────────────────────────────────────

    def normalize_whatsapp_webhook(self, payload: Dict[str, Any]) -> Optional[InboundMessage]:
        """Normalizes Meta WhatsApp Cloud API webhook JSON payload."""
        try:
            entry = payload.get("entry", [])[0]
            change = entry.get("changes", [])[0]
            val = change.get("value", {})
            messages = val.get("messages", [])
            if not messages:
                return None

            msg_data = messages[0]
            contact = val.get("contacts", [{}])[0]
            sender_phone = msg_data.get("from")
            sender_name = contact.get("profile", {}).get("name")
            text = msg_data.get("text", {}).get("body", "")

            return InboundMessage(
                channel="whatsapp",
                sender_id=sender_phone,
                sender_name=sender_name,
                text=text,
                metadata={"whatsapp_msg_id": msg_data.get("id"), "raw_payload": payload}
            )
        except Exception as exc:
            logger.error(f"Failed to normalize WhatsApp payload: {exc}")
            return None

    def normalize_telegram_update(self, update: Dict[str, Any]) -> Optional[InboundMessage]:
        """Normalizes Telegram Bot API update payload."""
        # 1. Handle message
        msg = update.get("message")
        if msg and "text" in msg:
            chat_id = str(msg.get("chat", {}).get("id"))
            first_name = msg.get("from", {}).get("first_name", "Telegram User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            text = msg.get("text", "")

            return InboundMessage(
                channel="telegram",
                sender_id=chat_id,
                sender_name=full_name,
                text=text,
                metadata={"message_id": msg.get("message_id"), "raw_update": update}
            )

        # 2. Handle callback query (e.g. inline button clicks)
        cb = update.get("callback_query")
        if cb:
            cb_data = cb.get("data", "")
            reviewer = cb.get("from", {}).get("first_name", "Telegram Admin")
            chat_id = str(cb.get("message", {}).get("chat", {}).get("id"))

            # Process through Security Gate
            res = security_gate.process_admin_callback(callback_data=cb_data, reviewer_name=reviewer)

            # Send acknowledgement back to Telegram
            self.messaging.send_telegram_message(
                chat_id=chat_id,
                text=f"⚡ <b>Action Processed:</b> {res.get('message')}"
            )
            return None

        return None

    def normalize_email_payload(self, payload: Dict[str, Any]) -> InboundMessage:
        """Normalizes an inbound email webhook payload."""
        sender = payload.get("sender") or payload.get("from") or "anonymous@example.com"
        subject = payload.get("subject", "")
        body = payload.get("body") or payload.get("text") or ""
        sender_name = payload.get("sender_name")

        return InboundMessage(
            channel="email",
            sender_id=sender,
            sender_name=sender_name,
            text=f"{subject}\n\n{body}".strip(),
            metadata={"subject": subject, "body": body, "raw_email": payload}
        )

    def normalize_webhook_payload(self, payload: Dict[str, Any]) -> InboundMessage:
        """Normalizes a generic REST/Webhook JSON payload."""
        return InboundMessage(
            channel=payload.get("channel", "webhook"),
            sender_id=payload.get("sender_id", "webhook_client"),
            sender_name=payload.get("sender_name", "Webhook User"),
            text=payload.get("text") or payload.get("query") or payload.get("message", ""),
            metadata=payload.get("metadata", {})
        )


gateway = ChannelGateway()
