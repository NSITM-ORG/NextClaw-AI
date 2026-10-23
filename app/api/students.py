"""Student Registration & Directory API Router.

Handles student enrollment submissions, database persistence, and triggers
instant Telegram alerts.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Student, AuditLog
from app.services.telegram_service import telegram_service

router = APIRouter(prefix="/students", tags=["students"])


class StudentRegisterRequest(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    course_name: str
    notes: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    course_name: str
    registration_id: str
    status: str
    created_at: datetime
    telegram_alert_sent: bool = False
    telegram_message_id: Optional[int] = None


@router.post(
    "/register",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student & dispatch Telegram alert",
    description="Saves student enrollment details to PostgreSQL and triggers an instant alert to Telegram."
)
def register_student(
    payload: StudentRegisterRequest,
    db: Session = Depends(get_db)
):
    # Check if student already registered for this course
    existing = db.query(Student).filter(
        Student.email == payload.email,
        Student.course_name == payload.course_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with email '{payload.email}' is already registered for '{payload.course_name}'."
        )

    # Generate unique registration ID
    reg_id = f"REG-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"

    # Persist in DB
    student = Student(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        course_name=payload.course_name,
        registration_id=reg_id,
        status="registered",
        notes=payload.notes,
        created_at=datetime.now(timezone.utc)
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Record Audit Log
    try:
        audit = AuditLog(
            agent_name="student_registration",
            action="student_enrolled",
            task_id=reg_id,
            status="success",
            details={
                "student_id": student.id,
                "full_name": student.full_name,
                "email": student.email,
                "course": student.course_name,
            },
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()
    except Exception:
        db.rollback()

    # Trigger Telegram Alert
    telegram_sent = False
    message_id = None
    try:
        tg_res = telegram_service.send_registration_alert(
            student_name=student.full_name,
            course=student.course_name,
            registration_id=student.registration_id
        )
        if tg_res.get("ok"):
            telegram_sent = True
            message_id = tg_res.get("result", {}).get("message_id")
    except Exception as exc:
        # Don't fail the registration if Telegram alert delivery fails
        pass

    return StudentResponse(
        id=student.id,
        full_name=student.full_name,
        email=student.email,
        phone=student.phone,
        course_name=student.course_name,
        registration_id=student.registration_id,
        status=student.status,
        created_at=student.created_at,
        telegram_alert_sent=telegram_sent,
        telegram_message_id=message_id,
    )


@router.get(
    "/",
    response_model=List[StudentResponse],
    summary="List registered students",
    description="Fetches recent student registrations ordered by registration date."
)
def list_students(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    students = db.query(Student).order_by(Student.id.desc()).limit(limit).all()
    return [
        StudentResponse(
            id=s.id,
            full_name=s.full_name,
            email=s.email,
            phone=s.phone,
            course_name=s.course_name,
            registration_id=s.registration_id,
            status=s.status,
            created_at=s.created_at,
            telegram_alert_sent=True,
        )
        for s in students
    ]
