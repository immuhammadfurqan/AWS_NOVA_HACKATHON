"""
Workflow Checkpoint Helpers

Functions for reading and writing workflow state via LangGraph checkpoints.
State is persisted to PostgreSQL for durability across server restarts.
"""

from app.workflow.state import GraphState
from app.workflow.builder import get_recruitment_graph


async def get_state_from_checkpoint(job_id: str) -> GraphState | None:
    """
    Retrieve the current state of a job from the LangGraph checkpoint.
    
    Args:
        job_id: The job/thread ID to retrieve state for
        
    Returns:
        GraphState if found, None if no checkpoint exists
    """
    config = {"configurable": {"thread_id": job_id}}
    
    async with get_recruitment_graph() as graph:
        state_snapshot = await graph.aget_state(config)
        if state_snapshot and state_snapshot.values:
            return state_snapshot.values
    return None


async def save_state_to_checkpoint(job_id: str, state: GraphState) -> None:
    """
    Save updated state to the LangGraph checkpoint.
    
    This is used for manual state updates (e.g., editing JD) outside
    of normal graph execution.
    
    Args:
        job_id: The job/thread ID
        state: The updated state to persist
    """
    config = {"configurable": {"thread_id": job_id}}
    
    async with get_recruitment_graph() as graph:
        await graph.aupdate_state(config, state)
