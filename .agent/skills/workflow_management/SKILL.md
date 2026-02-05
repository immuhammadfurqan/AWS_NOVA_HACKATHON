---
name: workflow_management
description: Manage LangGraph workflows, debug state transitions, and handle checkpoints
---

# LangGraph Workflow Management Skill

## Purpose
Master the AARLP recruitment workflow powered by LangGraph. This skill covers workflow debugging, state management, checkpoint handling, and adding new nodes/edges to the graph.

## AI Provider Selection (Amazon Nova AI Hackathon)

**AARLP supports two AI providers:**
- `bedrock` (default for hackathon) - AWS Nova models
- `openai` (fallback) - OpenAI GPT-4

Set via `AI_PROVIDER` environment variable.

## Secrets Management

**Required for External API Calls:**

| Secret | Provider | Purpose |
|--------|----------|---------|
| `AWS_ACCESS_KEY_ID` | bedrock | Nova model access |
| `AWS_SECRET_ACCESS_KEY` | bedrock | Nova model access |
| `OPENAI_API_KEY` | openai | JD generation fallback |
| `PINECONE_API_KEY` | both | Shortlisting nodes |

**Configuration (app/core/config.py):**
```python
class Settings(BaseSettings):
    # AI Provider Selection
    ai_provider: Literal["openai", "bedrock"] = "bedrock"
    
    # AWS Bedrock (Primary for hackathon)
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    
    # OpenAI (Fallback)
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    class Config:
        env_file = ".env"
```

**Security in Workflow Nodes:**
```python
async def api_integration_node(state: GraphState) -> GraphState:
    """Use provider-agnostic client for AI calls."""
    from app.ai.client import is_bedrock_provider
    from app.core.config import get_settings
    
    if is_bedrock_provider():
        from app.ai.bedrock_client import invoke_nova_model
        result = await invoke_nova_model(messages=[...])
    else:
        from app.ai.client import get_openai_client
        client = get_openai_client()
        response = await client.chat.completions.create(...)
    
    # NEVER log API keys
    logger.info(f"AI call completed for job {state.job_id}")
    
    return state.model_copy(...)
```

## Architecture Overview

### Workflow Files Structure
```
app/workflow/
├── state.py          # Pydantic GraphState models
├── nodes.py          # Node function implementations
├── edges.py          # Conditional routing logic
├── builder.py        # Graph construction
├── engine.py         # High-level workflow API
├── checkpoints.py    # State persistence
├── constants.py      # NodeName enum, constants
├── helpers.py        # Shared utilities
└── exceptions.py     # Workflow errors
```

## Core Concepts

### 1. State Management (Pydantic-Based)

The workflow uses **immutable Pydantic models** for type-safe state:

```python
from app.workflow.state import GraphState

# State is always accessed through Pydantic models
state = GraphState(
    job_id="123",
    current_node="generate_jd",
    jd=JobDescriptionState(
        title="Senior Engineer",
        status=Status.PENDING,
        approval_status=ApprovalStatus.PENDING
    )
)

# Type-safe access with autocomplete
print(state.jd.approval_status)  # ✅ IDE knows this is ApprovalStatus
```

**Key Benefits:**
- ✅ Runtime validation on every state update
- ✅ No manual dict-to-object conversions
- ✅ Full IDE support with autocomplete
- ✅ Nested state objects for organization

### 2. Checkpointing (Pause/Resume)

AARLP uses checkpoints to persist workflow state:

```python
from app.workflow.engine import WorkflowEngine
from app.workflow.checkpoints import save_checkpoint, load_checkpoint

# Initialize with checkpointing enabled
# IMPORTANT: Use consistent thread_id format: f"job-{job_id}"
engine = WorkflowEngine(
    job_id="job-123",
    thread_id="job-123",  # Standard format: job-{job_id}
    enable_checkpointing=True
)

# Run until human-in-the-loop wait state
result = await engine.run_until_interrupt()

# Later, resume from checkpoint
resumed_state = await engine.resume_from_checkpoint(
    updates={"jd": {"approval_status": "APPROVED"}}
)
```

**Checkpoint Use Cases:**
- JD approval waiting
- Shortlist approval waiting
- Voice interview scheduling
- Any human-in-the-loop decision point

### 3. Node Development

#### Node Function Signature
```python
from app.workflow.state import GraphState

async def my_node(state: GraphState) -> GraphState:
    """
    All nodes must:
    1. Accept GraphState as input
    2. Return modified GraphState
    3. Be async (for DB/API calls)
    4. Handle errors with custom exceptions
    """
    
    # Extract what you need (type-safe)
    job_id = state.job_id
    
    # Do work
    result = await some_async_operation(job_id)
    
    # Return updated state (Pydantic handles validation)
    return state.model_copy(
        update={
            "current_node": "my_node",
            "updated_at": datetime.now(timezone.utc)
        }
    )
```

#### Adding a New Node

1. **Define the node function** in `nodes.py`:
```python
async def my_new_node(state: GraphState) -> GraphState:
    """Description of what this node does."""
    try:
        # Your logic here
        logger.info(f"Processing {state.job_id} in my_new_node")
        
        # Update state
        return state.model_copy(
            update={"current_node": NodeName.MY_NEW_NODE}
        )
    except Exception as e:
        logger.error(f"Error in my_new_node: {e}")
        raise GraphExecutionError(f"Failed at my_new_node: {e}")
```

2. **Add node name to constants** in `constants.py`:
```python
class NodeName(str, Enum):
    GENERATE_JD = "generate_jd"
    MY_NEW_NODE = "my_new_node"  # Add this
```

3. **Register in builder** in `builder.py`:
```python
from app.workflow.nodes import my_new_node

graph.add_node(NodeName.MY_NEW_NODE, my_new_node)
```

4. **Add edges** (routing):
```python
# Simple edge
graph.add_edge(NodeName.GENERATE_JD, NodeName.MY_NEW_NODE)

# Conditional edge
graph.add_conditional_edges(
    NodeName.MY_NEW_NODE,
    my_routing_function,  # Defined in edges.py
    {
        "success": NodeName.NEXT_NODE,
        "failure": NodeName.ERROR_NODE
    }
)
```

### 4. Conditional Routing (Edges)

Edges determine the next node based on state:

```python
# In edges.py
def my_routing_function(state: GraphState) -> str:
    """
    Return a string key that maps to a node in the edge map.
    """
    if state.jd.approval_status == ApprovalStatus.APPROVED:
        return "approved"
    elif state.jd.approval_status == ApprovalStatus.REJECTED:
        return "rejected"
    else:
        return "waiting"

# In builder.py
graph.add_conditional_edges(
    NodeName.WAIT_JD_APPROVAL,
    my_routing_function,
    {
        "approved": NodeName.POST_JOB,
        "rejected": NodeName.GENERATE_JD,  # Regenerate
        "waiting": NodeName.WAIT_JD_APPROVAL  # Stay in wait state
    }
)
```

## Common Workflow Patterns

### Pattern 1: Human-in-the-Loop
```python
async def wait_for_approval_node(state: GraphState) -> GraphState:
    """
    Node that interrupts execution until human approval.
    Uses special interrupt pattern.
    """
    from langgraph.types import interrupt
    
    # Send interrupt signal with current state
    interrupt(
        value={
            "message": "Waiting for JD approval",
            "job_id": state.job_id,
            "jd": state.jd.model_dump()
        }
    )
    
    # This line only executes after resume
    return state.model_copy(
        update={"current_node": NodeName.WAIT_JD_APPROVAL}
    )
```

### Pattern 2: Error Handling
```python
async def robust_node(state: GraphState) -> GraphState:
    """Node with comprehensive error handling."""
    try:
        result = await risky_operation()
        
        return state.model_copy(
            update={"current_node": NodeName.ROBUST_NODE}
        )
    
    except SpecificError as e:
        # Log and store error in state
        logger.error(f"Specific error: {e}")
        return state.model_copy(
            update={
                "error_message": str(e),
                "current_node": NodeName.ERROR_HANDLER
            }
        )
    
    except Exception as e:
        # Unexpected errors raise custom exception
        logger.critical(f"Unexpected error: {e}")
        raise GraphExecutionError(f"Failed: {e}")
```

### Pattern 3: External API Integration
```python
async def api_integration_node(state: GraphState) -> GraphState:
    """Call external APIs within workflow."""
    from app.ai.client import get_openai_client
    
    client = get_openai_client()
    
    # Make async API call
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "..."}]
    )
    
    result = response.choices[0].message.content
    
    # Store result in state
    return state.model_copy(
        update={
            "jd": state.jd.model_copy(update={"content": result})
        }
    )
```

## Debugging Workflows

### 1. Enable Debug Logging
```python
# In config
import logging
logging.getLogger("app.workflow").setLevel(logging.DEBUG)
```

### 2. Inspect State at Each Node
```python
# Add to node for debugging
logger.debug(f"State at {NodeName.MY_NODE}: {state.model_dump_json(indent=2)}")
```

### 3. Test Individual Nodes
```python
# In tests/workflow/test_nodes.py
import pytest
from app.workflow.nodes import my_node
from app.workflow.state import GraphState

@pytest.mark.asyncio
async def test_my_node():
    # Arrange
    initial_state = GraphState(
        job_id="test-123",
        current_node="start",
        jd=JobDescriptionState(status=Status.PENDING)
    )
    
    # Act
    result = await my_node(initial_state)
    
    # Assert
    assert result.current_node == NodeName.MY_NODE
    assert result.jd.status == Status.COMPLETED
```

### 4. Validate State Transitions
```python
# Test edge logic
from app.workflow.edges import my_routing_function

def test_routing_approved():
    state = GraphState(
        job_id="123",
        jd=JobDescriptionState(approval_status=ApprovalStatus.APPROVED)
    )
    
    next_node = my_routing_function(state)
    assert next_node == "approved"
```

## Production Best Practices

### 1. Always Use Thread IDs
```python
# For checkpoint persistence - use consistent format
# Pattern: job-{job_id} (no UUID suffix for AARLP)
thread_id = f"job-{job_id}"
engine = WorkflowEngine(job_id=job_id, thread_id=thread_id)

# If you need multiple workflows per job (rare):
# thread_id = f"job-{job_id}-{workflow_type}"
```

### 2. Handle State Migrations
```python
# When updating GraphState schema, provide defaults
class GraphState(BaseModel):
    new_field: Optional[str] = None  # Add defaults for new fields
```

### 3. Idempotent Nodes
```python
async def idempotent_node(state: GraphState) -> GraphState:
    """
    Node can be safely re-run without side effects.
    Check if work is already done.
    """
    if state.jd.status == Status.COMPLETED:
        logger.info("JD already generated, skipping")
        return state
    
    # Do work...
```

### 4. Timeout Handling
```python
import asyncio

async def node_with_timeout(state: GraphState) -> GraphState:
    try:
        result = await asyncio.wait_for(
            long_running_task(),
            timeout=30.0  # 30 seconds
        )
    except asyncio.TimeoutError:
        logger.error("Node timed out")
        raise GraphExecutionError("Operation timed out")
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| State not persisting | Ensure `thread_id` is set and checkpointing enabled |
| Type errors | Use `state.model_copy()` not dict manipulation |
| Workflow stuck | Check conditional edge return values match edge map |
| State validation fails | Verify all required fields in nested states |
| Checkpoints not loading | Confirm PostgreSQL checkpoint table exists |

## Workflow Visualization

Generate workflow diagram:
```python
from app.workflow.builder import build_graph

graph = build_graph()
graph.get_graph().draw_png("workflow_diagram.png")
```

## Testing Workflow

```bash
# Run all workflow tests
pytest tests/workflow/ -v

# Test specific component
pytest tests/workflow/test_nodes.py::test_generate_jd_node -v

# With coverage
pytest tests/workflow/ --cov=app.workflow --cov-report=html
```

## Integration with FastAPI

```python
# In router.py
from app.workflow.engine import WorkflowEngine

@router.post("/jobs/create")
async def create_job(job_input: JobInput):
    # Initialize workflow
    engine = WorkflowEngine(
        job_id=new_job.id,
        thread_id=f"job-{new_job.id}"
    )
    
    # Run until first human checkpoint
    state = await engine.run_until_interrupt()
    
    return {"job_id": new_job.id, "status": state.current_node}

@router.post("/jobs/{job_id}/approve-jd")
async def approve_jd(job_id: str):
    # Resume workflow from checkpoint
    engine = WorkflowEngine(job_id=job_id, thread_id=f"job-{job_id}")
    
    state = await engine.resume_from_checkpoint(
        updates={"jd": {"approval_status": "APPROVED"}}
    )
    
    return {"status": state.current_node}
```

## Related Skills

- **[jd_optimization](../jd_optimization/SKILL.md)** - Understanding how optimized JDs are generated in `generate_jd_node`
- **[semantic_search](../semantic_search/SKILL.md)** - Shortlisting node uses Pinecone semantic search
- **[database_migrations](../database_migrations/SKILL.md)** - Updating GraphState schema requires migration strategy
- **[api_testing](../api_testing/SKILL.md)** - Testing workflow nodes and state transitions

---

## Resources

- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- OpenAI Model Docs: https://platform.openai.com/docs/models
- OpenAI Deprecations: https://platform.openai.com/docs/deprecations
- AARLP Workflow State: `app/workflow/state.py`
- Workflow Constants: `app/workflow/constants.py`
- Example Tests: `tests/workflow/`
