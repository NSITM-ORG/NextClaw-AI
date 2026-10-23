import hashlib
import math
import os
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import DocumentEmbedding, HAS_PGVECTOR

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 1536


def generate_local_embedding(text: str, dim: int = EMBEDDING_DIMENSION) -> List[float]:
    """
    Generate a deterministic, normalized, dense vector for a given text.
    Acts as a reliable local fallback when external embedding APIs (e.g. OpenAI)
    are unavailable or running in an offline test/development environment.
    """
    vec = [0.0] * dim
    words = text.lower().split()
    if not words:
        words = ["empty"]

    for word in words:
        # Hash word into dimension index
        h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        # Pseudo-random weight based on higher bits
        weight = ((h >> 16) % 1000) / 1000.0 + 0.1
        vec[idx] += weight

    # Normalize vector to unit length for valid cosine similarity
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def get_embedding(text: str) -> List[float]:
    """
    Produce a 1536-dimensional embedding vector for input text.
    Uses OpenAI if OPENAI_API_KEY is configured in the environment,
    otherwise falls back to deterministic local embedding.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import httpx
            response = httpx.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {openai_key}"},
                json={"input": text, "model": "text-embedding-3-small"},
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                return data["data"][0]["embedding"]
            else:
                logger.warning("OpenAI embedding API returned %s: %s", response.status_code, response.text)
        except Exception as exc:
            logger.warning("Error fetching OpenAI embedding: %s. Using local fallback.", exc)

    return generate_local_embedding(text, EMBEDDING_DIMENSION)


def add_document(
    db: Session,
    title: str,
    content: str,
    category: str,
    doc_metadata: Optional[Dict[str, Any]] = None
) -> DocumentEmbedding:
    """
    Embed text content and persist a new DocumentEmbedding record into the database.
    """
    embedding_vector = get_embedding(f"{title}\n{content}")

    doc = DocumentEmbedding(
        title=title,
        content=content,
        category=category,
        doc_metadata=doc_metadata or {},
        embedding=embedding_vector if HAS_PGVECTOR else None
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def search_documents(
    db: Session,
    query: str,
    category: Optional[str] = None,
    top_k: int = 4,
    distance_threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Query DocumentEmbedding using pgvector cosine similarity (<=> operator via cosine_distance).
    Returns matched documents ordered from highest to lowest similarity.
    """
    query_vector = get_embedding(query)

    if HAS_PGVECTOR:
        # Cosine distance operator (<=>): smaller distance means higher cosine similarity
        distance_col = DocumentEmbedding.embedding.cosine_distance(query_vector).label("distance")
        stmt = select(DocumentEmbedding, distance_col)

        if category:
            stmt = stmt.where(DocumentEmbedding.category == category)

        stmt = stmt.order_by(distance_col.asc()).limit(top_k)
        results = db.execute(stmt).all()

        matched = []
        for doc, dist in results:
            dist_val = float(dist) if dist is not None else 1.0
            similarity = max(0.0, 1.0 - dist_val)
            if distance_threshold is not None and dist_val > distance_threshold:
                continue

            matched.append({
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "category": doc.category,
                "metadata": doc.doc_metadata,
                "distance": round(dist_val, 4),
                "similarity": round(similarity, 4),
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            })
        return matched

    # Fallback keyword matching when pgvector is not enabled
    stmt = select(DocumentEmbedding)
    if category:
        stmt = stmt.where(DocumentEmbedding.category == category)
    docs = db.execute(stmt.limit(top_k * 2)).scalars().all()

    query_words = set(query.lower().split())
    ranked = []
    for doc in docs:
        doc_words = set(f"{doc.title} {doc.content}".lower().split())
        overlap = len(query_words.intersection(doc_words))
        ranked.append((overlap, doc))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "category": d.category,
            "metadata": d.doc_metadata,
            "distance": 0.0,
            "similarity": 1.0,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for _, d in ranked[:top_k]
    ]


def seed_initial_school_knowledge(db: Session) -> int:
    """
    Seed initial university catalog, course syllabi, and administrative policies
    into document_embeddings if table is empty.
    """
    existing_count = db.query(DocumentEmbedding).count()
    if existing_count > 0:
        return existing_count

    knowledge_items = [
        {
            "title": "CS101: Introduction to Computer Science",
            "category": "course",
            "content": (
                "CS101 covers foundational programming concepts in Python, algorithms, data structures, "
                "and computational thinking. Prerequisites: High school algebra. Offered: Fall & Spring. "
                "Credits: 4. Instructor: Dr. Alice Johnson. Grading: 40% Assignments, 30% Midterm, 30% Final Project."
            ),
            "metadata": {"course_code": "CS101", "department": "Computer Science", "credits": 4}
        },
        {
            "title": "CS201: Data Structures and Algorithms",
            "category": "course",
            "content": (
                "CS201 focuses on trees, graphs, heaps, dynamic programming, sorting algorithms, and complexity analysis. "
                "Prerequisites: CS101 with a grade of C or higher. Offered: Spring semester. "
                "Credits: 4. Corequisite: Discrete Mathematics (MATH210)."
            ),
            "metadata": {"course_code": "CS201", "department": "Computer Science", "credits": 4}
        },
        {
            "title": "Academic Integrity and Honor Code Policy",
            "category": "policy",
            "content": (
                "Academic integrity is strictly enforced. Plagiarism, unauthorized collaboration, using generative AI "
                "without explicit instructor consent on exams, and cheating will result in an immediate zero on the assignment "
                "and disciplinary review with the Academic Board."
            ),
            "metadata": {"policy_id": "POL-2024-01", "effective_date": "2024-09-01", "office": "Dean of Students"}
        },
        {
            "title": "Late Submission and Grading Policy",
            "category": "policy",
            "content": (
                "Standard policy permits assignment submissions up to 48 hours late with a 10% penalty per 24-hour period. "
                "Submissions beyond 48 hours will receive a grade of zero unless an approved extenuating medical circumstances waiver is filed."
            ),
            "metadata": {"policy_id": "POL-2024-02", "effective_date": "2024-09-01", "office": "Academic Affairs"}
        },
        {
            "title": "Course Drop, Withdrawal, and Refund Policy",
            "category": "policy",
            "content": (
                "Students may drop courses without academic record during the first 2 weeks of the semester with 100% tuition refund. "
                "Withdrawals between weeks 3-7 receive a 'W' grade with a 50% refund. No withdrawals permitted after week 8."
            ),
            "metadata": {"policy_id": "POL-2024-03", "effective_date": "2024-09-01", "office": "Registrar & Bursar"}
        },
        {
            "title": "Campus Student Handbook & Academic Calendar 2024-2025",
            "category": "school_doc",
            "content": (
                "Fall Semester begins September 2, 2024. Midterm examination week: October 21-25, 2024. "
                "Final examination period: December 9-16, 2024. Spring semester starts January 13, 2025. "
                "Campus health center, library hours, student organization registration, and housing procedures are detailed in section 3."
            ),
            "metadata": {"doc_id": "DOC-2024-HB", "version": "1.0", "office": "Student Affairs"}
        }
    ]

    for item in knowledge_items:
        add_document(
            db=db,
            title=item["title"],
            content=item["content"],
            category=item["category"],
            doc_metadata=item["metadata"]
        )

    return len(knowledge_items)
