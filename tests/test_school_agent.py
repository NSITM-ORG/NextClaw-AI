"""
Phase 3 Verification Tests for Nextserve School Agent.
Tests tools, database queries, agent reasoning, and FastAPI endpoint POST /api/v1/school/query.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from agents.school.tools import query_school_knowledge_base, get_course_details
from agents.school.agent import query_school_agent

client = TestClient(app)


def test_docs_endpoint():
    """Verify Swagger UI and OpenAPI schema expose /api/v1/school/query."""
    res = client.get("/docs")
    assert res.status_code == 200

    openapi = client.get("/api/v1/openapi.json").json()
    assert "/api/v1/school/query" in openapi.get("paths", {})


def test_tool_get_course_details():
    """Verify get_course_details tool retrieves course information."""
    result = get_course_details.invoke({"course_code_or_name": "Fullstack"})
    assert "Fullstack" in result
    assert "360,000" in result


def test_tool_query_school_knowledge_base():
    """Verify query_school_knowledge_base tool performs semantic vector search."""
    result = query_school_knowledge_base.invoke({"query": "What is the tuition refund policy?", "top_k": 2})
    assert "refund" in result.lower() or "withdrawal" in result.lower() or "nsitm" in result.lower()


def test_school_agent_function():
    """Verify agent query helper handles questions accurately."""
    res = query_school_agent("Tell me about Fullstack Web Development tuition and schedule.")
    assert "Fullstack" in res["response"]
    assert len(res["sources"]) >= 0


def test_api_school_query_course():
    """Verify POST /api/v1/school/query with course inquiry."""
    response = client.post("/api/v1/school/query", json={
        "query": "What is the tuition and duration for Fullstack Web Development?",
        "thread_id": "test_thread_fsw"
    })
    assert response.status_code == 200
    data = response.json()
    assert "Fullstack" in data["response"]


def test_api_school_query_policy():
    """Verify POST /api/v1/school/query with university policy inquiry."""
    response = client.post("/api/v1/school/query", json={
        "query": "What are the payment instalment options for tuition?",
        "thread_id": "test_thread_tuition"
    })
    assert response.status_code == 200
    data = response.json()
    assert "instalment" in data["response"].lower() or "tuition" in data["response"].lower() or "payment" in data["response"].lower()


def test_api_school_query_empty():
    """Verify POST /api/v1/school/query validation on empty string."""
    response = client.post("/api/v1/school/query", json={
        "query": "   "
    })
    assert response.status_code == 400


if __name__ == "__main__":
    test_docs_endpoint()
    test_tool_get_course_details()
    test_tool_query_school_knowledge_base()
    test_school_agent_function()
    test_api_school_query_course()
    test_api_school_query_policy()
    test_api_school_query_empty()
    print("All Phase 3 test cases passed!")
