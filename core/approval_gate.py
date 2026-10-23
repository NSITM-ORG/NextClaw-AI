"""NextClaw OS - 3-Tier Security & Human-in-the-Loop Gate (approval_gate.py).

Classifies and guards all tool actions into 3 execution tiers:
- TIER 1: Safe / Read-Only (Executes automatically 24/7)
- TIER 2: Draft & Review (Generates draft + preview link/card, pauses for review)
- TIER 3: High Risk / Administrative (Dispatches Telegram Approval Card to Admin, pauses until callback)
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable

from core.db import get_db_session, ApprovalTicket, NextClawAuditLog

logger = logging.getLogger("nextclaw.approval_gate")

# Classification matrix
TIER_1_ACTIONS = {
    "query", "search", "get_course", "course_details", "calculate_instalments",
    "list_courses", "list_events", "get_events", "get_next_cohort", "check_reminders",
    "generate_preview", "preview", "list_drafts"
}

TIER_2_ACTIONS = {
    "draft_announcement", "create_draft", "draft", "schedule_event", "create_event",
    "draft_email", "email_draft", "generate_flyer", "social_post"
}

TIER_3_ACTIONS = {
    "approve_deferral", "deferral", "update_payment_status", "reconcile_payment",
    "publish_live", "publish", "mass_broadcast", "delete_record", "override_balance"
}


class SecurityGate:
    """Security engine enforcing 3-Tier Human-in-the-Loop constraints."""

    def __init__(self):
        self._action_registry: Dict[str, Callable] = {}
        self._pending_executions: Dict[str, Dict[str, Any]] = {}

    def register_execution_handler(self, action_name: str, handler: Callable):
        """Registers a callback function to execute when a Tier 3 action is approved."""
        self._action_registry[action_name] = handler

    def classify_action(self, skill_name: str, action: str) -> int:
        """Determines the security tier for a given skill action."""
        act = action.lower()
        if act in TIER_3_ACTIONS:
            return 3
        if act in TIER_2_ACTIONS:
            return 2
        if act in TIER_1_ACTIONS:
            return 1

        # Check skill default if not explicitly listed
        if skill_name == "skill_telegram":
            return 3 if "approval" in act else 1
        if skill_name == "skill_cms" and "publish" in act:
            return 3
        if skill_name == "skill_calendar" and "schedule" in act:
            return 2
        return 1

    def enforce_gate(
        self,
        skill_name: str,
        action: str,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        execute_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Evaluates security rules and intercepts execution if Tier 2 or Tier 3."""
        tier = self.classify_action(skill_name, action)
        ctx = context or {}
        channel = ctx.get("channel", "direct")
        user_id = ctx.get("sender_id", "system")

        # ── TIER 1: Safe / Read-Only ─────────────────────────────────
        if tier == 1:
            self._log_audit(channel, user_id, f"{skill_name}.{action}", 1, "auto_executed", params)
            if execute_fn:
                return execute_fn()
            return {"status": "authorized", "tier": 1, "action": action}

        # ── TIER 2: Draft & Review ───────────────────────────────────
        elif tier == 2:
            self._log_audit(channel, user_id, f"{skill_name}.{action}", 2, "draft_staged", params)
            # Tier 2 creates the draft and holds for manual review
            result = execute_fn() if execute_fn else {"status": "draft_created", "tier": 2}
            result["security_gate"] = {
                "tier": 2,
                "tier_name": "Draft & Review",
                "status": "held_for_review",
                "instructions": "Draft generated. Review preview before sending to student or publishing."
            }
            return result

        # ── TIER 3: High Risk / Administrative ────────────────────────
        elif tier == 3:
            ticket_id = f"T3-{uuid.uuid4().hex[:8].upper()}"
            target = params.get("student_name") or params.get("draft_id") or params.get("target") or "Nextserve System"
            details_str = params.get("reason") or params.get("details") or f"Execution of {action} with parameters: {params}"

            # Store pending ticket in database
            db = get_db_session()
            ticket = ApprovalTicket(
                ticket_id=ticket_id,
                action_name=f"{skill_name}.{action}",
                target=str(target),
                tier=3,
                status="pending",
                details=params,
                requested_by=user_id
            )
            db.add(ticket)
            db.commit()
            db.close()

            # Cache the execution function for callback execution
            if execute_fn:
                self._pending_executions[ticket_id] = {
                    "skill_name": skill_name,
                    "action": action,
                    "params": params,
                    "execute_fn": execute_fn
                }

            # Dispatch interactive Telegram Approval Card to Admin
            from skills.skill_telegram import TelegramSkill
            tg = TelegramSkill()
            card_res = tg.dispatch_approval_card(
                ticket_id=ticket_id,
                action_name=action.replace("_", " ").title(),
                target=str(target),
                details=details_str,
                requester=f"{user_id} via {channel.upper()}"
            )

            self._log_audit(channel, user_id, f"{skill_name}.{action}", 3, "approval_card_dispatched", {
                "ticket_id": ticket_id,
                "card_res": card_res
            })

            return {
                "status": "approval_required",
                "tier": 3,
                "tier_name": "High Risk / Administrative",
                "ticket_id": ticket_id,
                "action": action,
                "message": (
                    f"⚠️ High-risk administrative action '{action}' requires approval. "
                    f"An interactive Approval Card with Ticket ID [{ticket_id}] has been sent to the Admin Telegram channel."
                ),
                "approval_card": card_res
            }

        return {"status": "error", "message": f"Invalid tier {tier}"}

    def process_admin_callback(self, callback_data: str, reviewer_name: str = "Telegram Admin") -> Dict[str, Any]:
        """Processes [ ✅ Approve & Execute ] or [ ❌ Reject / Revise ] callbacks."""
        is_approved = callback_data.startswith("t3_approve_")
        is_rejected = callback_data.startswith("t3_reject_")

        if not (is_approved or is_rejected):
            return {"status": "ignored", "message": "Not a Tier 3 approval callback."}

        ticket_id = callback_data.replace("t3_approve_", "").replace("t3_reject_", "").strip()

        db = get_db_session()
        ticket = db.query(ApprovalTicket).filter(ApprovalTicket.ticket_id == ticket_id).first()

        if not ticket:
            db.close()
            return {"status": "not_found", "message": f"Ticket {ticket_id} not found."}

        if ticket.status != "pending":
            status_prev = ticket.status
            db.close()
            return {"status": "already_resolved", "message": f"Ticket {ticket_id} was already {status_prev}."}

        ticket_status = "approved" if is_approved else "rejected"
        ticket.status = ticket_status
        ticket.reviewer = reviewer_name
        ticket.resolved_at = datetime.now(timezone.utc)
        action_name = str(ticket.action_name)
        target = str(ticket.target)
        db.commit()
        db.close()

        execution_result = None
        if is_approved:
            # Check cached execution
            pending = self._pending_executions.pop(ticket_id, None)
            if pending and pending.get("execute_fn"):
                try:
                    execution_result = pending["execute_fn"]()
                except Exception as exc:
                    logger.error(f"Error executing approved action {action_name}: {exc}")
                    execution_result = {"status": "execution_failed", "error": str(exc)}
            else:
                execution_result = {"status": "executed", "action": action_name, "target": target}

        self._log_audit("telegram", reviewer_name, action_name, 3, ticket_status, {
            "ticket_id": ticket_id,
            "execution_result": execution_result
        })

        return {
            "status": "success",
            "decision": ticket_status,
            "ticket_id": ticket_id,
            "action": action_name,
            "target": target,
            "execution_result": execution_result,
            "message": f"Ticket {ticket_id} {ticket_status.upper()} by {reviewer_name}."
        }

    def _log_audit(self, channel: str, user_id: str, tool: str, tier: int, status: str, details: Any):
        """Records audit log entry in database."""
        try:
            db = get_db_session()
            log = NextClawAuditLog(
                channel=channel,
                user_id=str(user_id),
                tool_invoked=tool,
                tier=tier,
                status=status,
                details=details if isinstance(details, dict) else {"raw": str(details)}
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception as exc:
            logger.debug(f"Audit log write skipped: {exc}")


security_gate = SecurityGate()
