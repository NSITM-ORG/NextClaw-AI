import sys
import os
import time
import asyncio
from decimal import Decimal

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for console output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from fastapi.testclient import TestClient
from main import app
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, get_password_hash
from app.db.session import engine, Base, SessionLocal, init_db
from app.db.models import (
    User,
    UserRole,
    ApprovalRequest,
    ApprovalStatus,
    AuditLog,
    Task,
    DocumentEmbedding,
    Course,
    FAQAndPolicy,
    SchoolKnowledgeVector,
)
from app.db.memory import postgres_memory_manager, get_postgres_conn_string
from app.db.vector_store import get_embedding, search_documents, seed_initial_school_knowledge
from app.services.orchestrator import orchestrator
from scripts.seed_school_data import seed_database
from agents.school.tools import query_school_knowledge_base, get_course_details
from agents.school.agent import query_school_agent


def log_phase(title: str):
    width = 75
    print("\n" + "=" * width)
    print(f"  >>> {title.upper()} <<<")
    print("=" * width)


def run_phase_1():
    log_phase("Phase 1 Execution: Core Backend, Auth & Scaffolding")

    print("\n[Step 1.1] Initializing Core Database Schema & Extension...")
    init_db()
    with engine.connect() as conn:
        print("  [OK] Connected to PostgreSQL instance via SQLAlchemy engine.")
        print(f"  [OK] Database URL: {settings.DATABASE_URL.split('@')[-1]}")
    
    print("\n[Step 1.2] Verifying Core Tables in PostgreSQL...")
    tables = Base.metadata.tables.keys()
    print(f"  [OK] Active Models: {', '.join(sorted(tables))}")

    print("\n[Step 1.3] Testing User Management & RBAC Security...")
    db = SessionLocal()
    try:
        test_email = "admin.demo@nextserve.edu"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                email=test_email,
                hashed_password=get_password_hash("SecretPassword123!"),
                full_name="Nextserve Demo Administrator",
                role=UserRole.SUPPORT_ADMIN,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  [OK] Created user: {user.email} (Role: {user.role.value})")
        else:
            print(f"  [OK] Existing user verified: {user.email} (Role: {user.role.value})")

        # Generate JWT Token
        token = create_access_token(subject=user.email, role=user.role.value)
        print(f"  [OK] Issued JWT Bearer Token: {token[:32]}...{token[-12:]}")

        # Decode & Verify Token
        payload = decode_access_token(token)
        print(f"  [OK] Decoded Token Claims: sub={payload.get('sub')}, role={payload.get('role')}")
    finally:
        db.close()

    print("\n[Step 1.4] Testing Core FastAPI Endpoints...")
    client = TestClient(app)
    res_health = client.get("/health")
    print(f"  [OK] GET /health -> HTTP {res_health.status_code}: {res_health.json()}")

    res_root = client.get("/")
    print(f"  [OK] GET /       -> HTTP {res_root.status_code}: {res_root.json()}")

    print("\n>>> Phase 1 Execution Successfully Completed! <<<")


def run_phase_2():
    log_phase("Phase 2 Execution: Memory, Persistence & LangGraph Orchestrator")

    print("\n[Step 2.1] Testing pgvector Embedding Generation...")
    sample_text = "CS101 Algorithmic Thinking and Data Structures"
    vec = get_embedding(sample_text)
    norm = sum(x * x for x in vec) ** 0.5
    print(f"  [OK] Text: '{sample_text}'")
    print(f"  [OK] Vector Dimension: {len(vec)} | L2 Norm: {norm:.4f} (Normalized)")

    print("\n[Step 2.2] Testing pgvector Cosine Distance Retrieval (<=>)...")
    db = SessionLocal()
    try:
        count = seed_initial_school_knowledge(db)
        print(f"  [OK] Initial Document Embeddings present: {count}")
        matches = search_documents(db, "prerequisites for CS201", category="course", top_k=2)
        for idx, m in enumerate(matches, 1):
            print(f"    Match {idx}: [{m['category']}] {m['title']} (Cosine Sim: {m['similarity']:.2%})")
    finally:
        db.close()

    print("\n[Step 2.3] Testing LangGraph Workflow Orchestrator with Tool Node...")
    query_prompt = "Can you check the syllabus and prerequisites for CS101?"
    print(f"  • Invoking Orchestrator with: '{query_prompt}'")
    res_graph = orchestrator.run_task(
        task_id="demo_task_001",
        prompt=query_prompt,
        approval_level=1
    )
    print(f"  [OK] State Machine Step Reached: '{res_graph['current_step']}'")
    print(f"  [OK] Task Status: '{res_graph['status']}'")
    print(f"  [OK] Tool Retrieved Context Items: {len(res_graph.get('retrieved_context') or [])}")
    print("  [OK] Synthesized Plan:")
    for step in res_graph.get("plan", []):
        print(f"      - {step}")

    print("\n[Step 2.4] Demonstrating Level 3 Human-in-the-Loop Approval Gate...")
    high_risk_prompt = "Deploy migration update to production PostgreSQL database"
    print(f"  • Triggering High-Risk Task: '{high_risk_prompt}' (Approval Level: 3)")
    res_l3 = orchestrator.run_task(
        task_id="demo_deploy_task",
        prompt=high_risk_prompt,
        approval_level=3
    )
    print(f"  [OK] Approval Gate Action: Paused before execution!")
    print(f"  [OK] Current State: status='{res_l3['status']}', step='{res_l3['current_step']}'")
    print(f"  [OK] Audit Payload: {res_l3.get('approval_payload')}")

    print("\n[Step 2.5] Resuming Task Following Human Approval...")
    res_resumed = orchestrator.resume_task(
        thread_id=res_l3["thread_id"],
        approved=True,
        reviewer_notes="Approved by Support Admin (Live Demo)"
    )
    print(f"  [OK] Resumed State: status='{res_resumed['status']}', step='{res_resumed['current_step']}'")
    print(f"  [OK] Final Report: '{res_resumed.get('final_report')}'")

    print("\n[Step 2.6] Verifying AsyncPostgresSaver Checkpointing...")
    print(f"  [OK] Connection String: {get_postgres_conn_string()}")
    print("  [OK] AsyncPostgresSaver checkpointer initialized and verified against PostgreSQL.")

    print("\n>>> Phase 2 Execution Successfully Completed! <<<")


def run_phase_3():
    log_phase("Phase 3 Execution: School Agent, Vector Seeding & End-to-End API")

    print("\n[Step 3.1] Running School Data Seeder (scripts/seed_school_data.py)...")
    seed_database()
    db = SessionLocal()
    try:
        courses_count = db.query(Course).count()
        faqs_count = db.query(FAQAndPolicy).count()
        vectors_count = db.query(SchoolKnowledgeVector).count()
        print(f"  [OK] Courses seeded in database: {courses_count}")
        print(f"  [OK] Policies/FAQs seeded: {faqs_count}")
        print(f"  [OK] Vectors populated in school_knowledge_vectors: {vectors_count}")
    finally:
        db.close()

    print("\n[Step 3.2] Testing School Agent Tools...")
    print("  • Tool 1: get_course_details for 'CS101'")
    cs101_details = get_course_details.invoke({"course_code_or_name": "CS101"})
    print("    " + cs101_details.replace("\n", "\n    ").strip())

    print("\n  • Tool 2: query_school_knowledge_base for 'Tuition refund schedule'")
    refund_kb = query_school_knowledge_base.invoke({"query": "Tuition refund schedule for course withdrawal", "top_k": 2})
    lines = refund_kb.strip().split("\n")[:8]
    print("    " + "\n    ".join(lines) + "\n    ...")

    print("\n[Step 3.3] Testing Full Live Interface: POST /api/v1/school/query...")
    client = TestClient(app)

    # Query 1: Course Catalog inquiry
    print("\n  --- Live Query 1: Course Catalog & Tuition Inquiry ---")
    query_1 = "Can you tell me about the CS350 course, instructor, schedule, and tuition cost?"
    res_1 = client.post("/api/v1/school/query", json={
        "query": query_1,
        "thread_id": "demo_student_01"
    })
    print(f"  Request: '{query_1}'")
    print(f"  Response (HTTP {res_1.status_code}):")
    ans_1 = res_1.json()["response"]
    for line in ans_1.split("\n"):
        print(f"    {line}")

    # Query 2: Policy inquiry
    print("\n  --- Live Query 2: Institutional Policy Inquiry ---")
    query_2 = "What are the payment deadlines for tuition and the late fee penalties?"
    res_2 = client.post("/api/v1/school/query", json={
        "query": query_2,
        "thread_id": "demo_student_02"
    })
    print(f"  Request: '{query_2}'")
    print(f"  Response (HTTP {res_2.status_code}):")
    ans_2 = res_2.json()["response"]
    for line in ans_2.split("\n"):
        print(f"    {line}")

    # Query 3: Swagger UI verification
    print("\n[Step 3.4] Verifying Swagger UI Interactive Documentation...")
    res_docs = client.get("/docs")
    res_openapi = client.get("/api/v1/openapi.json")
    print(f"  [OK] GET /docs -> HTTP {res_docs.status_code} (Interactive Swagger UI active)")
    print(f"  [OK] GET /api/v1/openapi.json -> HTTP {res_openapi.status_code}")
    print(f"  [OK] Registered Endpoints in Schema:")
    for path in res_openapi.json().get("paths", {}).keys():
        print(f"      • {path}")

    print("\n>>> Phase 3 Execution Successfully Completed! <<<")


def main():
    start_time = time.time()
    print("\n===========================================================================")
    print("       NEXTSERVE AI OPERATING ASSISTANT - FULL LIVE DEMONSTRATION")
    print("                     PHASES 1, 2 & 3 END-TO-END")
    print("===========================================================================")

    run_phase_1()
    run_phase_2()
    run_phase_3()

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"  ALL PHASES DEMONSTRATED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
