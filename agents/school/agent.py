import os
import uuid
import logging
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver

from agents.school.tools import (
    query_school_knowledge_base,
    get_course_details,
    calculate_tuition_instalments,
    get_institution_info,
    get_academic_and_admission_policies,
    get_company_calendar_and_events,
    get_cohort_and_campaign_schedules,
    check_unread_gmail_inquiries,
    draft_and_request_email_approval,
)
from app.knowledge.nsitm_knowledge import INSTITUTION_INFO, PROGRAMMES_DATA

logger = logging.getLogger(__name__)

from pathlib import Path

def _load_blueprint_prompt() -> str:
    """Dynamically loads SOUL.md and MEMORY.md blueprints into system prompt."""
    configs_dir = Path(__file__).resolve().parent.parent.parent / "configs"
    soul_file = configs_dir / "SOUL.md"
    memory_file = configs_dir / "MEMORY.md"

    parts = []
    if soul_file.exists():
        try:
            with open(soul_file, "r", encoding="utf-8") as f:
                parts.append(f.read())
        except Exception as e:
            logger.warning("Could not read SOUL.md: %s", e)
    if memory_file.exists():
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                parts.append(f.read())
        except Exception as e:
            logger.warning("Could not read MEMORY.md: %s", e)

    if parts:
        return "\n\n---\n\n".join(parts)
    return (
        "You are Nextclaw, the official School Operating AI for Nextserve School of Information "
        "Technology and Management (NSITM), located in Lagos, Nigeria with nationwide virtual delivery."
    )

SYSTEM_PROMPT = _load_blueprint_prompt()


SCHOOL_TOOLS = [
    query_school_knowledge_base,
    get_course_details,
    calculate_tuition_instalments,
    get_institution_info,
    get_academic_and_admission_policies,
    get_company_calendar_and_events,
    get_cohort_and_campaign_schedules,
    check_unread_gmail_inquiries,
    draft_and_request_email_approval,
]


def _build_langgraph_agent(api_key: Optional[str] = None):
    """Build LangGraph ReAct agent using ChatOpenAI(model='gpt-4o')."""
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=api_key or os.getenv("OPENAI_API_KEY")
    )
    checkpointer = MemorySaver()
    agent = create_react_agent(
        model=llm,
        tools=SCHOOL_TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )
    return agent


class SchoolAgentManager:
    """Manages school agent executions, tool calling, conversational memory,
    and provides a robust offline fallback if OPENAI_API_KEY is not configured.
    """

    def __init__(self):
        self._agent = None
        self._checkpointer = MemorySaver()
        self._init_agent()

    def _init_agent(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self._agent = _build_langgraph_agent(openai_key)
                logger.info("LangGraph School Agent initialized with ChatOpenAI (gpt-4o).")
            except Exception as exc:
                logger.warning("Failed to initialize ChatOpenAI agent: %s. Using tool fallback.", exc)
                self._agent = None
        else:
            logger.info("OPENAI_API_KEY not configured. Running school agent in deterministic tool runner mode.")
            self._agent = None

    def query(self, query_text: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Synchronously query the School Agent."""
        tid = thread_id or f"school_thread_{uuid.uuid4().hex[:8]}"
        openai_key = os.getenv("OPENAI_API_KEY")

        if openai_key:
            if not self._agent:
                self._init_agent()
            if self._agent:
                try:
                    config = {"configurable": {"thread_id": tid}}
                    result = self._agent.invoke(
                        {"messages": [HumanMessage(content=query_text)]},
                        config=config
                    )
                    messages = result.get("messages", [])
                    final_text = ""
                    sources = []
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage) and msg.content:
                            final_text = msg.content
                            break
                        elif isinstance(msg, ToolMessage):
                            sources.append({"tool": msg.name, "content": str(msg.content)[:200]})

                    if final_text:
                        return {
                            "query": query_text,
                            "response": final_text,
                            "thread_id": tid,
                            "sources": sources
                        }
                except Exception as exc:
                    logger.warning("Error running ChatOpenAI agent: %s. Falling back to deterministic runner.", exc)

        return self._run_tool_fallback(query_text, tid)

    async def aquery(self, query_text: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Asynchronously query the School Agent."""
        tid = thread_id or f"school_thread_{uuid.uuid4().hex[:8]}"
        openai_key = os.getenv("OPENAI_API_KEY")

        if openai_key:
            if not self._agent:
                self._init_agent()
            if self._agent:
                try:
                    config = {"configurable": {"thread_id": tid}}
                    result = await self._agent.ainvoke(
                        {"messages": [HumanMessage(content=query_text)]},
                        config=config
                    )
                    messages = result.get("messages", [])
                    final_text = ""
                    sources = []
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage) and msg.content:
                            final_text = msg.content
                            break
                        elif isinstance(msg, ToolMessage):
                            sources.append({"tool": msg.name, "content": str(msg.content)[:200]})

                    if final_text:
                        return {
                            "query": query_text,
                            "response": final_text,
                            "thread_id": tid,
                            "sources": sources
                        }
                except Exception as exc:
                    logger.warning("Error in aquery: %s. Using fallback runner.", exc)

        return self._run_tool_fallback(query_text, tid)

    def _run_tool_fallback(self, query_text: str, thread_id: str) -> Dict[str, Any]:
        """Deterministic agent runner executing tools based on query intent.
        Authoritative NSITM grounding without requiring external API keys.
        """
        query_stripped = query_text.strip()
        query_lower = query_stripped.lower()
        words = query_lower.split()
        sources = []

        # 1. Greetings
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "howdy", "what's up", "yo"]
        if query_lower in greetings or (len(words) <= 2 and any(w in greetings for w in words)):
            return {
                "query": query_text,
                "response": (
                    "Hello! 👋 I'm **NextClaw**, the official Operating AI for **Nextserve School of Information Technology & Management (NSITM)**.\n\n"
                    "I can assist you with:\n"
                    "• 📚 **26 Accredited Programmes** — Fullstack, UI/UX, Cyber Security, Data Science, Digital Marketing, and more\n"
                    "• 💰 **Tuition & 3-Part Instalment Plans** — 40% initial deposit calculations in ₦ Naira\n"
                    "• 📜 **Academic Policies** — 80% attendance rule, Capstone defense, strict no-refund terms\n"
                    "• 📝 **Admissions & Cohorts** — 4-step guided enrollment, online & Lagos hub formats\n"
                    "• 📬 **Gmail Student Inquiries** — Automatic drafting & Level 3 Telegram approval cards\n\n"
                    "What would you like to explore today?"
                ),
                "thread_id": thread_id,
                "sources": []
            }

        # 2. Institutional History / Founder
        if any(p in query_lower for p in ["who founded", "established", "history", "about nextserve", "founder", "background", "where are you located", "campus", "address"]):
            info = get_institution_info.invoke({})
            sources.append({"tool": "get_institution_info"})
            return {
                "query": query_text,
                "response": info,
                "thread_id": thread_id,
                "sources": sources
            }

        # 2b. Academic Cohorts & Strategic Campaigns
        if any(p in query_lower for p in ["cohort", "summer programme", "summer program", "weekend professional", "weekend cohort", "pitch contest", "campaign", "contest"]):
            schedules = get_cohort_and_campaign_schedules.invoke({"cohort_or_campaign": query_text})
            sources.append({"tool": "get_cohort_and_campaign_schedules"})
            return {
                "query": query_text,
                "response": schedules,
                "thread_id": thread_id,
                "sources": sources
            }

        # 2c. Marketing & Content Calendar
        if any(p in query_lower for p in ["calendar", "schedule of post", "content schedule", "video series", "marketing post", "build log", "tobi", "two roads", "the other voice"]):
            events = get_company_calendar_and_events.invoke({"query_or_date": query_text})
            sources.append({"tool": "get_company_calendar_and_events"})
            return {
                "query": query_text,
                "response": events,
                "thread_id": thread_id,
                "sources": sources
            }

        # 3. Instalments & Payment calculations
        if any(p in query_lower for p in ["instalment", "installment", "part payment", "deposit", "payment plan", "how to pay", "40%", "tranche"]):
            # Find which programme
            for p in PROGRAMMES_DATA:
                if p["name"].lower() in query_lower or p["slug"] in query_lower or p["course_code"].lower() in query_lower:
                    breakdown = calculate_tuition_instalments.invoke({"programme_name": p["name"]})
                    sources.append({"tool": "calculate_tuition_instalments", "programme": p["name"]})
                    return {
                        "query": query_text,
                        "response": breakdown,
                        "thread_id": thread_id,
                        "sources": sources
                    }
            # Generic instalment overview if no specific programme mentioned
            sources.append({"tool": "get_academic_and_admission_policies"})
            return {
                "query": query_text,
                "response": (
                    "💰 **Nextserve 3-Part Instalment Plan (Tech Development & Management)**:\n\n"
                    "• **Structure**: 40% initial deposit at enrollment, 30% after 30 days, 30% after 60 days.\n"
                    "• **Eligible Programmes**: All 6-month Tech Development and Management courses (e.g. Fullstack is ₦152,000 initial; Front-End is ₦92,000 initial; Management courses are ₦66,000 initial).\n"
                    "• **Short-Term Courses**: 6-week courses (₦60,000) require 100% full payment upon enrollment.\n"
                    "• **Payment Method**: Direct transfer to Guaranty Trust Bank (GTB).\n"
                    "• **Balance Tracking**: Students manage their schedules and upload follow-up receipts at `/my-payment`."
                ),
                "thread_id": thread_id,
                "sources": sources
            }

        # 4. Suggestions & Academic Policies
        if "attendance" in query_lower and ("capstone" in query_lower or "defense" in query_lower):
            sources.append({"tool": "get_academic_and_admission_policies", "topic": "attendance_and_capstone"})
            return {
                "query": query_text,
                "response": (
                    "Here is a simple explanation of Nextserve's **80% Attendance** and **Capstone Defense** rules:\n\n"
                    "• 📋 **80% Mandatory Attendance Rule**:\n"
                    "  Students must attend at least **80%** of scheduled virtual live sessions or physical classes to qualify for course completion and an official NSITM Certificate. If an emergency occurs, you can request a formal cohort deferral.\n\n"
                    "• 🎓 **Mandatory Capstone Project Defense**:\n"
                    "  To graduate, you must build, submit, and successfully defend a real-world, industry-standard project before a panel of senior faculty. No student graduates on theory alone!\n\n"
                    "Both policies guarantee that every NSITM graduate has proven, portfolio-ready skills employers can trust.\n\n"
                    "👉 *Do you have any questions about class timetables or refund terms?*"
                ),
                "thread_id": thread_id,
                "sources": sources
            }

        if "management" in query_lower and ("short-term" in query_lower or "short term" in query_lower or "programmes" in query_lower):
            sources.append({"tool": "query_school_knowledge_base", "topic": "management_and_short_term"})
            return {
                "query": query_text,
                "response": (
                    "Here are all the **Management** and **Short-Term** programmes offered at Nextserve:\n\n"
                    "💼 **Management Programmes (6 Months — ₦150k one-off or ₦165k in 3 instalments):**\n"
                    "• **Project Management** — Agile, Scrum, Jira, and sprint delivery\n"
                    "• **Product Management** — Market discovery, PRDs, UX wireframes, roadmaps\n"
                    "• **Business Analysis** — Requirements gathering, BPMN, gap analysis\n"
                    "• **Digital Marketing & Growth** — SEO, meta ads, funnels, analytics\n"
                    "• **Human Resource Management** — Talent sourcing, HR software, payroll\n"
                    "• **Accounting & Financial Management** — Budgeting, financial models, audits\n"
                    "• **Executive Virtual Assistance** — CRM, remote ops, executive calendar\n\n"
                    "⚡ **Short-Term Executive Courses (6 Weeks — ₦60k flat, full payment):**\n"
                    "• **Microsoft Office Suites** — Advanced Excel (XLOOKUP, formulas), Word, PowerPoint\n"
                    "• **Image & Video Editing** — Premiere Pro, After Effects, short-form reels\n"
                    "• **AutoCAD / Revit / SolidWorks** — 2D technical drawings & 3D BIM models\n"
                    "• **Sage / QuickBooks / Tally** — Computerized accounting & reconciliations\n\n"
                    "👉 *Which of these courses caught your interest? I can provide full syllabi or fee details!*"
                ),
                "thread_id": thread_id,
                "sources": sources
            }

        if any(p in query_lower for p in ["attendance", "miss class", "absent", "refund", "money back", "cancel", "capstone", "defense", "project", "enroll", "admission"]):
            topic = "attendance" if "attendance" in query_lower or "absent" in query_lower else \
                    "refund" if "refund" in query_lower or "money back" in query_lower else \
                    "capstone" if "capstone" in query_lower or "defense" in query_lower else "admissions"
            policy = get_academic_and_admission_policies.invoke({"topic": topic})
            sources.append({"tool": "get_academic_and_admission_policies", "topic": topic})
            return {
                "query": query_text,
                "response": policy,
                "thread_id": thread_id,
                "sources": sources
            }

        # 5. Check Gmail / Student Inquiries
        if any(p in query_lower for p in ["check email", "check gmail", "unread email", "student inquiries", "inquiry"]):
            email_info = check_unread_gmail_inquiries.invoke({})
            sources.append({"tool": "check_unread_gmail_inquiries"})
            return {
                "query": query_text,
                "response": email_info,
                "thread_id": thread_id,
                "sources": sources
            }

        # 6. Specific Programme Search
        for p in PROGRAMMES_DATA:
            if (p["name"].lower() in query_lower or 
                p["slug"] in query_lower or 
                p["course_code"].lower() in query_lower or
                (p["name"].split()[0].lower() in query_lower and len(p["name"].split()[0]) > 3)):
                details = get_course_details.invoke({"course_code_or_name": p["name"]})
                sources.append({"tool": "get_course_details", "programme": p["name"]})
                return {
                    "query": query_text,
                    "response": details,
                    "thread_id": thread_id,
                    "sources": sources
                }

        # 7. Fallback Vector Search / School Knowledge
        result = query_school_knowledge_base.invoke({"query": query_text})
        sources.append({"tool": "query_school_knowledge_base", "query": query_text})
        return {
            "query": query_text,
            "response": result,
            "thread_id": thread_id,
            "sources": sources
        }


# Global instance
school_agent = SchoolAgentManager()


def query_school_agent(query: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
    """Top-level helper function to synchronously query the school agent."""
    return school_agent.query(query, thread_id)


async def aquery_school_agent(query: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
    """Top-level helper function to asynchronously query the school agent."""
    return await school_agent.aquery(query, thread_id)
