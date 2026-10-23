"""
Verification test suite for Nextserve School Agent Calendar and Campaign Integration.
Tests:
- get_company_calendar_and_events tool
- get_cohort_and_campaign_schedules tool
- query_school_knowledge_base with calendar/campaign context
- query_school_agent end-to-end reasoning on cohorts and calendar
- POST /api/v1/school/query API integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from agents.school.tools import (
    get_company_calendar_and_events,
    get_cohort_and_campaign_schedules,
    query_school_knowledge_base,
)
from agents.school.agent import query_school_agent

client = TestClient(app)


def test_tool_get_company_calendar_and_events():
    """Verify get_company_calendar_and_events retrieves scheduled video series and posts."""
    # Query Dev series
    dev_res = get_company_calendar_and_events.invoke({"query_or_date": "Dev"})
    assert "Dev Ep 1" in dev_res
    assert "May 18, 2026" in dev_res

    # Query UI/UX series
    uiux_res = get_company_calendar_and_events.invoke({"query_or_date": "UIUX"})
    assert "UIUX Ep 1" in uiux_res or "Wireframe" in uiux_res

    # Query Tobi series
    tobi_res = get_company_calendar_and_events.invoke({"query_or_date": "Tobi"})
    assert "Meet Tobi" in tobi_res
    assert "August 31, 2026" in tobi_res

    # Query Two Roads
    two_roads = get_company_calendar_and_events.invoke({"query_or_date": "Two Roads"})
    assert "Two Roads" in two_roads

    # Query Year 2027
    y2027 = get_company_calendar_and_events.invoke({"query_or_date": "2027"})
    assert "2027" in y2027


def test_tool_get_cohort_and_campaign_schedules():
    """Verify get_cohort_and_campaign_schedules retrieves verified cohort and campaign info."""
    # Cohort 3 intake
    c3_res = get_cohort_and_campaign_schedules.invoke({"cohort_or_campaign": "Cohort 3"})
    assert "January 26, 2027" in c3_res
    assert "December 28, 2026" in c3_res

    # Cohort 4 intake & milestone
    c4_res = get_cohort_and_campaign_schedules.invoke({"cohort_or_campaign": "Cohort 4"})
    assert "April 24, 2027" in c4_res
    assert "Graduation" in c4_res or "Capstone" in c4_res

    # Weekend Professionals
    wk_res = get_cohort_and_campaign_schedules.invoke({"cohort_or_campaign": "Weekend"})
    assert "Weekend Professionals Cohort" in wk_res
    assert "November 2, 2026" in wk_res or "November 30, 2026" in wk_res

    # Pitch Contest 2026
    pitch_res = get_cohort_and_campaign_schedules.invoke({"cohort_or_campaign": "Pitch Contest"})
    assert "450,000" in pitch_res
    assert "Muolokwu Ekene Dominic" in pitch_res or "PADIO" in pitch_res


def test_query_school_knowledge_base_calendar():
    """Verify semantic vector search retrieves cohort/calendar documents."""
    res = query_school_knowledge_base.invoke({"query": "When does Cohort 3 start?", "top_k": 3})
    assert "cohort" in res.lower() or "january" in res.lower() or "2027" in res.lower()


def test_query_school_agent_cohorts():
    """Verify school agent handles cohort schedule questions."""
    res = query_school_agent("When does Cohort 3 start and what is the registration window?")
    assert "January 26, 2027" in res["response"] or "Cohort 3" in res["response"]
    assert len(res["sources"]) > 0


def test_query_school_agent_pitch_contest():
    """Verify school agent provides details on Pitch Contest 2026."""
    res = query_school_agent("Tell me about the Nextserve Pitch Contest 2026 and the budget.")
    assert "Pitch Contest" in res["response"]
    assert "450,000" in res["response"]


def test_api_school_query_cohort_schedule():
    """Verify POST /api/v1/school/query returns cohort schedule information."""
    response = client.post("/api/v1/school/query", json={
        "query": "What are the start dates for upcoming cohorts?",
        "thread_id": "test_thread_cohort_dates"
    })
    assert response.status_code == 200
    data = response.json()
    assert "Cohort" in data["response"] or "January" in data["response"] or "November" in data["response"]


def test_api_school_query_marketing_calendar():
    """Verify POST /api/v1/school/query returns video series and marketing calendar information."""
    response = client.post("/api/v1/school/query", json={
        "query": "What is on the Nextserve video series content schedule?",
        "thread_id": "test_thread_video_schedule"
    })
    assert response.status_code == 200
    data = response.json()
    assert "Video" in data["response"] or "Dev" in data["response"] or "Tobi" in data["response"] or "Calendar" in data["response"]


if __name__ == "__main__":
    test_tool_get_company_calendar_and_events()
    test_tool_get_cohort_and_campaign_schedules()
    test_query_school_knowledge_base_calendar()
    test_query_school_agent_cohorts()
    test_query_school_agent_pitch_contest()
    test_api_school_query_cohort_schedule()
    test_api_school_query_marketing_calendar()
    print("All Calendar & Campaign Integration verification tests passed successfully!")
