"""
Workflow Graph Builder

Constructs and compiles the LangGraph recruitment workflow.
Uses PostgreSQL-based checkpointing for persistent state.
"""

from contextlib import asynccontextmanager

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import get_settings
from app.workflow.state import GraphState
from app.workflow.constants import NodeName, WAIT_FOR_HUMAN
from app.workflow.nodes import (
    generate_jd_node,
    post_job_node,
    monitor_applications_node,
    shortlist_candidates_node,
    voice_prescreening_node,
    review_responses_node,
    schedule_interview_node,
    schedule_interview_node,
    reject_candidate_node,
    optimize_jd_node,
)
from app.workflow.edges import (
    should_regenerate_jd,
    check_jd_approval,
    check_shortlist_approval,
    recruiter_decision,
)


def build_recruitment_graph() -> StateGraph:
    """
    Build the complete recruitment workflow graph.

    Graph Structure:
    generate_jd -> [approval?] -> post_job -> monitor_applications
        -> [enough applicants?] -> shortlist_candidates
        -> [approval?] -> voice_prescreening -> review_responses
        -> [decision] -> schedule_interview | reject_candidate

    Returns:
        StateGraph: The uncompiled workflow graph
    """
    workflow = StateGraph(GraphState)

    # Add nodes using NodeName enum for consistency
    workflow.add_node(NodeName.GENERATE_JD.value, generate_jd_node)
    workflow.add_node(NodeName.POST_JOB.value, post_job_node)
    workflow.add_node(NodeName.MONITOR_APPLICATIONS.value, monitor_applications_node)
    workflow.add_node(NodeName.SHORTLIST_CANDIDATES.value, shortlist_candidates_node)
    workflow.add_node(NodeName.VOICE_PRESCREENING.value, voice_prescreening_node)
    workflow.add_node(NodeName.REVIEW_RESPONSES.value, review_responses_node)
    workflow.add_node(NodeName.SCHEDULE_INTERVIEW.value, schedule_interview_node)
    workflow.add_node(NodeName.REJECT_CANDIDATE.value, reject_candidate_node)
    workflow.add_node(NodeName.OPTIMIZE_JD.value, optimize_jd_node)

    # Set entry point
    workflow.set_entry_point(NodeName.GENERATE_JD.value)

    # JD approval gate
    workflow.add_conditional_edges(
        NodeName.GENERATE_JD.value,
        check_jd_approval,
        {
            NodeName.POST_JOB.value: NodeName.POST_JOB.value,
            WAIT_FOR_HUMAN: END,  # Pause for human approval
        },
    )

    workflow.add_edge(NodeName.POST_JOB.value, NodeName.MONITOR_APPLICATIONS.value)

    # Applicant threshold check
    workflow.add_conditional_edges(
        NodeName.MONITOR_APPLICATIONS.value,
        should_regenerate_jd,
        {
            NodeName.GENERATE_JD.value: NodeName.GENERATE_JD.value,
            NodeName.SHORTLIST_CANDIDATES.value: NodeName.SHORTLIST_CANDIDATES.value,
            NodeName.OPTIMIZE_JD.value: NodeName.OPTIMIZE_JD.value,
            WAIT_FOR_HUMAN: END,
        },
    )

    # Shortlist approval gate
    workflow.add_conditional_edges(
        NodeName.SHORTLIST_CANDIDATES.value,
        check_shortlist_approval,
        {
            NodeName.VOICE_PRESCREENING.value: NodeName.VOICE_PRESCREENING.value,
            WAIT_FOR_HUMAN: END,  # Pause for human approval
        },
    )

    workflow.add_edge(
        NodeName.VOICE_PRESCREENING.value, NodeName.REVIEW_RESPONSES.value
    )

    # Recruiter decision after prescreening
    workflow.add_conditional_edges(
        NodeName.REVIEW_RESPONSES.value,
        recruiter_decision,
        {
            NodeName.SCHEDULE_INTERVIEW.value: NodeName.SCHEDULE_INTERVIEW.value,
            NodeName.REJECT_CANDIDATE.value: NodeName.REJECT_CANDIDATE.value,
        },
    )

    # Loop back to posting after optimization
    workflow.add_edge(NodeName.OPTIMIZE_JD.value, NodeName.POST_JOB.value)

    # Terminal nodes
    workflow.add_edge(NodeName.SCHEDULE_INTERVIEW.value, END)
    workflow.add_edge(NodeName.REJECT_CANDIDATE.value, END)

    return workflow


@asynccontextmanager
async def get_recruitment_graph():
    """
    Context manager to get a compiled graph with PostgreSQL checkpointer.

    Usage:
        async with get_recruitment_graph() as graph:
            result = await graph.ainvoke(initial_state, config)

    Yields:
        CompiledGraph: Ready-to-use graph with checkpointing enabled
    """
    settings = get_settings()

    # Convert asyncpg URL to psycopg-compatible URL
    db_url = settings.database_url.replace("postgresql+asyncpg", "postgresql")

    async with AsyncPostgresSaver.from_conn_string(db_url) as checkpointer:
        await checkpointer.setup()
        workflow = build_recruitment_graph()
        yield workflow.compile(checkpointer=checkpointer)
