"""School Agent Tools package.
Provides tools for semantic vector retrieval over school knowledge,
exact course & programme lookup, instalment fee calculations,
academic policy checks, and Level 3 Gmail Human-in-the-Loop workflows.
"""

from typing import Optional, Dict, Any, List
import logging
from sqlalchemy import select, or_
from langchain_core.tools import tool

from app.db.session import SessionLocal
from app.db.models import Course, SchoolKnowledgeVector, HAS_PGVECTOR
from app.db.vector_store import get_embedding
from app.knowledge.nsitm_knowledge import (
    INSTITUTION_INFO,
    PROGRAMMES_DATA,
    PAYMENT_INSTALMENT_RULES,
    ACADEMIC_POLICIES,
    ENROLLMENT_WORKFLOW,
    MARKETING_CALENDAR_DATA,
    CAMPAIGN_TRACKER_DATA,
    COHORT_SCHEDULES,
)

logger = logging.getLogger(__name__)


@tool
def query_school_knowledge_base(query: str, content_type: Optional[str] = None, top_k: int = 4) -> str:
    """Search the Nextserve School (NSITM) knowledge base for policies, tuition rules, FAQs,
    academic guidelines, and course information using semantic vector search.

    Args:
        query: Natural language query describing what information is needed.
        content_type: Optional filter by type ('course', 'policy', 'faq').
        top_k: Number of most relevant documents to retrieve (default: 4).

    Returns:
        Formatted string containing relevant knowledge documents and policy snippets.
    """
    db = SessionLocal()
    try:
        query_vector = get_embedding(query)

        if HAS_PGVECTOR:
            dist_col = SchoolKnowledgeVector.embedding.cosine_distance(query_vector).label("distance")
            stmt = select(SchoolKnowledgeVector, dist_col)
            if content_type:
                stmt = stmt.where(SchoolKnowledgeVector.content_type == content_type)
            stmt = stmt.order_by(dist_col.asc()).limit(top_k)
            rows = db.execute(stmt).all()

            if rows:
                output_lines = [f"Found {len(rows)} relevant knowledge item(s) for query: '{query}':\n"]
                for idx, (doc, dist) in enumerate(rows, 1):
                    dist_val = float(dist) if dist is not None else 1.0
                    similarity = max(0.0, 1.0 - dist_val)
                    output_lines.append(
                        f"--- Result {idx} [Type: {doc.content_type.upper()}] (Similarity: {similarity:.2%}) ---\n"
                        f"Title: {doc.title}\n"
                        f"{doc.text_content}\n"
                    )
                return "\n".join(output_lines)

        # Keyword match fallback over DB
        stmt = select(SchoolKnowledgeVector)
        if content_type:
            stmt = stmt.where(SchoolKnowledgeVector.content_type == content_type)
        docs = db.execute(stmt.limit(top_k * 2)).scalars().all()

        query_terms = set(query.lower().split())
        scored = []
        for d in docs:
            score = sum(1 for t in query_terms if t in d.text_content.lower())
            scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)

        selected = [doc for score, doc in scored[:top_k] if score > 0]
        if selected:
            output_lines = [f"Found {len(selected)} relevant knowledge item(s) for query: '{query}':\n"]
            for idx, doc in enumerate(selected, 1):
                output_lines.append(
                    f"--- Result {idx} [Type: {doc.content_type.upper()}] ---\n"
                    f"Title: {doc.title}\n"
                    f"{doc.text_content}\n"
                )
            return "\n".join(output_lines)

        # Direct in-memory authoritative fallback from nsitm_knowledge
        query_lower = query.lower()
        matched_policies = []
        for key, policy in ACADEMIC_POLICIES.items():
            if any(term in key or term in policy["rule"].lower() or term in policy["description"].lower() for term in query_terms):
                matched_policies.append(f"• {policy['rule']}: {policy['description']}")
        
        # Check cohort schedules and campaigns
        matched_calendar = []
        for c in COHORT_SCHEDULES:
            if any(term in c["cohort_name"].lower() or any(term in tr.lower() for tr in c.get("tracks", [])) for term in query_terms):
                matched_calendar.append(f"• {c['cohort_name']} Kickoff: {c['class_start_date']} (Enrollment window: {c['enrollment_window']})")
        for cmp in CAMPAIGN_TRACKER_DATA:
            if any(term in cmp["campaign_name"].lower() or term in cmp["campaign_objective"].lower() for term in query_terms):
                matched_calendar.append(f"• Campaign '{cmp['campaign_name']}' ({cmp['status']}): {cmp['start_date']} to {cmp['end_date']} — {cmp['campaign_objective']}")

        if matched_policies:
            return "Authoritative Nextserve Institutional Policies:\n" + "\n".join(matched_policies)
        if matched_calendar:
            return "Authoritative Nextserve Academic & Campaign Schedule:\n" + "\n".join(matched_calendar)

        return f"No specific school policy or course document matched: '{query}'. Nextserve offers 26 accredited programmes in Tech Development, Management, and Short-Term courses."
    except Exception as exc:
        logger.error("Error executing query_school_knowledge_base: %s", exc)
        return f"Error querying school knowledge base: {str(exc)}"
    finally:
        db.close()


@tool
def get_course_details(course_code_or_name: str) -> str:
    """Retrieve comprehensive specifications for any of the 26 NSITM programmes
    including course name, code, duration, tuition in Naira (₦), instalment plan,
    curriculum skills, and career pathways.

    Args:
        course_code_or_name: Course code (e.g. 'TECH-FSW', 'MGMT-DMK', 'SHORT-MOS')
                             or keyword (e.g. 'Fullstack', 'Frontend', 'Cyber Security', 'UI/UX', 'Digital Marketing').

    Returns:
        Structured course details and tuition breakdown.
    """
    clean_input = course_code_or_name.strip().lower()

    # Search authoritative PROGRAMMES_DATA
    matches = []
    for p in PROGRAMMES_DATA:
        if (clean_input in p["name"].lower() or 
            clean_input in p["slug"].lower() or 
            clean_input in p["course_code"].lower() or
            clean_input in p["category"].lower() or
            any(clean_input in skill.lower() for skill in p.get("skills", []))):
            matches.append(p)

    if not matches:
        return (
            f"Programme '{course_code_or_name}' was not found in the NSITM catalog. "
            f"Nextserve offers 26 programmes across Tech Development (Fullstack, Front-End, Back-End, UI/UX, Data Analytics, Data Science, Cyber Security, etc.), "
            f"Management (Digital Marketing, Project Management, Virtual Assistance, etc.), and Short-Term (MS Office, Video Editing, AutoCAD, QuickBooks)."
        )

    output_lines = []
    for p in matches[:3]:
        full_tuition_str = f"₦{p['tuition']:,.2f}"
        if p.get("instalment_fee"):
            instalment_str = f"₦{p['instalment_fee']:,.2f} (Split: 40% initial, 30% Day 30, 30% Day 60)"
        else:
            instalment_str = "Full payment required upon enrollment (Short-Term course)"

        skills_list = ", ".join(p.get("skills", []))
        careers_list = ", ".join(p.get("careers", []))

        output_lines.append(
            f"=== {p['name']} ({p['course_code']}) ===\n"
            f"• Category: {p['category_label']}\n"
            f"• Duration: {p['duration']}\n"
            f"• Tuition (Full Payment): {full_tuition_str}\n"
            f"• Tuition (Instalment Plan): {instalment_str}\n"
            f"• Key Skills: {skills_list}\n"
            f"• Target Careers: {careers_list}\n"
            f"• Schedule & Delivery: {p.get('schedule', 'Online Virtual Cohorts, Lagos Campus Hub, or Hybrid')}\n"
            f"• Summary: {p['summary']}\n"
        )
    return "\n".join(output_lines)


@tool
def calculate_tuition_instalments(programme_name: str) -> str:
    """Calculates the exact 3-part instalment payment breakdown in Nigerian Naira (₦)
    for any 6-month Tech Development or Management programme at Nextserve.

    Args:
        programme_name: Name or keyword of the programme (e.g. 'Fullstack', 'Frontend', 'UI/UX', 'Project Management').

    Returns:
        Exact payment amounts for Tranche 1 (40%), Tranche 2 (30%), and Tranche 3 (30%).
    """
    clean = programme_name.strip().lower()
    match = None
    for p in PROGRAMMES_DATA:
        if clean in p["name"].lower() or clean in p["slug"].lower() or clean in p["course_code"].lower():
            match = p
            break

    if not match:
        return f"Could not calculate instalments: programme '{programme_name}' not found. Please provide a valid NSITM course name."

    if not match.get("instalment_fee") or not match.get("instalment_breakdown"):
        return (
            f"{match['name']} is a Short-Term programme ({match['duration']}) with a fixed tuition of ₦{match['tuition']:,.2f}. "
            "Short-term courses are not eligible for instalment payments and require 100% full payment upon enrollment."
        )

    breakdown = match["instalment_breakdown"]
    lines = [
        f"📊 Instalment Payment Breakdown for {match['name']}:",
        f"• Total Tuition via Instalment: ₦{match['instalment_fee']:,.2f} (Full payment upfront is ₦{match['tuition']:,.2f})",
        f"• Number of Tranches: 3 parts",
        f"• Tranche 1 (40% Initial Deposit): ₦{breakdown[0]['amount']:,.2f} — Due at enrollment (Step 3/4)",
        f"• Tranche 2 (30% Second Payment): ₦{breakdown[1]['amount']:,.2f} — Due 30 days after first confirmation",
        f"• Tranche 3 (30% Final Payment): ₦{breakdown[2]['amount']:,.2f} — Due 60 days after first confirmation",
        f"• Payment Portal: Students track balances and upload receipts anytime at /my-payment",
        f"• Bank Details: Guaranty Trust Bank (GTB) — provided automatically during Step 4 checkout."
    ]
    return "\n".join(lines)


@tool
def get_institution_info() -> str:
    """Returns official institutional history, leadership background, accreditation,
    contact numbers, WhatsApp links, and physical hub location for Nextserve (NSITM).
    """
    info = INSTITUTION_INFO
    founder = info["founder"]
    stats = info["stats"]
    contacts = info["contacts"]

    return (
        f"🏛️ {info['name']} ({info['short_name']})\n"
        f"• Established: {info['established_year']} ({info['years_of_experience']} years of continuous excellence)\n"
        f"• Tagline: {info['tagline']}\n"
        f"• Leadership: {founder['title']}, Alumnus of {founder['education']}. {founder['background']}\n"
        f"• Track Record: {stats['graduates']} graduates trained, {stats['instructors']} expert industry instructors, {stats['programmes_count']} active programmes.\n"
        f"• Delivery Formats:\n"
        f"   - Online: Nationwide live virtual classes with mentors\n"
        f"   - In-Person: Hands-on training hub in Lagos, Nigeria\n"
        f"   - Hybrid: Flexible combo of online lectures and campus labs\n"
        f"• Official Contacts:\n"
        f"   - WhatsApp: {contacts['whatsapp_number']} ({contacts['whatsapp_link']})\n"
        f"   - Email: {contacts['email']}\n"
        f"   - Campus Hub: {contacts['address']}\n"
    )


@tool
def get_academic_and_admission_policies(topic: Optional[str] = None) -> str:
    """Retrieve strict institutional policies regarding 80% class attendance,
    capstone project defense, strict no-refund policy, deferrals, and the 4-step admissions workflow.

    Args:
        topic: Optional topic filter ('attendance', 'refund', 'capstone', 'admissions').
    """
    t = (topic or "").lower()
    lines = ["📜 NSITM Official Academic & Admissions Policies:"]

    if not t or "attendance" in t:
        lines.append(f"• Attendance Rule: {ACADEMIC_POLICIES['attendance']['rule']} - {ACADEMIC_POLICIES['attendance']['description']}")

    if not t or "capstone" in t:
        lines.append(f"• Capstone Defense: {ACADEMIC_POLICIES['capstone']['rule']} - {ACADEMIC_POLICIES['capstone']['description']}")

    if not t or "refund" in t:
        ref = ACADEMIC_POLICIES['refund_policy']
        lines.append(f"• Refund Policy: {ref['rule']} - {ref['description']}")
        lines.append(f"  Cancellation prior to start: {ref['prior_cancellation']}")
        lines.append(f"  Emergency Deferral: {ref['deferral']}")

    if not t or "admissions" in t or "enrollment" in t:
        lines.append("• Guided 4-Step Enrollment Workflow:")
        for s in ENROLLMENT_WORKFLOW['steps']:
            lines.append(f"   Step {s['step']} ({s['name']}): {s['details']}")
        lines.append(f"  Lead Protection: {ENROLLMENT_WORKFLOW['abandonment_protection']}")

    return "\n".join(lines)


@tool
def get_company_calendar_and_events(query_or_date: Optional[str] = None) -> str:
    """Retrieve scheduled company marketing posts, educational video series episodes,
    dates, platforms, and content release milestones from the Nextserve Marketing Calendar.

    Args:
        query_or_date: Optional search keyword (e.g. 'Dev', 'UIUX', 'VA', 'Tobi', 'Build Log', 'Two Roads')
                       or month/year (e.g. 'May 2026', 'October 2026', '2027').
    """
    q = (query_or_date or "").strip().lower()
    q_terms = [t for t in q.split() if len(t) > 2]
    items = []
    for item in MARKETING_CALENDAR_DATA:
        title_lower = item["title"].lower()
        if not q or (
            q in title_lower or
            title_lower in q or
            q in item["post_date"].lower() or
            any(t in title_lower for t in q_terms) or
            any(t in item.get("category", "").lower() for t in q_terms) or
            any(t in p.lower() for p in item.get("platforms", []) for t in q_terms)
        ):
            items.append(item)

    if not items:
        return f"No scheduled calendar events or marketing posts found matching '{query_or_date}'."

    lines = [f"📅 Nextserve Marketing & Content Calendar ({len(items)} matching event(s)):\n"]
    for it in items[:15]:
        plats = ", ".join(it.get("platforms", []))
        status = it.get("status", "Scheduled")
        lines.append(
            f"• [{it['post_date']}] {it['title']} ({status})\n"
            f"   Category: {it.get('category', 'General')} | Platforms: {plats}"
        )
    if len(items) > 15:
        lines.append(f"\n...and {len(items) - 15} more scheduled content posts.")
    return "\n".join(lines)


@tool
def get_cohort_and_campaign_schedules(cohort_or_campaign: Optional[str] = None) -> str:
    """Retrieve official academic cohort schedules, start dates, enrollment deadlines,
    orientation dates, and strategic marketing campaigns (e.g. Pitch Contest, Weekend Cohort,
    Summer Programme, Cohort 2, Cohort 3, Cohort 4) from Nextserve's Campaign Tracker.

    Args:
        cohort_or_campaign: Optional search keyword (e.g. 'Cohort 2', 'Cohort 3', 'Cohort 4',
                            'Weekend', 'Summer', 'Pitch Contest', 'Webinar', 'Corporate').
    """
    clean = (cohort_or_campaign or "").strip().lower()
    clean_terms = [t for t in clean.split() if len(t) > 2]
    lines = []

    # 1. Match Cohort Schedules
    matched_cohorts = []
    for c in COHORT_SCHEDULES:
        c_name = c["cohort_name"].lower()
        if not clean or (
            clean in c_name or
            c_name in clean or
            any(t in c_name for t in clean_terms) or
            any(t in tr.lower() for tr in c.get("tracks", []) for t in clean_terms)
        ):
            matched_cohorts.append(c)

    if matched_cohorts:
        lines.append("🎓 Official Nextserve Academic Cohort Cycles:")
        for c in matched_cohorts:
            tracks_str = ", ".join(c.get("tracks", []))
            lines.append(
                f"\n📌 {c['cohort_name']} [{c.get('status', 'Scheduled')}]\n"
                f"• Class Kickoff: {c['class_start_date']}\n"
                f"• Enrollment Window: {c['enrollment_window']}\n"
                f"• Orientation: {c.get('orientation_date', 'TBA')}\n"
                f"• Delivery: {c.get('delivery', 'Lagos Hub & Virtual Online')}\n"
                f"• Tracks: {tracks_str}"
            )
            if c.get("milestone"):
                lines.append(f"• Milestone: {c['milestone']}")

    # 2. Match Strategic Campaigns
    matched_campaigns = []
    for cmp in CAMPAIGN_TRACKER_DATA:
        cmp_name = cmp["campaign_name"].lower()
        if not clean or (
            clean in cmp_name or
            cmp_name in clean or
            any(t in cmp_name for t in clean_terms) or
            any(t in cmp["campaign_objective"].lower() for t in clean_terms)
        ):
            matched_campaigns.append(cmp)

    if matched_campaigns:
        if lines:
            lines.append("\n" + "="*50 + "\n")
        lines.append("🚀 Nextserve Strategic Campaigns & Timelines:")
        for cmp in matched_campaigns[:6]:
            budget_str = f"₦{cmp['budget']:,.2f}" if cmp.get("budget") else "Internal"
            lines.append(
                f"\n🌟 {cmp['campaign_name']} ({cmp.get('campaign_type', 'General')}) — [{cmp['status']}]\n"
                f"• Timeline: {cmp['start_date']} to {cmp['end_date']} (Phase: {cmp.get('phase', 'Phase One')})\n"
                f"• Objective: {cmp['campaign_objective']}\n"
                f"• Target Audience: {cmp.get('target_audience', 'Prospective Students')}\n"
                f"• Primary KPI: {cmp.get('primary_kpi', 'Enrollments')} ({cmp.get('kpi_target', 'N/A')})\n"
                f"• Budget: {budget_str} | Manager: {cmp.get('campaign_manager', 'PADIO')}"
            )
            if cmp.get("notes"):
                lines.append(f"• Notes: {cmp['notes']}")

    if not lines:
        return f"No cohort intakes or strategic campaigns found matching '{cohort_or_campaign}'. Nextserve operates on structured bi-monthly cohort intakes (Cohort 2, Weekend Cohort, Cohort 3, Cohort 4)."

    return "\n".join(lines)


@tool
def check_unread_gmail_inquiries() -> str:
    """Check the official Nextserve admissions and support Gmail inbox (chigbookpalaugo@gmail.com)
    for the latest unread student or applicant email inquiries.
    """
    from app.services.gmail_service import gmail_service
    try:
        unread = gmail_service.fetch_latest_unread(mark_as_read=False)
        if not unread:
            return "No unread emails currently found in the Gmail inbox."
        return (
            f"=== Unread Email Received ===\n"
            f"• Message ID: {unread.get('id')}\n"
            f"• From: {unread.get('sender_name')} <{unread.get('sender')}>\n"
            f"• Date: {unread.get('date')}\n"
            f"• Subject: {unread.get('subject')}\n\n"
            f"Body:\n{unread.get('body')}\n"
        )
    except Exception as exc:
        logger.error("Error checking unread Gmail: %s", exc)
        return f"Error checking unread emails: {str(exc)}"


@tool
def draft_and_request_email_approval(
    to_email: str,
    subject: str,
    body: str,
    sender_name: Optional[str] = "Student",
    inquiry_context: Optional[str] = None
) -> str:
    """Create a draft email response and submit it for Level 3 Human-in-the-Loop review
    to the owner on Telegram before dispatch.

    Args:
        to_email: Recipient student's email address.
        subject: Subject line for the response.
        body: The proposed email body text.
        sender_name: Name of the student (optional).
        inquiry_context: Brief summary of the original inquiry (optional).
    """
    from app.services.gmail_service import create_and_store_draft, format_telegram_approval_card
    from app.services.telegram_service import telegram_service

    try:
        token, draft = create_and_store_draft(
            sender=to_email,
            subject=subject,
            body=inquiry_context or "Inquiry from student regarding courses/admissions.",
            sender_name=sender_name or "Student",
            draft_reply=body
        )

        telegram_text, reply_markup = format_telegram_approval_card(
            sender=to_email,
            subject=subject,
            body=inquiry_context or "Student inquiry submitted.",
            draft_body=body,
            token=token,
            sender_name=sender_name or "Student",
            is_simulated=False
        )

        tg_res = telegram_service.send_message(
            text=telegram_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        msg_id = tg_res.get("result", {}).get("message_id", "N/A")
        return (
            f"Draft submitted for Level 3 Human-in-the-Loop approval on Telegram.\n"
            f"• Approval Token: {token}\n"
            f"• Telegram Message ID: {msg_id}\n"
            f"• Status: Pending owner [✅ Approve & Send] or [❌ Reject] decision."
        )
    except Exception as exc:
        logger.error("Error creating approval draft: %s", exc)
        return f"Error creating email approval request: {str(exc)}"
