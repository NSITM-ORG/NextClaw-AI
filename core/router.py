"""NextClaw OS - Gateway APIRouter.

Allows seamless embedding of NextClaw OS multi-channel gateway endpoints
directly into the main Nextserve API router.
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, Request, Query, HTTPException, Response
from pydantic import BaseModel

from core.gateway import gateway, InboundMessage
from core.approval_gate import security_gate
from skills import skill_registry

logger = logging.getLogger("nextclaw.router")

gateway_router = APIRouter(prefix="/gateway", tags=["NextClaw OS Gateway"])


class DirectChatRequest(BaseModel):
    query: str
    channel: str = "web"
    sender_id: str = "web_visitor"
    sender_name: Optional[str] = "Prospective Student"


class ApprovalCallbackRequest(BaseModel):
    callback_data: str
    reviewer_name: Optional[str] = "Admin"


@gateway_router.get("/skills", summary="List Active Skills")
def get_skills_status():
    return {
        "status": "success",
        "skills": skill_registry.list_active_skills()
    }


@gateway_router.get("/calendar", summary="Academic Calendar Events")
def get_calendar_events(days_ahead: int = 60):
    cal_skill = skill_registry.get_skill("skill_calendar")
    if cal_skill:
        return cal_skill.execute("list_events", {"days_ahead": days_ahead})
    return {"status": "error", "message": "Calendar skill is not loaded."}


@gateway_router.post("/calendar/send-telegram", summary="Send Academic Calendar Alert to Telegram")
def send_calendar_to_telegram(chat_id: Optional[str] = None):
    """Dispatches real-time academic calendar alert to Telegram bot."""
    cal_skill = skill_registry.get_skill("skill_calendar")
    if cal_skill:
        return cal_skill.execute("send_telegram_notification", {"chat_id": chat_id})
    return {"status": "error", "message": "Calendar skill is not loaded."}



@gateway_router.post("/chat", summary="Multi-Channel Direct Chat")
def direct_chat(req: DirectChatRequest):
    inbound = InboundMessage(
        channel=req.channel,
        sender_id=req.sender_id,
        sender_name=req.sender_name,
        text=req.query
    )
    outbound = gateway.process_inbound(inbound, dispatch_outbound=False)
    return {
        "status": outbound.status,
        "tier": outbound.tier,
        "channel": outbound.channel,
        "reply": outbound.text,
        "details": outbound.extra
    }


@gateway_router.post("/webhook", summary="Inbound Generic Webhook")
async def generic_webhook(request: Request):
    payload = await request.json()
    inbound = gateway.normalize_webhook_payload(payload)
    outbound = gateway.process_inbound(inbound, dispatch_outbound=True)
    return {
        "status": outbound.status,
        "tier": outbound.tier,
        "reply": outbound.text,
        "extra": outbound.extra
    }


@gateway_router.post("/telegram", summary="Telegram Bot Inbound Webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    inbound = gateway.normalize_telegram_update(update)
    if inbound:
        outbound = gateway.process_inbound(inbound, dispatch_outbound=True)
        return {"ok": True, "action": "processed_message", "tier": outbound.tier}
    return {"ok": True, "action": "processed_callback_or_non_text"}


@gateway_router.get("/whatsapp", summary="Meta WhatsApp Verification")
def whatsapp_verify_token(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "nextclaw_secret_token")
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Invalid verification token")


@gateway_router.post("/whatsapp", summary="Meta WhatsApp Inbound Webhook")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    inbound = gateway.normalize_whatsapp_webhook(payload)
    if inbound:
        outbound = gateway.process_inbound(inbound, dispatch_outbound=True)
        return {"status": "success", "tier": outbound.tier}
    return {"status": "ignored_non_message_event"}


@gateway_router.post("/email", summary="Inbound Email Webhook")
async def email_inbound_webhook(request: Request):
    payload = await request.json()
    inbound = gateway.normalize_email_payload(payload)
    outbound = gateway.process_inbound(inbound, dispatch_outbound=True)
    return {
        "status": "success",
        "tier": outbound.tier,
        "reply": outbound.text,
        "recipient": outbound.recipient
    }


@gateway_router.post("/approval/callback", summary="Tier 3 Approval Callback")
def process_approval_callback(req: ApprovalCallbackRequest):
    res = security_gate.process_admin_callback(
        callback_data=req.callback_data,
        reviewer_name=req.reviewer_name or "Admin"
    )
    return res


def interactive_dashboard():
    """Interactive NextClaw Dashboard with Academic Calendar and Live Test Console."""
    from fastapi.responses import HTMLResponse
    cal_skill = skill_registry.get_skill("skill_calendar")
    events_data = cal_skill.execute("list_events", {"days_ahead": 60}) if cal_skill else {"events": []}
    events = events_data.get("events", [])

    events_html = ""
    for e in events:
        badge_color = "#38bdf8" if e.get("type") == "webinar" else ("#10b981" if e.get("type") == "cohort_start" else "#f59e0b")
        events_html += f"""
        <div style="background:rgba(30,41,59,0.7); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:18px; margin-bottom:14px; backdrop-filter:blur(8px);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="background:{badge_color}22; color:{badge_color}; border:1px solid {badge_color}44; font-size:11px; font-weight:700; padding:3px 10px; border-radius:12px; text-transform:uppercase;">{e.get('type','event').replace('_',' ')}</span>
                <span style="color:#94a3b8; font-size:12px; font-weight:600;">{e.get('time_until', '')}</span>
            </div>
            <h3 style="color:#f8fafc; font-size:16px; margin:0 0 6px 0; font-weight:600;">{e.get('title')}</h3>
            <div style="color:#cbd5e1; font-size:13px; line-height:1.5; margin-bottom:10px;">{e.get('description', '')}</div>
            <div style="display:flex; flex-wrap:wrap; gap:12px; font-size:12px; color:#94a3b8; border-top:1px solid rgba(255,255,255,0.06); padding-top:10px;">
                <span>⏰ <b>Date:</b> {e.get('formatted_date', e.get('start_time'))}</span>
                <span>📍 <b>Venue:</b> {e.get('location', 'Online')}</span>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextClaw — Academic Calendar & Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #0b0f19; color: #f1f5f9; min-height: 100vh; padding: 24px; }}
        .header {{ max-width: 1200px; margin: 0 auto 28px auto; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 20px; }}
        .logo-title {{ display: flex; align-items: center; gap: 14px; }}
        .logo-box {{ width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #0284c7, #06b6d4); display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; color: white; }}
        .pill {{ background: #10b98122; color: #10b981; border: 1px solid #10b98144; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 600; }}
        .grid {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.1fr 1fr; gap: 24px; }}
        .card {{ background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .card h2 {{ font-size: 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: #f8fafc; }}
        .chat-box {{ background: #0d131f; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; height: 380px; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }}
        .msg {{ padding: 12px 16px; border-radius: 12px; font-size: 13.5px; line-height: 1.5; max-width: 88%; word-break: break-word; }}
        .msg.user {{ align-self: flex-end; background: #0284c7; color: #ffffff; border-bottom-right-radius: 2px; }}
        .msg.agent {{ align-self: flex-start; background: #1e293b; color: #e2e8f0; border: 1px solid rgba(255,255,255,0.08); border-bottom-left-radius: 2px; }}
        .tier-badge {{ display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 6px; margin-bottom: 4px; }}
        .tier-1 {{ background: #10b98122; color: #34d399; border: 1px solid #34d39944; }}
        .tier-2 {{ background: #f59e0b22; color: #fbbf24; border: 1px solid #fbbf2444; }}
        .tier-3 {{ background: #ef444422; color: #f87171; border: 1px solid #f8717144; }}
        .presets {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }}
        .preset-btn {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 12px; padding: 6px 12px; border-radius: 8px; cursor: pointer; transition: 0.15s; }}
        .preset-btn:hover {{ background: rgba(2,132,199,0.15); border-color: #38bdf8; color: #38bdf8; }}
        .input-row {{ display: flex; gap: 10px; }}
        .input-row input {{ flex: 1; background: #0d131f; border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 12px 16px; border-radius: 10px; font-size: 14px; outline: none; }}
        .input-row select {{ background: #0d131f; border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 0 12px; border-radius: 10px; font-size: 13px; outline: none; }}
        .send-btn {{ background: #0284c7; color: #fff; border: none; padding: 0 20px; border-radius: 10px; font-weight: 600; cursor: pointer; transition: 0.15s; }}
        .send-btn:hover {{ background: #0369a1; }}
        .approval-box {{ margin-top: 14px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 14px; display: none; }}
        .action-btn {{ padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; border: none; margin-right: 8px; }}
        .approve-btn {{ background: #10b981; color: white; }}
        .reject-btn {{ background: #ef4444; color: white; }}
        .tg-notify-btn {{ background: linear-gradient(135deg, #0284c7, #0284c7); color: white; border: none; padding: 10px 18px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; margin-bottom: 16px; transition: 0.2s; }}
        .tg-notify-btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-title">
            <div class="logo-box">NC</div>
            <div>
                <h1 style="font-size:20px; font-weight:700;">NextClaw Academic Console</h1>
                <p style="font-size:13px; color:#94a3b8;">Nextserve School of Information Technology & Management</p>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <a href="/app/" style="color:#10b981; text-decoration:none; font-size:13px; font-weight:600;">Open School UI ↗</a>
            <a href="/docs" target="_blank" style="color:#38bdf8; text-decoration:none; font-size:13px; font-weight:600;">Swagger Docs ↗</a>
            <span class="pill">● System Healthy</span>
        </div>
    </div>

    <div class="grid">
        <!-- Live Chat Console -->
        <div class="card">
            <h2>💬 Multi-Channel Agent Test Console</h2>
            
            <div class="presets">
                <button class="preset-btn" onclick="sendPreset('How much is Fullstack Web Development tuition?')">💰 Fullstack Tuition</button>
                <button class="preset-btn" onclick="sendPreset('What is the 3-tranche instalment breakdown for AI Engineering?')">💳 Instalment Plan</button>
                <button class="preset-btn" onclick="sendPreset('When is the next cohort starting and what events are scheduled?')">📅 Next Cohort</button>
                <button class="preset-btn" onclick="sendPreset('What is the school refund policy?')">📜 Refund Policy</button>
                <button class="preset-btn" onclick="sendPreset('I would like to defer my admission to the next cohort')">🚨 Request Deferral (Tier 3)</button>
            </div>

            <div class="chat-box" id="chatBox">
                <div class="msg agent">
                    <span class="tier-badge tier-1">TIER 1 (SAFE)</span><br>
                    Welcome to <b>NextClaw</b>! Ask any question about Nextserve's 26 programmes, tuition schedules, flexible instalments, academic policies, or cohort kick-offs.
                </div>
            </div>

            <div id="approvalBox" class="approval-box">
                <b style="color:#f87171;">🚨 Tier 3 Telegram Approval Gate Triggered!</b>
                <div id="approvalDetails" style="font-size:12px; margin:6px 0 10px 0; color:#cbd5e1;"></div>
                <button class="action-btn approve-btn" id="btnApprove" onclick="resolveApproval(true)">✅ [Approve & Execute]</button>
                <button class="action-btn reject-btn" id="btnReject" onclick="resolveApproval(false)">❌ [Reject / Revise]</button>
            </div>

            <form id="chatForm" onsubmit="handleSend(event)" style="margin-top:14px;">
                <div class="input-row">
                    <select id="channelSelect">
                        <option value="web">🌐 Web Chat</option>
                        <option value="whatsapp">📱 WhatsApp</option>
                        <option value="telegram">✈️ Telegram</option>
                        <option value="email">✉️ Email</option>
                    </select>
                    <input type="text" id="userInput" placeholder="Ask about fees, courses, calendar, or deferral..." autocomplete="off">
                    <button type="submit" class="send-btn">Send</button>
                </div>
            </form>
        </div>

        <!-- Academic Calendar View -->
        <div class="card">
            <h2>📅 Nextserve Academic Calendar & Events</h2>
            <button class="tg-notify-btn" onclick="sendCalendarTelegram()">
                <span>📲 Send Calendar Alert to My Telegram</span>
            </button>
            <div id="tgAlertStatus" style="display:none; font-size:12px; padding:8px 12px; border-radius:8px; margin-bottom:12px; background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3);"></div>
            <div style="font-size:13px; color:#94a3b8; margin-bottom:16px;">
                Synced with <code>configs/CALENDAR.json</code>. Automated reminders are sent before upcoming events.
            </div>
            <div style="max-height: 480px; overflow-y: auto; padding-right: 4px;">
                {events_html}
            </div>
        </div>
    </div>

    <script>
        let currentTicketId = null;

        async function sendCalendarTelegram() {{
            const statusBox = document.getElementById('tgAlertStatus');
            statusBox.style.display = 'block';
            statusBox.innerText = '⏳ Dispatching calendar alert to your Telegram...';
            try {{
                const res = await fetch('/api/v1/gateway/calendar/send-telegram', {{ method: 'POST' }});
                const data = await res.json();
                statusBox.innerText = '✅ Academic Calendar Alert dispatched to your Telegram successfully!';
            }} catch(err) {{
                statusBox.innerText = '❌ Failed to send Telegram: ' + err;
            }}
        }}

        function sendPreset(text) {{
            document.getElementById('userInput').value = text;
            handleSend(new Event('submit'));
        }}

        async function handleSend(e) {{
            e.preventDefault();
            const input = document.getElementById('userInput');
            const channel = document.getElementById('channelSelect').value;
            const query = input.value.trim();
            if (!query) return;

            input.value = '';
            appendMsg(query, 'user');

            try {{
                const res = await fetch('/api/v1/gateway/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ query: query, channel: channel, sender_id: 'tester', sender_name: 'Test Student' }})
                }});
                const data = await res.json();
                
                const tier = data.tier || 1;
                const tierClass = 'tier-' + tier;
                const tierLabel = tier === 1 ? 'TIER 1 (SAFE AUTO)' : (tier === 2 ? 'TIER 2 (DRAFT REVIEW)' : 'TIER 3 (HITL APPROVAL)');
                
                appendMsg(`<span class="tier-badge ${{tierClass}}">${{tierLabel}}</span><br>` + data.reply, 'agent');

                if (tier === 3 && data.details && data.details.ticket_id) {{
                    currentTicketId = data.details.ticket_id;
                    const appBox = document.getElementById('approvalBox');
                    document.getElementById('approvalDetails').innerText = `Ticket ID: [${{currentTicketId}}] - Administrative approval dispatched to Admin Telegram. You can also approve/reject right here:`;
                    appBox.style.display = 'block';
                }}
            }} catch(err) {{
                appendMsg("Error communicating with NextClaw: " + err, 'agent');
            }}
        }}

        async function resolveApproval(approve) {{
            if (!currentTicketId) return;
            const cb = (approve ? 't3_approve_' : 't3_reject_') + currentTicketId;
            try {{
                const res = await fetch('/api/v1/gateway/approval/callback', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ callback_data: cb, reviewer_name: 'Director (Dashboard)' }})
                }});
                const data = await res.json();
                document.getElementById('approvalBox').style.display = 'none';
                appendMsg(`⚡ <b>Security Gate Decision Recorded:</b> Ticket [${{currentTicketId}}] was <b>${{data.decision.toUpperCase()}}</b> by Director.`, 'agent');
                currentTicketId = null;
            }} catch(err) {{
                alert("Approval failed: " + err);
            }}
        }}

        function appendMsg(html, role) {{
            const box = document.getElementById('chatBox');
            const el = document.createElement('div');
            el.className = 'msg ' + role;
            el.innerHTML = html;
            box.appendChild(el);
            box.scrollTop = box.scrollHeight;
        }}
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

