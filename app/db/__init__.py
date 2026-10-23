"""Database package initialization."""
from app.db.session import engine, SessionLocal, Base, get_db
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
from app.db.memory import (
    postgres_memory_manager,
    get_postgres_checkpointer,
)
from app.db.vector_store import (
    get_embedding,
    add_document,
    search_documents,
    seed_initial_school_knowledge,
)

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "User",
    "UserRole",
    "ApprovalRequest",
    "ApprovalStatus",
    "AuditLog",
    "Task",
    "DocumentEmbedding",
    "postgres_memory_manager",
    "get_postgres_checkpointer",
    "get_embedding",
    "add_document",
    "search_documents",
    "seed_initial_school_knowledge",
]
