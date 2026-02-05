---
name: aws_bedrock_integration
description: Use AWS Bedrock with Nova models for JD generation, embeddings, and agentic workflows
---

# AWS Bedrock Integration Skill

## Purpose
Master AWS Bedrock integration with Nova models for the AARLP platform. This skill covers Bedrock client usage, Nova model invocation, embedding generation, and provider switching for the Amazon Nova AI Hackathon.

## Hackathon Context

**Amazon Nova AI Hackathon Entry:**
- **Category**: Agentic AI
- **Submission Deadline**: March 16, 2026
- **AWS Credits**: $100 available (request at https://challengepost.wufoo.com/forms/m1udy4ml0km7g62/)

## Provider Configuration

### Environment Variables (.env)
```bash
# AI Provider Selection ("openai" or "bedrock")
AI_PROVIDER=bedrock  # Set to "bedrock" for hackathon

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

# OpenAI (Fallback)
OPENAI_API_KEY=sk-...
```

### Switching Providers
```python
from app.ai.client import is_bedrock_provider, get_ai_provider

# Check current provider
provider = get_ai_provider()  # Returns "bedrock" or "openai"

if is_bedrock_provider():
    # Use Bedrock-specific logic
    from app.ai.bedrock_client import invoke_nova_model
    result = await invoke_nova_model(messages=[...])
else:
    # Use OpenAI
    from app.ai.client import get_openai_client
    client = get_openai_client()
```

## Nova Models Available

### Text Generation (via Bedrock)

| Model ID | Use Case | Tokens | Speed |
|----------|----------|--------|-------|
| `amazon.nova-lite-v1:0` | Fast JD generation | 300K | Fastest |
| `amazon.nova-pro-v1:0` | Complex reasoning | 300K | Fast |
| `amazon.nova-premier-v1:0` | Best quality | 1M | Slower |

### Embeddings

| Model ID | Dimensions | Use Case |
|----------|------------|----------|
| `amazon.titan-embed-text-v2:0` | 1024 | Text embeddings |
| `amazon.titan-embed-image-v1:0` | 1024 | Multimodal |

## Core Usage

### 1. Invoke Nova Model

```python
from app.ai.bedrock_client import invoke_nova_model

# Simple completion
result = await invoke_nova_model(
    messages=[{"role": "user", "content": "Generate a JD for a Python developer"}],
    system_prompt="You are an expert HR professional.",
    max_tokens=2048,
    temperature=0.7
)

print(result)  # Generated text
```

### 2. Generate Embeddings

```python
from app.ai.bedrock_client import generate_embedding

# Generate embedding vector
embedding = await generate_embedding("Senior Python Developer with FastAPI experience")

print(f"Dimension: {len(embedding)}")  # 1024 for Titan
```

### 3. JD Generation with Nova

```python
from app.ai.jd_generator import generate_job_description
from app.jobs.schemas import JobInput

job_input = JobInput(
    role_title="Senior Backend Engineer",
    company_name="TechCorp",
    experience_years=5,
    key_requirements=["Python", "FastAPI", "PostgreSQL"],
)

# Automatically uses Nova if AI_PROVIDER=bedrock
jd = await generate_job_description(job_input)

print(jd.job_title)
print(jd.description)
```

## Bedrock Client Architecture

### Files
```
app/ai/
├── client.py           # Provider abstraction (is_bedrock_provider)
├── bedrock_client.py   # Bedrock client factory, invoke functions
├── bedrock_utils.py    # Message formatting, response parsing
├── jd_generator.py     # JD generation (supports both providers)
└── embeddings.py       # Embeddings (supports both providers)
```

### Client Functions

```python
# app/ai/bedrock_client.py

# Get cached sync client
from app.ai.bedrock_client import get_bedrock_client
client = get_bedrock_client()

# Get async client (context manager)
from app.ai.bedrock_client import get_async_bedrock_client
async with get_async_bedrock_client() as client:
    response = await client.invoke_model(...)

# Test connection
from app.ai.bedrock_client import test_bedrock_connection
is_connected = await test_bedrock_connection()
```

### Message Formatting

```python
from app.ai.bedrock_utils import format_messages_for_bedrock

# OpenAI format -> Bedrock format
openai_messages = [{"role": "user", "content": "Hello"}]
bedrock_messages = format_messages_for_bedrock(openai_messages)
# Result: [{"role": "user", "content": [{"text": "Hello"}]}]
```

### Response Parsing

```python
from app.ai.bedrock_utils import parse_bedrock_response, parse_bedrock_json_response

# Extract text
text = parse_bedrock_response(response)

# Extract JSON (for JD generation)
data = parse_bedrock_json_response(response)  # Handles markdown wrapping
```

## Error Handling

```python
from app.ai.bedrock_utils import BedrockInvocationError

try:
    result = await invoke_nova_model(messages=[...])
except BedrockInvocationError as e:
    logger.error(f"Bedrock call failed: {e}")
    # Fallback to OpenAI if needed
```

## Embedding Dimension Differences

**IMPORTANT:** Nova/Titan embeddings use 1024 dimensions, OpenAI uses 1536.

```python
from app.ai.client import get_embedding_dimension

dimension = get_embedding_dimension()  # 1024 for Bedrock, 1536 for OpenAI
```

### Pinecone Index Considerations

When switching providers, you need a new Pinecone index:

```python
# In .env
PINECONE_INDEX=aarlp-candidates  # OpenAI (1536 dim)
PINECONE_INDEX_NOVA=aarlp-nova-candidates  # Nova (1024 dim)
```

## Testing Bedrock Integration

```bash
# Test JD generation
pytest tests/ai/test_jd_generator.py -v

# Test embeddings
pytest tests/ai/test_embeddings.py -v

# Manual test via API
# Start backend: uvicorn app.main:app --reload
# POST /jobs/create with job input
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `AccessDeniedException` | Enable model access in AWS Bedrock console |
| `ValidationException` | Check message format matches Nova's schema |
| `ThrottlingException` | Implement retry logic, reduce request rate |
| Embedding dimension mismatch | Create new Pinecone index for 1024 dimensions |

## Rollback to OpenAI

If Bedrock issues arise:

```bash
# In .env
AI_PROVIDER=openai
```

All code automatically falls back to OpenAI.

## Related Skills

- **[workflow_management](../workflow_management/SKILL.md)** - Workflows use Nova via JD generator
- **[jd_optimization](../jd_optimization/SKILL.md)** - JD generation uses Nova for text
- **[semantic_search](../semantic_search/SKILL.md)** - Embeddings use Titan via Bedrock

---

## Resources

- AWS Bedrock Docs: https://docs.aws.amazon.com/bedrock/
- Nova Developer Guide: https://nova.amazon.com/dev
- AARLP Bedrock Client: `app/ai/bedrock_client.py`
- Hackathon Page: https://amazon-nova.devpost.com
