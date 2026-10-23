import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Enum,
    Numeric
)
from sqlalchemy.orm import relationship
from app.db.session import Base

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False


class UserRole(str, enum.Enum):
    SUPPORT_ADMIN = "Support Admin"
    INSTRUCTOR = "Instructor"
    DEVELOPER = "Developer"
    OWNER = "Owner"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(
        Enum(UserRole, name="user_role_enum", native_enum=False),
        default=UserRole.DEVELOPER,
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    approval_requests = relationship(
        "ApprovalRequest",
        foreign_keys="[ApprovalRequest.requested_by]",
        back_populates="requester"
    )
    reviewed_approvals = relationship(
        "ApprovalRequest",
        foreign_keys="[ApprovalRequest.reviewed_by]",
        back_populates="reviewer"
    )
    audit_logs = relationship("AuditLog", back_populates="user")


class ApprovalRequest(Base):
    """
    Level 3 Human-in-the-Loop approval gates table.
    Guarantees critical actions (e.g. deployments, emails, credit balance updates)
    require designated personnel approval before execution.
    """
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(
        Enum(ApprovalStatus, name="approval_status_enum", native_enum=False),
        default=ApprovalStatus.PENDING,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Reviewer tracking
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)

    # Relationships
    requester = relationship("User", foreign_keys=[requested_by], back_populates="approval_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by], back_populates="reviewed_approvals")


class AuditLog(Base):
    """
    Tracks every action, decision, tool invocation, and state transition
    performed by specialist agents in the Nextserve system.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    action = Column(String(255), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    task_id = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    status = Column(String(50), default="success", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Task(Base):
    """
    Background tasks executed by orchestrator agents.
    Includes optional pgvector embedding for semantic retrieval.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, completed, failed
    assigned_service = Column(String(100), nullable=True)
    
    # pgvector embedding representation (1536 dims for standard embedding models)
    if HAS_PGVECTOR:
        embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DocumentEmbedding(Base):
    """
    Stores chunked document knowledge, course descriptions, and school policies
    with vector embeddings for cosine similarity retrieval.
    """
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # 'course', 'policy', 'school_doc'
    doc_metadata = Column(JSON, nullable=True)

    # 1536-dimensional vector for OpenAI / standard embedding models
    if HAS_PGVECTOR:
        embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Course(Base):
    """
    Academic courses offered by the school, containing curriculum specifications,
    tuition, prerequisites, and schedules.
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, index=True, nullable=False)
    course_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    credits = Column(Integer, default=3, nullable=False)
    description = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    instructor = Column(String(255), nullable=True)
    schedule = Column(String(255), nullable=True)
    tuition = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class FAQAndPolicy(Base):
    """
    School administrative policies, tuition terms, and frequent student inquiries.
    """
    __tablename__ = "faqs_and_policies"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # 'tuition', 'policy', 'admissions', 'grading'
    question_or_topic = Column(String(255), nullable=False)
    answer_or_policy = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SchoolKnowledgeVector(Base):
    """
    Vector storage table for semantic retrieval over school courses, FAQs, and policies.
    """
    __tablename__ = "school_knowledge_vectors"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # 'course', 'faq', 'policy'
    reference_id = Column(String(100), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    text_content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)

    if HAS_PGVECTOR:
        embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class WebsiteDraft(Base):
    """
    Stores website page updates and new drafts generated by the Website Agent.
    All write/publish actions remain locked behind Level 3 Approval gates.
    """
    __tablename__ = "website_drafts"

    id = Column(String(100), primary_key=True, index=True)
    slug = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    page_type = Column(String(100), default="general", nullable=False)
    seo_metadata = Column(JSON, nullable=True)
    status = Column(String(50), default="pending_approval", nullable=False, index=True)
    preview_url = Column(String(500), nullable=True)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DeploymentAuditLog(Base):
    """
    Tracks all website CMS publications and preflight verification results.
    """
    __tablename__ = "deployment_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(String(100), nullable=False, index=True)
    environment = Column(String(50), default="production", nullable=False)
    status = Column(String(50), default="success", nullable=False, index=True)
    preflight_results = Column(JSON, nullable=True)
    deployment_url = Column(String(500), nullable=True)
    triggered_by = Column(String(100), default="website_agent", nullable=False)
    deployed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class CodePatchDraft(Base):
    """
    Stores code patches, branch info, and diff summaries created by the Coding Agent.
    Submitting a Pull Request remains locked behind Level 3 Approval gates.
    """
    __tablename__ = "code_patches"

    id = Column(String(100), primary_key=True, index=True)
    repo_name = Column(String(255), nullable=False, index=True)
    issue_description = Column(Text, nullable=False)
    target_files = Column(JSON, nullable=False)
    proposed_patch = Column(JSON, nullable=False)
    diff_summary = Column(Text, nullable=False)
    branch_name = Column(String(255), nullable=True)
    status = Column(String(50), default="draft", nullable=False, index=True)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CodeAuditLog(Base):
    """
    Tracks repository analysis, patch generation, static analysis, and PR creation events.
    """
    __tablename__ = "code_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    patch_id = Column(String(100), nullable=True, index=True)
    repo_name = Column(String(255), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="success", nullable=False)
    static_analysis_results = Column(JSON, nullable=True)
    pr_number = Column(Integer, nullable=True)
    pr_url = Column(String(500), nullable=True)
    triggered_by = Column(String(100), default="coding_agent", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Student(Base):
    """
    Stores registered students, enrolled courses, contact information,
    and registration status.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    course_name = Column(String(255), nullable=False, index=True)
    registration_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="registered", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class EmailRecord(Base):
    """
    Stores all incoming emails detected by NextClaw and tracks their
    Human-in-the-Loop review and dispatch status in PostgreSQL.
    """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    email_uid = Column(String(100), nullable=True, index=True)
    sender = Column(String(255), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    received_date = Column(String(100), nullable=True)
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED
    reply_body = Column(Text, nullable=True)
    token = Column(String(100), nullable=True, index=True)  # Telegram callback token (e.g. d_8d4de2f2)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CompositePipelineRun(Base):
    """
    Stores end-to-end multi-agent composite orchestrator runs coordinating:
    School Advising Agent -> Coding Agent -> Website Agent -> HITL Gate -> Multi-Channel Dispatch.
    """
    __tablename__ = "composite_pipeline_runs"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="custom", nullable=False, index=True)
    status = Column(String(50), default="running", nullable=False, index=True)  # running, awaiting_approval, approved, rejected, completed, failed
    current_stage = Column(String(100), default="school_analysis", nullable=False)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    school_output = Column(JSON, nullable=True)
    coding_output = Column(JSON, nullable=True)
    website_output = Column(JSON, nullable=True)
    dispatch_output = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SocialPostDraft(Base):
    """
    Phase 6: Stores multi-channel social media posts and campaigns generated by the Content & Social Agent.
    All social publications are protected behind Level 3 Human-in-the-Loop review.
    """
    __tablename__ = "social_post_drafts"

    id = Column(String(100), primary_key=True, index=True)
    campaign_id = Column(String(100), nullable=True, index=True)
    campaign_name = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=False, index=True)  # x_twitter, linkedin, instagram, facebook, whatsapp
    post_type = Column(String(100), default="announcement", nullable=False)
    topic = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    hashtags = Column(JSON, nullable=True)
    character_count = Column(Integer, default=0, nullable=False)
    cta_link = Column(String(500), nullable=True)
    media_prompt = Column(Text, nullable=True)
    status = Column(String(50), default="pending_approval", nullable=False, index=True)  # draft, pending_approval, approved, published, scheduled, rejected
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    scheduled_for = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SocialAuditLog(Base):
    """
    Phase 6: Immutable audit log for social post drafts, approval reviews, and channel dispatch.
    """
    __tablename__ = "social_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(String(100), nullable=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    status = Column(String(50), default="success", nullable=False)
    details = Column(JSON, nullable=True)
    triggered_by = Column(String(100), default="social_agent", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
