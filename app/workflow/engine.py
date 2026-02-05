"""
Workflow Engine

High-level abstraction for LangGraph workflow operations.
Encapsulates graph invocation and state management.
"""

from typing import Optional

from app.core.logging import get_logger
from app.workflow.builder import get_recruitment_graph
from app.workflow.state import GraphState, validate_state_for_node
from app.workflow.constants import NodeName
from app.workflow.helpers import dict_to_graph_state, graph_state_to_dict
from app.workflow.exceptions import (
    GraphError,
    GraphExecutionError,
    InvalidStateTransitionError,
    FeatureNotImplementedError,
    JDGenerationError,
    JobPostingError,
    ApplicationMonitoringError,
    ShortlistingError,
    PrescreeningError,
    SchedulingError,
)

logger = get_logger(__name__)


class WorkflowEngine:
    """
    Engine for managing LangGraph recruitment workflow execution.

    Provides a clean interface for workflow operations without
    exposing LangGraph internals to the service layer.
    """

    async def get_state(self, thread_id: str) -> Optional[GraphState]:
        """
        Retrieve the current state of a workflow thread.

        Args:
            thread_id: The unique identifier for the workflow thread

        Returns:
            The current GraphState if found, None otherwise
        """
        try:
            async with get_recruitment_graph() as graph:
                config = {"configurable": {"thread_id": thread_id}}
                state_snapshot = await graph.aget_state(config)
                if state_snapshot and state_snapshot.values:
                    # LangGraph returns dict, convert to Pydantic model
                    return dict_to_graph_state(state_snapshot.values)
                return None
        except GraphError:
            # Re-raise workflow-specific errors
            raise
        except Exception as e:
            logger.warning(f"Failed to get state for thread {thread_id}: {e}")
            return None

    async def save_state(self, thread_id: str, state: GraphState) -> None:
        """
        Save/update the state of a workflow thread.

        Args:
            thread_id: The unique identifier for the workflow thread
            state: The GraphState to persist
            
        Raises:
            GraphExecutionError: If state save fails
        """
        try:
            async with get_recruitment_graph() as graph:
                config = {"configurable": {"thread_id": thread_id}}
                # Convert Pydantic model to dict for LangGraph
                state_dict = graph_state_to_dict(state)
                await graph.aupdate_state(config, state_dict)
        except GraphError:
            raise
        except Exception as e:
            logger.error(f"Failed to save state for thread {thread_id}: {e}")
            raise GraphExecutionError(
                message=f"Failed to save workflow state: {e}",
                node=state.current_node if hasattr(state, 'current_node') else "unknown",
                original_error=str(e),
            )

    async def invoke(self, state: GraphState, thread_id: str) -> GraphState:
        """
        Execute the workflow graph with the given state.

        Args:
            state: The initial or current GraphState
            thread_id: The unique identifier for the workflow thread

        Returns:
            The resulting GraphState after execution
            
        Raises:
            GraphError: Base class for all workflow errors
            JDGenerationError: If JD generation fails
            JobPostingError: If job posting fails
            ApplicationMonitoringError: If monitoring fails
            ShortlistingError: If shortlisting fails
            PrescreeningError: If prescreening fails
            SchedulingError: If interview scheduling fails
            FeatureNotImplementedError: If a feature is not yet implemented
        """
        try:
            async with get_recruitment_graph() as graph:
                config = {"configurable": {"thread_id": thread_id}}
                # Convert Pydantic model to dict for LangGraph
                state_dict = graph_state_to_dict(state)
                result = await graph.ainvoke(state_dict, config)
                # LangGraph returns dict, convert to Pydantic model
                return dict_to_graph_state(result) if result else result
        except (
            JDGenerationError,
            JobPostingError,
            ApplicationMonitoringError,
            ShortlistingError,
            PrescreeningError,
            SchedulingError,
            FeatureNotImplementedError,
            InvalidStateTransitionError,
        ) as e:
            # Log and re-raise specific workflow errors
            logger.error(f"Workflow error in thread {thread_id}: {e.message}")
            raise
        except GraphError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in workflow {thread_id}: {e}")
            raise GraphExecutionError(
                message=f"Workflow execution failed: {e}",
                node=state.current_node if state else "unknown",
                original_error=str(e),
            )

    async def update_and_resume(
        self, 
        thread_id: str, 
        state: GraphState,
        validate: bool = True,
    ) -> GraphState:
        """
        Update state and resume workflow execution.

        Use this for human-in-the-loop scenarios where state is
        modified externally and the workflow needs to continue.

        Args:
            thread_id: The unique identifier for the workflow thread
            state: The updated GraphState
            validate: Whether to validate state before resuming (default: True)

        Returns:
            The resulting GraphState after resuming execution
            
        Raises:
            InvalidStateTransitionError: If state validation fails
            GraphExecutionError: If workflow execution fails
        """
        try:
            # Optionally validate state before resuming
            if validate:
                current_node = state.current_node
                if current_node:
                    try:
                        target = NodeName(current_node)
                        validate_state_for_node(state, target)
                    except ValueError:
                        # Current node is not in NodeName enum (e.g., "pending", "jd_review")
                        # This is okay, validation is optional for these states
                        pass
            
            async with get_recruitment_graph() as graph:
                config = {"configurable": {"thread_id": thread_id}}
                # Convert Pydantic model to dict for LangGraph
                state_dict = graph_state_to_dict(state)
                await graph.aupdate_state(config, state_dict)
                # Resume from the updated state
                result = await graph.ainvoke(None, config)
                # LangGraph returns dict, convert to Pydantic model
                return dict_to_graph_state(result) if result else result
        except InvalidStateTransitionError:
            raise
        except (
            JDGenerationError,
            JobPostingError,
            ApplicationMonitoringError,
            ShortlistingError,
            PrescreeningError,
            SchedulingError,
            FeatureNotImplementedError,
        ) as e:
            logger.error(f"Workflow error resuming thread {thread_id}: {e.message}")
            raise
        except GraphError:
            raise
        except Exception as e:
            logger.error(f"Failed to resume workflow {thread_id}: {e}")
            raise GraphExecutionError(
                message=f"Failed to resume workflow: {e}",
                node=state.current_node if state else "unknown",
                original_error=str(e),
            )

    async def validate_transition(
        self, 
        state: GraphState, 
        target_node: NodeName,
    ) -> None:
        """
        Validate that a state transition is allowed.
        
        Args:
            state: Current graph state
            target_node: The node to transition to
            
        Raises:
            InvalidStateTransitionError: If transition is not valid
        """
        validate_state_for_node(state, target_node)
