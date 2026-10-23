import sys
import os
import logging
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, init_db
from app.db.models import Course, FAQAndPolicy, SchoolKnowledgeVector, HAS_PGVECTOR
from app.db.vector_store import get_embedding
from app.knowledge.nsitm_knowledge import (
    INSTITUTION_INFO,
    PROGRAMMES_DATA,
    PAYMENT_INSTALMENT_RULES,
    ACADEMIC_POLICIES,
    ENROLLMENT_WORKFLOW,
    FREQUENT_QUESTIONS,
    MARKETING_CALENDAR_DATA,
    CAMPAIGN_TRACKER_DATA,
    COHORT_SCHEDULES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_school_data")


def seed_courses(db):
    """Seed or update all 26 real NSITM programmes."""
    logger.info("Seeding NSITM Programmes into 'courses' table...")
    count = 0
    for p in PROGRAMMES_DATA:
        existing = db.query(Course).filter(Course.course_code == p["course_code"]).first()
        skills_str = ", ".join(p.get("skills", []))
        careers_str = ", ".join(p.get("careers", []))
        desc = f"{p['summary']} Skills: {skills_str}. Target Careers: {careers_str}."

        if existing:
            existing.course_name = p["name"]
            existing.department = p["category_label"]
            existing.credits = p.get("credits", 3)
            existing.description = desc
            existing.prerequisites = "Open to all backgrounds. Basic computer literacy recommended."
            existing.instructor = "NSITM Senior Industry Practitioner"
            existing.schedule = p.get("schedule", "Online Virtual Cohorts or Lagos Campus Hub")
            existing.tuition = p["tuition"]
        else:
            course = Course(
                course_code=p["course_code"],
                course_name=p["name"],
                department=p["category_label"],
                credits=p.get("credits", 3),
                description=desc,
                prerequisites="Open to all backgrounds. Basic computer literacy recommended.",
                instructor="NSITM Senior Industry Practitioner",
                schedule=p.get("schedule", "Online Virtual Cohorts or Lagos Campus Hub"),
                tuition=p["tuition"],
            )
            db.add(course)
        count += 1
    db.commit()
    logger.info("Successfully seeded %d NSITM programmes.", count)


def seed_faqs_and_policies(db):
    """Seed NSITM administrative policies, payment rules, and admissions FAQs."""
    logger.info("Seeding FAQs and Policies into 'faqs_and_policies' table...")

    records = []

    # Academic Policies
    for key, item in ACADEMIC_POLICIES.items():
        records.append({
            "category": "academic_policy",
            "question_or_topic": item["rule"],
            "answer_or_policy": item.get("description", "") + " " + item.get("prior_cancellation", "") + " " + item.get("deferral", "")
        })

    # Payment Rules
    records.append({
        "category": "tuition_and_payments",
        "question_or_topic": "Tuition Payment & 3-Part Instalment Plan",
        "answer_or_policy": (
            f"Method: {PAYMENT_INSTALMENT_RULES['method']}. Bank: {PAYMENT_INSTALMENT_RULES['bank_details']['bank']}. "
            f"Formula: {PAYMENT_INSTALMENT_RULES['instalment_plan']['split_formula']}. "
            f"Confirmation window: {PAYMENT_INSTALMENT_RULES['confirmation_time']}. "
            f"Student portal: {PAYMENT_INSTALMENT_RULES['portal_link']} - {PAYMENT_INSTALMENT_RULES['portal_description']}"
        )
    })

    # Enrollment Workflow
    steps_desc = " ".join([f"Step {s['step']}: {s['name']} - {s['details']}" for s in ENROLLMENT_WORKFLOW["steps"]])
    records.append({
        "category": "admissions",
        "question_or_topic": "Guided 4-Step Enrollment Workflow",
        "answer_or_policy": f"{steps_desc} Abandonment protection: {ENROLLMENT_WORKFLOW['abandonment_protection']}"
    })

    # Frequently Asked Questions
    for faq in FREQUENT_QUESTIONS:
        records.append({
            "category": "faq",
            "question_or_topic": faq["q"],
            "answer_or_policy": faq["a"]
        })

    # Institutional History
    records.append({
        "category": "institution_history",
        "question_or_topic": "About Nextserve (NSITM) & Leadership",
        "answer_or_policy": (
            f"{INSTITUTION_INFO['name']} established {INSTITUTION_INFO['established_year']} ({INSTITUTION_INFO['years_of_experience']} years). "
            f"Leadership: {INSTITUTION_INFO['founder']['title']}, {INSTITUTION_INFO['founder']['education']}. "
            f"Background: {INSTITUTION_INFO['founder']['background']}. "
            f"Stats: {INSTITUTION_INFO['stats']['graduates']} graduates, {INSTITUTION_INFO['stats']['instructors']} instructors. "
            f"Campus: {INSTITUTION_INFO['contacts']['address']}. WhatsApp: {INSTITUTION_INFO['contacts']['whatsapp_number']}."
        )
    })

    # Academic Cohorts & Intake Cycles
    cohort_lines = []
    for c in COHORT_SCHEDULES:
        cohort_lines.append(f"{c['cohort_name']}: Kickoff {c['class_start_date']} (Enrollment {c['enrollment_window']}). Tracks: {', '.join(c['tracks'])}.")
    records.append({
        "category": "academic_calendar",
        "question_or_topic": "Academic Cohort Cycles & Start Dates",
        "answer_or_policy": "Nextserve official cohort schedule: " + " ".join(cohort_lines)
    })

    # Strategic Campaigns & Pitch Contest
    for cmp in CAMPAIGN_TRACKER_DATA:
        budget_str = f" Budget: ₦{cmp['budget']:,.2f}." if cmp.get("budget") else ""
        records.append({
            "category": "campaign_schedule",
            "question_or_topic": f"Campaign: {cmp['campaign_name']}",
            "answer_or_policy": f"{cmp['campaign_name']} ({cmp['status']}). Timeline: {cmp['start_date']} to {cmp['end_date']}. Objective: {cmp['campaign_objective']}. Target Audience: {cmp['target_audience']}. Primary KPI: {cmp['primary_kpi']} ({cmp['kpi_target']}).{budget_str} Manager: {cmp['campaign_manager']}."
        })

    # Marketing Content Calendar
    records.append({
        "category": "marketing_calendar",
        "question_or_topic": "Nextserve Video Series & Content Calendar",
        "answer_or_policy": (
            "Nextserve publishes multi-series educational video episodes across Dev Engineering (Ep 1-5), UI/UX (Ep 1-5), "
            "Virtual Assistance (Ep 1-5), Tobi Student Journey (Ep 1-5), Foundation Tracks (Before Nextserve Ep 1-5), "
            "The Other Voice (Ep 1-4), and The Build Log (Ep 1-5) across Facebook, Instagram, LinkedIn, and Twitter/X."
        )
    })

    count = 0
    for r in records:
        existing = db.query(FAQAndPolicy).filter(FAQAndPolicy.question_or_topic == r["question_or_topic"]).first()
        if existing:
            existing.category = r["category"]
            existing.answer_or_policy = r["answer_or_policy"]
        else:
            db.add(FAQAndPolicy(**r))
        count += 1
    db.commit()
    logger.info("Successfully seeded %d FAQs, Policies, and Campaign records.", count)


def seed_vector_embeddings(db):
    """Generate dense embeddings and store in 'school_knowledge_vectors'."""
    logger.info("Generating dense embeddings for semantic search...")
    # Clear existing vectors to ensure fresh, authentic data
    try:
        db.query(SchoolKnowledgeVector).delete()
        db.commit()
    except Exception:
        db.rollback()

    vectors_count = 0

    # 1. Embed Programmes
    for p in PROGRAMMES_DATA:
        skills = ", ".join(p.get("skills", []))
        careers = ", ".join(p.get("careers", []))
        instalment_txt = f" Instalment fee: ₦{p['instalment_fee']:,.2f}." if p.get("instalment_fee") else " Full upfront payment only."
        text = (
            f"Programme: {p['name']} ({p['course_code']}). "
            f"Category: {p['category_label']}. Duration: {p['duration']}. "
            f"Tuition: ₦{p['tuition']:,.2f}.{instalment_txt} "
            f"Skills covered: {skills}. Career outcomes: {careers}. "
            f"Description: {p['summary']}"
        )
        vec = get_embedding(text)
        skv = SchoolKnowledgeVector(
            content_type="course",
            reference_id=p["course_code"],
            title=f"{p['name']} ({p['course_code']})",
            text_content=text,
            metadata_={
                "slug": p["slug"],
                "category": p["category"],
                "tuition": str(p["tuition"]),
                "duration": p["duration"],
            }
        )
        if HAS_PGVECTOR:
            skv.embedding = vec
        db.add(skv)
        vectors_count += 1

    # 2. Embed Policies & FAQs
    faqs_and_policies = db.query(FAQAndPolicy).all()
    for fp in faqs_and_policies:
        text = f"Topic: {fp.question_or_topic}\nContent: {fp.answer_or_policy}"
        vec = get_embedding(text)
        skv = SchoolKnowledgeVector(
            content_type="policy" if "policy" in fp.category else "faq",
            reference_id=str(fp.id),
            title=fp.question_or_topic,
            text_content=text,
            metadata_={"category": fp.category}
        )
        if HAS_PGVECTOR:
            skv.embedding = vec
        db.add(skv)
        vectors_count += 1

    # 3. Embed Academic Cohort Schedules
    for c in COHORT_SCHEDULES:
        tracks_txt = ", ".join(c.get("tracks", []))
        milestone_txt = f" Milestone: {c['milestone']}." if c.get("milestone") else ""
        text = (
            f"Academic Cohort: {c['cohort_name']} ({c['status']}). "
            f"Class Kickoff: {c['class_start_date']}. "
            f"Enrollment Window: {c['enrollment_window']}. "
            f"Orientation Date: {c.get('orientation_date', 'TBA')}. "
            f"Delivery Format: {c.get('delivery', 'Lagos Hub & Virtual Online')}. "
            f"Programmes & Tracks: {tracks_txt}.{milestone_txt}"
        )
        vec = get_embedding(text)
        skv = SchoolKnowledgeVector(
            content_type="calendar",
            reference_id=f"cohort-{c['cohort_name'].lower().replace(' ', '-')}",
            title=f"Cohort Schedule: {c['cohort_name']}",
            text_content=text,
            metadata_={"cohort_name": c["cohort_name"], "status": c["status"]}
        )
        if HAS_PGVECTOR:
            skv.embedding = vec
        db.add(skv)
        vectors_count += 1

    # 4. Embed Strategic Campaigns
    for cmp in CAMPAIGN_TRACKER_DATA:
        budget_str = f" Budget: ₦{cmp['budget']:,.2f}." if cmp.get("budget") else ""
        text = (
            f"Campaign: {cmp['campaign_name']} ({cmp.get('campaign_type', 'General')}) [{cmp['status']}]. "
            f"Active Timeline: {cmp['start_date']} to {cmp['end_date']} (Phase: {cmp.get('phase', 'Phase One')}). "
            f"Objective: {cmp['campaign_objective']} "
            f"Target Audience: {cmp.get('target_audience', 'Prospective Students')}. "
            f"Primary KPI: {cmp.get('primary_kpi', 'Enrollments')} ({cmp.get('kpi_target', 'N/A')}).{budget_str} "
            f"Manager: {cmp.get('campaign_manager', 'PADIO')}."
        )
        vec = get_embedding(text)
        skv = SchoolKnowledgeVector(
            content_type="campaign",
            reference_id=f"cmp-{cmp['campaign_name'].lower().replace(' ', '-')}",
            title=f"Campaign: {cmp['campaign_name']}",
            text_content=text,
            metadata_={"campaign_name": cmp["campaign_name"], "status": cmp["status"]}
        )
        if HAS_PGVECTOR:
            skv.embedding = vec
        db.add(skv)
        vectors_count += 1

    db.commit()
    logger.info("Successfully generated and stored %d knowledge vectors.", vectors_count)


def main():
    logger.info("=== Starting NSITM School Data Ingestion ===")
    try:
        init_db()
    except Exception as exc:
        logger.warning("init_db note: %s", exc)

    db = SessionLocal()
    try:
        seed_courses(db)
        seed_faqs_and_policies(db)
        seed_vector_embeddings(db)
        logger.info("=== NSITM Data Ingestion Completed Successfully! ===")
    except Exception as exc:
        logger.error("Failed during seed_school_data: %s", exc)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
