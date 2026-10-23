from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.security import get_current_user
from app.db.models import User
from app.services.orchestrator import orchestrator

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_service: Optional[str] = "general"
    approval_level: Optional[int] = 1


class TaskResponse(BaseModel):
    task_id: str
    thread_id: Optional[str] = None
    title: str
    status: str
    current_step: Optional[str] = None
    needs_approval: bool = False
    result: Optional[Dict[str, Any]] = None


class TaskResumeRequest(BaseModel):
    approved: bool
    reviewer_notes: Optional[str] = None


@router.post("/", response_model=TaskResponse)
def create_task(payload: TaskCreate, current_user: User = Depends(get_current_user)):
    task_id = f"task_{abs(hash(payload.title)) % 100000}"
    execution = orchestrator.run_task(
        task_id=task_id,
        prompt=payload.description or payload.title,
        approval_level=payload.approval_level or 1
    )
    is_awaiting_approval = execution.get("status") == "awaiting_approval"
    return TaskResponse(
        task_id=task_id,
        thread_id=execution.get("thread_id"),
        title=payload.title,
        status=execution.get("status", "pending"),
        current_step=execution.get("current_step"),
        needs_approval=is_awaiting_approval,
        result=execution
    )


@router.post("/{thread_id}/resume", response_model=TaskResponse)
def resume_task(
    thread_id: str,
    payload: TaskResumeRequest,
    current_user: User = Depends(get_current_user)
):
    resumed_state = orchestrator.resume_task(
        thread_id=thread_id,
        approved=payload.approved,
        reviewer_notes=payload.reviewer_notes
    )
    if "error" in resumed_state:
        raise HTTPException(status_code=404, detail=resumed_state["error"])

    return TaskResponse(
        task_id=resumed_state.get("task_id", "unknown"),
        thread_id=thread_id,
        title=f"Task {resumed_state.get('task_id')}",
        status=resumed_state.get("status", "completed"),
        current_step=resumed_state.get("current_step"),
        needs_approval=resumed_state.get("status") == "awaiting_approval",
        result=resumed_state
    )


@router.get("/", response_model=List[TaskResponse])
def list_tasks(current_user: User = Depends(get_current_user)):
    return [
        TaskResponse(
            task_id="task_demo_1",
            thread_id="thread_task_demo_1",
            title="Initialize Nextserve Workspace",
            status="completed",
            current_step="report",
            needs_approval=False
        )
    ]
