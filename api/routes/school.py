"""
School Agent API Router.
Exposes the POST /api/v1/school/query endpoint for student and faculty queries.
"""
from typing import Optional, List, Dict, Any
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agents.school.agent import query_school_agent, aquery_school_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/school", tags=["school-agent"])


class SchoolQueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="The student or faculty inquiry regarding courses, tuition, schedules, or policies.",
        examples=["What are the prerequisites and tuition for CS101?", "What is the policy for dropping a course?"]
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="Optional conversation thread ID for multi-turn state persistence."
    )


class SchoolQueryResponse(BaseModel):
    query: str
    response: str
    thread_id: str
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


@router.post(
    "/query",
    response_model=SchoolQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Nextserve School AI Assistant",
    description="Ask questions about course syllabi, prerequisites, instructors, tuition payment deadlines, and school policies."
)
async def query_school(request: SchoolQueryRequest):
    """
    Execute semantic search and AI reasoning over the Nextserve school knowledge base.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty."
        )

    try:
        result = await aquery_school_agent(query=request.query, thread_id=request.thread_id)
        return SchoolQueryResponse(
            query=result["query"],
            response=result["response"],
            thread_id=result["thread_id"],
            sources=result.get("sources", [])
        )
    except Exception as exc:
        logger.error("Error processing school agent query: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your school query: {str(exc)}"
        )
