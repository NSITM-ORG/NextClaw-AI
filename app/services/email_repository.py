"""Email Repository Service for NextClaw.

Manages persistent storage and lifecycle tracking of incoming emails,
draft responses, and Human-in-the-Loop decision states in PostgreSQL.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import SessionLocal, init_db, Base, engine
from app.db.models import EmailRecord

logger = logging.getLogger("email_repository")


class EmailRepository:
    """Repository for storing and updating EmailRecord instances in PostgreSQL."""

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure the emails table is created in PostgreSQL."""
        try:
            Base.metadata.create_all(bind=engine, tables=[EmailRecord.__table__])
        except Exception as exc:
            logger.warning("Could not auto-create emails table: %s", exc)

    def save_incoming_email(
        self,
        sender: str,
        subject: str,
        body: str,
        received_date: Optional[str] = None,
        sender_name: Optional[str] = None,
        email_uid: Optional[str] = None,
        token: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> EmailRecord:
        """Saves a newly detected incoming email with status 'PENDING'.

        Args:
            sender: Email address of sender
            subject: Subject line
            body: Email body text
            received_date: Raw date string from email header
            sender_name: Display name of sender
            email_uid: IMAP unique message ID / sequence number
            token: Short Telegram approval token (e.g. d_8d4de2f2)
            db: Optional active DB session. If None, creates a temporary session.

        Returns:
            The saved or updated EmailRecord instance.
        """
        session = db or SessionLocal()
        should_close = db is None

        try:
            # Check for existing record by email_uid to prevent duplicates
            record = None
            if email_uid:
                record = session.query(EmailRecord).filter(EmailRecord.email_uid == str(email_uid)).first()

            if record:
                if token:
                    record.token = token
                record.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(record)
                logger.info("Updated existing EmailRecord ID %s with token %s", record.id, token)
                return record

            new_email = EmailRecord(
                email_uid=str(email_uid) if email_uid else None,
                sender=sender,
                sender_name=sender_name,
                subject=subject,
                body=body,
                received_date=received_date,
                status="PENDING",
                token=token,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(new_email)
            session.commit()
            session.refresh(new_email)
            logger.info("Saved new incoming EmailRecord ID %s from %s (Status: PENDING)", new_email.id, sender)
            return new_email

        except Exception as e:
            session.rollback()
            logger.error("Failed to save incoming email to DB: %s", e)
            raise
        finally:
            if should_close:
                session.close()

    def update_email_status(
        self,
        token_or_id: str,
        status: str = "APPROVED",
        reply_body: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Optional[EmailRecord]:
        """Updates an email record status (e.g. 'APPROVED' or 'REJECTED') and stores sent reply.

        Args:
            token_or_id: The approval token (e.g. 'd_8d4de2f2') or integer ID as string
            status: 'APPROVED' or 'REJECTED'
            reply_body: Text of the approved response sent via NextClaw
            db: Optional active DB session.

        Returns:
            Updated EmailRecord or None if not found.
        """
        session = db or SessionLocal()
        should_close = db is None

        try:
            query = session.query(EmailRecord)
            int_id = int(token_or_id) if token_or_id.isdigit() else None

            if int_id:
                record = query.filter(or_(EmailRecord.id == int_id, EmailRecord.token == token_or_id)).first()
            else:
                record = query.filter(EmailRecord.token == token_or_id).first()

            if not record:
                logger.warning("No EmailRecord found matching token/id: %s", token_or_id)
                return None

            record.status = status.upper()
            if reply_body:
                record.reply_body = reply_body
            if status.upper() == "APPROVED":
                record.approved_at = datetime.now(timezone.utc)
            record.updated_at = datetime.now(timezone.utc)

            session.commit()
            session.refresh(record)
            logger.info(
                "Updated EmailRecord ID %s to status '%s' with reply length %d",
                record.id,
                record.status,
                len(reply_body or ""),
            )
            return record

        except Exception as e:
            session.rollback()
            logger.error("Failed to update email status for %s: %s", token_or_id, e)
            raise
        finally:
            if should_close:
                session.close()

    def get_email_by_token(self, token: str, db: Optional[Session] = None) -> Optional[EmailRecord]:
        """Fetch EmailRecord by its approval token."""
        session = db or SessionLocal()
        should_close = db is None
        try:
            return session.query(EmailRecord).filter(EmailRecord.token == token).first()
        finally:
            if should_close:
                session.close()

    def get_email_by_uid(self, email_uid: str, db: Optional[Session] = None) -> Optional[EmailRecord]:
        """Fetch EmailRecord by its IMAP email_uid."""
        if not email_uid:
            return None
        session = db or SessionLocal()
        should_close = db is None
        try:
            return session.query(EmailRecord).filter(EmailRecord.email_uid == str(email_uid)).first()
        finally:
            if should_close:
                session.close()

    def list_emails(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        db: Optional[Session] = None,
    ) -> List[EmailRecord]:
        """List email records, optionally filtered by status."""
        session = db or SessionLocal()
        should_close = db is None
        try:
            q = session.query(EmailRecord)
            if status:
                q = q.filter(EmailRecord.status == status.upper())
            return q.order_by(EmailRecord.id.desc()).limit(limit).all()
        finally:
            if should_close:
                session.close()


# Global repository instance
email_repository = EmailRepository()
