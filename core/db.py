"""NextClaw OS - Database & Connection Manager (core/db.py).

Provides PostgreSQL + pgvector session management with seamless
sandbox SQLite fallback for localized testing and zero-downtime operation.
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Numeric
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timezone

logger = logging.getLogger("nextclaw.db")

# Detect pgvector availability
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

Base = declarative_base()

# Models
class Course(Base):
    __tablename__ = "nextclaw_courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, index=True, nullable=False)
    course_name = Column(String(255), nullable=False)
    department = Column(String(100), default="Tech Development")
    credits = Column(Integer, default=4)
    description = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    tuition = Column(Numeric(10, 2), nullable=True)
    instalment_tuition = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SchoolKnowledgeVector(Base):
    __tablename__ = "nextclaw_knowledge_vectors"
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False)
    reference_id = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    text_content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
    if HAS_PGVECTOR:
        embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ApprovalTicket(Base):
    __tablename__ = "nextclaw_approval_tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(100), unique=True, index=True, nullable=False)
    action_name = Column(String(150), nullable=False)
    target = Column(String(255), nullable=False)
    tier = Column(Integer, default=3, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected
    details = Column(JSON, nullable=True)
    requested_by = Column(String(100), default="NextClaw OS")
    reviewer = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)


class NextClawAuditLog(Base):
    __tablename__ = "nextclaw_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String(50), nullable=False)
    user_id = Column(String(100), nullable=True)
    tool_invoked = Column(String(100), nullable=False)
    tier = Column(Integer, default=1)
    status = Column(String(50), default="success")
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Database Engine Initialization
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nextserve")

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine

    try:
        # Attempt PostgreSQL connection
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            pass
        _engine = engine
        logger.info(f"Connected to PostgreSQL database: {DATABASE_URL.split('@')[-1]}")
    except Exception as exc:
        # Fallback to local SQLite sandbox
        sqlite_url = "sqlite:///./nextclaw_sandbox.db"
        logger.warning(f"PostgreSQL connection unavailable ({exc}). Using sandbox database: {sqlite_url}")
        _engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

    # Create tables
    Base.metadata.create_all(bind=_engine)
    return _engine


def get_db_session() -> Session:
    """Returns a new database session."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()
