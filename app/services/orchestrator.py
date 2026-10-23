from typing import Any, Dict, Optional
import uuid
import logging

from app.services.graph import (
    AgentState,
    understand_node,
    search_school_knowledge_node,
    plan_node,
    pause_approval_node,
    execute_node,
    verify_node,
    report_node,
)
from app.db.memory import postgres_memory_manager, get_postgres_checkpointer

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
    try:
        from langgraph.checkpoint.memory import MemorySaver
        HAS_MEMORY_SAVER = True
    except ImportError:
        HAS_MEMORY_SAVER = False
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    HAS_MEMORY_SAVER = False


def route_after_understand(state: AgentState) -> str:
    """
    Evaluates whether user inquiry relates to courses, school documents,
    or university policies. If detected, branches to the search_school_knowledge
    tool node to perform semantic vector search against pgvector.
    Otherwise, proceeds directly to plan.
    """
    messages = list(state.get("messages", []))
    prompt = (messages[0] if messages else "").lower()
    school_keywords = [
        "course", "courses", "class", "classes", "syllabus", "prereq", "prerequisite",
        "credit", "credits", "doc", "docs", "document", "documents", "handbook",
        "policy", "policies", "grading", "attendance", "admission", "refund",
        "integrity", "enrollment", "tuition", "calendar", "exam", "grade", "grades"
    ]
    if any(k in prompt for k in school_keywords):
        return "search_school_knowledge"
    return "plan"


def route_after_plan(state: AgentState) -> str:
    """
    Conditional Routing Edge:
    Evaluates whether task requires Level 3 Human-in-the-Loop approval.
    If Level 3 approval is required and not yet granted, branch to pause node.
    Otherwise, proceed directly to execute.
    """
    approval_level = state.get("approval_level", 1)
    is_approved = state.get("is_approved", False)

    if approval_level >= 3 and not is_approved:
        return "pause_for_approval"
    return "execute"


class WorkflowOrchestrator:
    """
    Orchestrator managing task execution lifecycle:
    Understand -> [search_school_knowledge if school query] -> Plan -> [Pause if Level 3] -> Execute -> Verify -> Report.
    Supports persistent thread checkpointing with AsyncPostgresSaver and MemorySaver fallback.
    """

    def __init__(self):
        self.workflow = None
        self.checkpointer = MemorySaver() if HAS_MEMORY_SAVER else None
        # Thread state cache for resume operations
        self._thread_states: Dict[str, AgentState] = {}
        
        if HAS_LANGGRAPH:
            self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        # 1. Register state machine nodes & tools
        builder.add_node("understand", understand_node)
        builder.add_node("search_school_knowledge", search_school_knowledge_node)
        builder.add_node("plan", plan_node)
        builder.add_node("pause_for_approval", pause_approval_node)
        builder.add_node("execute", execute_node)
        builder.add_node("verify", verify_node)
        builder.add_node("report", report_node)

        # 2. Configure Transitions
        builder.set_entry_point("understand")

        # Conditional tool call after Understand: query vector store if user asks about school/courses/policies
        builder.add_conditional_edges(
            "understand",
            route_after_understand,
            {
                "search_school_knowledge": "search_school_knowledge",
                "plan": "plan"
            }
        )

        # Tool node transitions to planning with retrieved knowledge context
        builder.add_edge("search_school_knowledge", "plan")

        # Conditional branch after Plan: Check for Level 3 approval gate
        builder.add_conditional_edges(
            "plan",
            route_after_plan,
            {
                "pause_for_approval": "pause_for_approval",
                "execute": "execute"
            }
        )

        # If paused for approval, stop at this gate until resumed by human approval
        builder.add_edge("pause_for_approval", END)

        # Main execution line: Execute -> Verify -> Report -> END
        builder.add_edge("execute", "verify")
        builder.add_edge("verify", "report")
        builder.add_edge("report", END)

        # Compile graph with checkpointer and interrupt before execute
        compile_kwargs = {}
        if self.checkpointer:
            compile_kwargs["checkpointer"] = self.checkpointer
            compile_kwargs["interrupt_before"] = ["execute"]

        self.workflow = builder.compile(**compile_kwargs)

    def run_task(
        self,
        task_id: str,
        prompt: str,
        approval_level: int = 1,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute or initiate a task through the state machine.
        If approval_level == 3, pauses before 'execute' until approved.
        """
        tid = thread_id or f"thread_{task_id}_{uuid.uuid4().hex[:6]}"
        initial_state: AgentState = {
            "task_id": task_id,
            "thread_id": tid,
            "messages": [prompt],
            "current_step": "init",
            "approval_level": approval_level,
            "is_approved": False,
            "approval_id": None,
            "approval_payload": None,
            "plan": None,
            "retrieved_context": None,
            "execution_result": None,
            "verification_result": None,
            "final_report": None,
            "status": "started"
        }

        # Cache initial state
        self._thread_states[tid] = initial_state

        if self.workflow:
            config = {"configurable": {"thread_id": tid}} if self.checkpointer else {}
            result = self.workflow.invoke(initial_state, config=config)
            self._thread_states[tid] = result
            return result

        # Fallback runner when LangGraph library is pending in environment
        return self._run_fallback(initial_state)

    async def arun_task(
        self,
        task_id: str,
        prompt: str,
        approval_level: int = 1,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Asynchronous execution using AsyncPostgresSaver checkpointer
        for full PostgreSQL thread state persistence.
        """
        tid = thread_id or f"thread_{task_id}_{uuid.uuid4().hex[:6]}"
        initial_state: AgentState = {
            "task_id": task_id,
            "thread_id": tid,
            "messages": [prompt],
            "current_step": "init",
            "approval_level": approval_level,
            "is_approved": False,
            "approval_id": None,
            "approval_payload": None,
            "plan": None,
            "retrieved_context": None,
            "execution_result": None,
            "verification_result": None,
            "final_report": None,
            "status": "started"
        }

        self._thread_states[tid] = initial_state

        if HAS_LANGGRAPH:
            postgres_saver = await postgres_memory_manager.get_checkpointer()
            builder = StateGraph(AgentState)
            builder.add_node("understand", understand_node)
            builder.add_node("search_school_knowledge", search_school_knowledge_node)
            builder.add_node("plan", plan_node)
            builder.add_node("pause_for_approval", pause_approval_node)
            builder.add_node("execute", execute_node)
            builder.add_node("verify", verify_node)
            builder.add_node("report", report_node)

            builder.set_entry_point("understand")
            builder.add_conditional_edges(
                "understand",
                route_after_understand,
                {
                    "search_school_knowledge": "search_school_knowledge",
                    "plan": "plan"
                }
            )
            builder.add_edge("search_school_knowledge", "plan")
            builder.add_conditional_edges(
                "plan",
                route_after_plan,
                {
                    "pause_for_approval": "pause_for_approval",
                    "execute": "execute"
                }
            )
            builder.add_edge("pause_for_approval", END)
            builder.add_edge("execute", "verify")
            builder.add_edge("verify", "report")
            builder.add_edge("report", END)

            app = builder.compile(checkpointer=postgres_saver, interrupt_before=["execute"])
            config = {"configurable": {"thread_id": tid}}
            result = await app.ainvoke(initial_state, config=config)
            self._thread_states[tid] = result
            return result

        return self._run_fallback(initial_state)

    def resume_task(
        self,
        thread_id: str,
        approved: bool,
        reviewer_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resume an interrupted task after Human-in-the-Loop approval decision.
        """
        state = self._thread_states.get(thread_id)
        if not state:
            return {"error": f"Thread ID '{thread_id}' not found", "status": "failed"}

        if not approved:
            state["status"] = "rejected"
            state["current_step"] = "rejected"
            state["messages"] = list(state.get("messages", [])) + [
                f"[Approval Rejected] Task rejected by human reviewer. Notes: {reviewer_notes}"
            ]
            self._thread_states[thread_id] = state
            return state

        # Mark approved and resume execution: Execute -> Verify -> Report
        state["is_approved"] = True
        state["messages"] = list(state.get("messages", [])) + [
            f"[Approval Granted] Level 3 gate passed. Resuming execution. Notes: {reviewer_notes}"
        ]

        if self.workflow and self.checkpointer:
            config = {"configurable": {"thread_id": thread_id}}
            result = self.workflow.invoke(state, config=config)
            # Resume past interrupt_before=['execute'] gate
            if result.get("status") == "planned" and result.get("is_approved"):
                result = self.workflow.invoke(None, config=config)
            self._thread_states[thread_id] = result
            return result

        # Fallback continuation: Execute -> Verify -> Report
        step_exec = execute_node(state)
        state.update(step_exec)
        step_verify = verify_node(state)
        state.update(step_verify)
        step_report = report_node(state)
        state.update(step_report)

        self._thread_states[thread_id] = state
        return state

    def _run_fallback(self, state: AgentState) -> Dict[str, Any]:
        """Deterministic simulation of the state machine transitions."""
        # 1. Understand
        state.update(understand_node(state))

        # Tool node: search_school_knowledge if requested
        if route_after_understand(state) == "search_school_knowledge":
            state.update(search_school_knowledge_node(state))

        # 2. Plan
        state.update(plan_node(state))

        # Check Level 3 approval interrupt
        if route_after_plan(state) == "pause_for_approval":
            state.update(pause_approval_node(state))
            self._thread_states[state["thread_id"]] = state
            return state

        # 3. Execute
        state.update(execute_node(state))

        # 4. Verify
        state.update(verify_node(state))

        # 5. Report
        state.update(report_node(state))

        self._thread_states[state["thread_id"]] = state
        return state


orchestrator = WorkflowOrchestrator()
