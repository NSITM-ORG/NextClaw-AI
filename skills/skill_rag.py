"""NextClaw OS - RAG Knowledge Base Skill (skill_rag.py).

Queries PostgreSQL + pgvector for accurate course, fee, syllabus,
and FAQ answers with automatic in-memory fallback to MEMORY.md.
Execution Tier: TIER 1 (Safe / Read-Only).
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from skills import BaseSkill

logger = logging.getLogger("nextclaw.skills.rag")

# Path to MEMORY.md for authoritative school fallback
MEMORY_FILE = Path(__file__).resolve().parent.parent / "configs" / "MEMORY.md"



class RAGSkill(BaseSkill):
    """Tier 1 RAG Skill querying course catalogs, fees, syllabus, and FAQs."""

    name: str = "skill_rag"
    tier: int = 1
    description: str = "PostgreSQL + pgvector semantic retrieval and school catalog search."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._memory_cache: Dict[str, Any] = {}
        self._load_memory_cache()

    def _load_memory_cache(self):
        """Loads and parses verified courses and policies from MEMORY.md into memory."""
        if not MEMORY_FILE.exists():
            return

        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            self._raw_memory = content
            # Parse courses from markdown
            self._courses: List[Dict[str, Any]] = []
            
            # Extract course blocks
            course_blocks = re.findall(
                r"\d+\.\s+\*\*(.+?)\s+\(`([A-Z0-9\-]+)`\)\*\*\n\s+\*\s+\*\*Curriculum:\*\*\s*(.+?)\n\s+\*\s+\*\*Tuition \(One-Off\):\*\*\s*₦([0-9,]+)\n\s+\*\s+\*\*Tuition \(Instalment\):\*\*\s*₦([0-9,]+)\s*(?:\((.+?)\))?",
                content
            )
            for title, code, curriculum, one_off_str, inst_str, breakdown in course_blocks:
                one_off = float(one_off_str.replace(",", ""))
                inst = float(inst_str.replace(",", ""))
                self._courses.append({
                    "course_code": code,
                    "name": title.strip(),
                    "curriculum": curriculum.strip(),
                    "tuition_one_off": one_off,
                    "tuition_instalment": inst,
                    "breakdown": breakdown.strip() if breakdown else f"Tranche 1: ₦{inst*0.4:,.0f} | Tranche 2: ₦{inst*0.3:,.0f} | Tranche 3: ₦{inst*0.3:,.0f}"
                })

            logger.info(f"Loaded {len(self._courses)} courses from MEMORY.md into RAG memory cache.")
        except Exception as err:
            logger.warning(f"Could not load courses from MEMORY.md: {err}")

    def execute(self, action: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes RAG search action."""
        if action == "query" or action == "search":
            query_text = params.get("query", "")
            top_k = int(params.get("top_k", 4))
            return self.query_knowledge_base(query=query_text, top_k=top_k)

        elif action == "get_course" or action == "course_details":
            course_ref = params.get("course_code") or params.get("name") or params.get("query", "")
            return self.get_course_details(course_ref)

        elif action == "calculate_instalments" or action == "instalments":
            course_ref = params.get("course_code") or params.get("name", "")
            return self.calculate_instalments(course_ref)

        elif action == "list_courses":
            return {"status": "success", "total": len(self._courses), "courses": self._courses}

        else:
            return {
                "status": "error",
                "message": f"Unknown RAG action '{action}'. Valid actions: query, get_course, calculate_instalments, list_courses"
            }

    def query_knowledge_base(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Queries vector database with keyword fallback over MEMORY.md."""
        results = []

        # 1. Try PostgreSQL + pgvector query if DB is available
        try:
            from core.db import get_db_session, SchoolKnowledgeVector, HAS_PGVECTOR
            from app.db.vector_store import get_embedding
            from sqlalchemy import select

            db = get_db_session()
            if HAS_PGVECTOR:
                query_vec = get_embedding(query)
                dist_col = SchoolKnowledgeVector.embedding.cosine_distance(query_vec).label("distance")
                stmt = select(SchoolKnowledgeVector, dist_col).order_by(dist_col.asc()).limit(top_k)
                rows = db.execute(stmt).all()
                for doc, dist in rows:
                    results.append({
                        "title": doc.title,
                        "type": doc.content_type,
                        "snippet": doc.text_content,
                        "score": round(1.0 - float(dist or 0.0), 3)
                    })
            db.close()
        except Exception as exc:
            logger.debug(f"PostgreSQL pgvector query bypassed: {exc}")

        # 2. If vector search yielded results, return them
        if results:
            return {"status": "success", "source": "pgvector", "query": query, "results": results}

        # 3. Fallback: Semantic/Keyword match over MEMORY.md
        query_words = set(re.findall(r"\w+", query.lower()))
        matched_courses = []

        for c in self._courses:
            text = f"{c['course_code']} {c['name']} {c['curriculum']}".lower()
            score = sum(1 for w in query_words if w in text)
            if score > 0:
                matched_courses.append((score, c))

        matched_courses.sort(key=lambda x: x[0], reverse=True)

        for score, c in matched_courses[:top_k]:
            results.append({
                "title": f"{c['name']} ({c['course_code']})",
                "type": "course",
                "snippet": f"Curriculum: {c['curriculum']}. Tuition One-Off: ₦{c['tuition_one_off']:,.0f}. Instalment Total: ₦{c['tuition_instalment']:,.0f} ({c['breakdown']}).",
                "score": round(score / max(len(query_words), 1), 2)
            })

        # Check policy keywords (refund, deferral, attendance, certificate, instalment)
        if any(w in query.lower() for w in ["refund", "money back", "cancel"]):
            results.append({
                "title": "Nextserve Refund Policy",
                "type": "policy",
                "snippet": "Refund Policy: Before Day 1 of classes: 80% tuition refundable upon written request (20% retained + ₦10,000 registration fee non-refundable). After Day 1 of classes: 0% refund. No exceptions.",
                "score": 1.0
            })
        if any(w in query.lower() for w in ["defer", "postpone", "next cohort"]):
            results.append({
                "title": "Nextserve Deferral Policy",
                "type": "policy",
                "snippet": "Deferral Policy: A student may request to defer admission to the subsequent cohort once. Request must be submitted at least 7 days prior to cohort commencement. Subject to Tier 3 Admin approval.",
                "score": 1.0
            })
        if any(w in query.lower() for w in ["attendance", "graduate", "certificate"]):
            results.append({
                "title": "Nextserve Graduation & Attendance Policy",
                "type": "policy",
                "snippet": "Graduation Policy: Minimum 80% attendance in lectures and practical labs is mandatory to qualify for the certificate of completion and capstone defense.",
                "score": 1.0
            })
        if any(w in query.lower() for w in ["instalment", "installment", "part payment", "pay small"]):
            results.append({
                "title": "Nextserve Instalment Policy",
                "type": "policy",
                "snippet": "Instalment Policy: Standard 3-tranche structure: 40% at enrollment, 30% at Day 30, 30% at Day 60. A non-refundable ₦10,000 application fee applies.",
                "score": 1.0
            })

        return {
            "status": "success",
            "source": "memory_blueprint",
            "query": query,
            "results": results or [{
                "title": "General Nextserve Information",
                "type": "general",
                "snippet": "Nextserve offers 26 accredited practical programmes in Tech Development, Management, and Short-Term Masterclasses. Contact WhatsApp +2348093344991 for personalized admissions counseling.",
                "score": 0.5
            }]
        }

    def get_course_details(self, course_ref: str) -> Dict[str, Any]:
        """Look up exact course by code or partial name."""
        ref = course_ref.strip().lower()
        for c in self._courses:
            if c["course_code"].lower() == ref or ref in c["name"].lower() or c["course_code"].lower() in ref:
                return {
                    "status": "success",
                    "course": c,
                    "tuition_formatted": f"₦{c['tuition_one_off']:,.2f}",
                    "instalment_total_formatted": f"₦{c['tuition_instalment']:,.2f}",
                    "breakdown": c["breakdown"]
                }

        return {
            "status": "not_found",
            "message": f"Course matching '{course_ref}' was not found in the Nextserve catalog."
        }

    def calculate_instalments(self, course_ref: str) -> Dict[str, Any]:
        """Calculates 40% / 30% / 30% payment breakdown."""
        details = self.get_course_details(course_ref)
        if details.get("status") != "success":
            return details

        c = details["course"]
        total_inst = c["tuition_instalment"]
        tranche_1 = round(total_inst * 0.40, 2)
        tranche_2 = round(total_inst * 0.30, 2)
        tranche_3 = round(total_inst * 0.30, 2)

        return {
            "status": "success",
            "course_name": c["name"],
            "course_code": c["course_code"],
            "one_off_discounted_tuition": f"₦{c['tuition_one_off']:,.2f}",
            "instalment_total": f"₦{total_inst:,.2f}",
            "schedule": [
                {"tranche": 1, "percentage": "40%", "due": "At Enrollment", "amount": f"₦{tranche_1:,.2f}"},
                {"tranche": 2, "percentage": "30%", "due": "Day 30", "amount": f"₦{tranche_2:,.2f}"},
                {"tranche": 3, "percentage": "30%", "due": "Day 60", "amount": f"₦{tranche_3:,.2f}"},
            ],
            "registration_fee": "₦10,000 (Non-refundable application fee)"
        }
