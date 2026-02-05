---
name: semantic_search
description: Manage Pinecone vector operations for semantic candidate matching and job similarity
---

# Semantic Search & Vector Operations Skill

## Purpose
Manage Pinecone vector database operations for the AARLP platform. This skill covers embedding generation, vector upserts, semantic similarity search, and candidate ranking.

## AI Provider Support (Amazon Nova Hackathon)

AARLP supports multiple embedding providers:
- **AWS Bedrock (default)**: `amazon.titan-embed-text-v2:0` - 1024 dimensions
- **OpenAI (fallback)**: `text-embedding-3-small` - 1536 dimensions

Set via `AI_PROVIDER` environment variable.

## Secrets Management

**Required API Keys:**

| Secret | Provider | Purpose |
|--------|----------|---------|
| `PINECONE_API_KEY` | both | Vector database |
| `AWS_ACCESS_KEY_ID` | bedrock | Titan embeddings |
| `AWS_SECRET_ACCESS_KEY` | bedrock | Titan embeddings |
| `OPENAI_API_KEY` | openai | OpenAI embeddings |

**Configuration (app/core/config.py):**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AI Provider
    ai_provider: Literal["openai", "bedrock"] = "bedrock"
    
    # Pinecone
    pinecone_api_key: str
    pinecone_index: str = "aarlp-nova-candidates"
    
    # AWS Bedrock Embeddings
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_embedding_dimension: int = 1024
    
    # OpenAI Embeddings (Fallback)
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimension: int = 1536
```

**Dynamic Dimension Handling:**
```python
from app.ai.client import get_embedding_dimension

dimension = get_embedding_dimension()  # Returns 1024 or 1536 based on provider
```



## Overview

AARLP uses **Pinecone** for semantic search to match candidates with jobs beyond keyword matching. The system embeds both job descriptions and candidate resumes using OpenAI's `text-embedding-3-small` model.

## Architecture

```
app/ai/
├── client.py         # OpenAI client wrapper
├── embeddings.py     # Pinecone operations
└── jd_generator.py   # Uses embeddings for job matching
```

## Core Operations

### 1. Initialize Pinecone

```python
from app.ai.embeddings import get_pinecone_index

# Get configured index
index = get_pinecone_index()

# Index info
print(f"Dimension: {index.describe_index_stats()['dimension']}")
print(f"Total vectors: {index.describe_index_stats()['total_vector_count']}")
```

### 2. Generate Embeddings

```python
from app.ai.embeddings import generate_embedding

# Embed job description
jd_text = "Senior Backend Engineer with FastAPI and Python expertise..."
jd_embedding = await generate_embedding(jd_text)

print(f"Embedding dimension: {len(jd_embedding)}")  # 1536 for text-embedding-3-small

# Embed candidate resume
resume_text = "5 years Python development, FastAPI, PostgreSQL..."
resume_embedding = await generate_embedding(resume_text)
```

### 3. Store Vectors (Upsert)

```python
from app.ai.embeddings import upsert_job_embedding, upsert_candidate_embedding

# Store job vector
await upsert_job_embedding(
    job_id="job-123",
    embedding=jd_embedding,
    metadata={
        "title": "Senior Backend Engineer",
        "company": "TechCorp",
        "location": "San Francisco",
        "experience_level": "SENIOR",
        "skills": ["Python", "FastAPI", "PostgreSQL"]
    }
)

# Store candidate vector
await upsert_candidate_embedding(
    candidate_id="cand-456",
    job_id="job-123",
    embedding=resume_embedding,
    metadata={
        "name": "John Doe",
        "experience_years": 5,
        "skills": ["Python", "FastAPI", "Django"],
        "email": "john@example.com"
    }
)
```

### 4. Semantic Search (Query)

```python
from app.ai.embeddings import search_similar_candidates, search_similar_jobs

# Find candidates similar to job
results = await search_similar_candidates(
    job_embedding=jd_embedding,
    job_id="job-123",
    top_k=10  # Top 10 matches
)

for match in results:
    print(f"Candidate: {match['metadata']['name']}")
    print(f"Similarity Score: {match['score']:.2f}")  # 0.0 to 1.0
    print(f"Skills: {match['metadata']['skills']}")
    print("---")
```

## Candidate Ranking Algorithm

### Semantic + Attribute Scoring

```python
from app.candidates.services import rank_candidates

async def rank_candidates(job_id: str, candidates: List[Candidate]) -> List[RankedCandidate]:
    """
    Hybrid ranking: Semantic similarity + attribute matching.
    """
    # Get job embedding
    job = await get_job(job_id)
    job_embedding = await generate_embedding(job.jd_content)
    
    ranked = []
    for candidate in candidates:
        # 1. Semantic similarity (60% weight)
        resume_embedding = await generate_embedding(candidate.resume_text)
        similarity = await calculate_similarity(job_embedding, resume_embedding)
        semantic_score = similarity * 0.6
        
        # 2. Experience match (20% weight)
        exp_score = calculate_experience_score(job, candidate) * 0.2
        
        # 3. Skills match (20% weight)
        skills_score = calculate_skills_overlap(job, candidate) * 0.2
        
        # Total score
        total_score = semantic_score + exp_score + skills_score
        
        ranked.append(RankedCandidate(
            candidate=candidate,
            total_score=total_score,
            semantic_score=similarity,
            breakdown={
                "semantic": semantic_score,
                "experience": exp_score,
                "skills": skills_score
            }
        ))
    
    # Sort by total score descending
    return sorted(ranked, key=lambda x: x.total_score, reverse=True)
```

### Experience Matching

```python
def calculate_experience_score(job: Job, candidate: Candidate) -> float:
    """
    Match candidate experience to job requirements.
    Returns score from 0.0 to 1.0.
    """
    required_years = job.required_experience_years
    candidate_years = candidate.total_experience_years
    
    if candidate_years < required_years:
        # Penalty for under-qualified
        return max(0.0, candidate_years / required_years)
    elif candidate_years <= required_years + 3:
        # Perfect range
        return 1.0
    else:
        # Slight penalty for over-qualified
        return max(0.7, 1.0 - ((candidate_years - required_years - 3) * 0.05))
```

### Skills Overlap

```python
def calculate_skills_overlap(job: Job, candidate: Candidate) -> float:
    """
    Calculate Jaccard similarity of skills.
    """
    job_skills = set(skill.lower() for skill in job.required_skills)
    candidate_skills = set(skill.lower() for skill in candidate.skills)
    
    if not job_skills:
        return 1.0  # No requirements = perfect match
    
    intersection = job_skills & candidate_skills
    union = job_skills | candidate_skills
    
    return len(intersection) / len(union)  # Jaccard index
```

## Best Practices

### 1. Chunking Long Texts

For very long resumes or JDs:

```python
def chunk_text(text: str, max_tokens: int = 8000) -> List[str]:
    """
    Split text into chunks that fit embedding model limits.
    OpenAI's text-embedding-3-small supports 8191 tokens.
    """
    import tiktoken
    
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = encoding.encode(text)
    
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))
    
    return chunks

async def embed_long_document(text: str) -> List[float]:
    """
    Average embeddings of chunks for long documents.
    """
    chunks = chunk_text(text)
    embeddings = []
    
    for chunk in chunks:
        embedding = await generate_embedding(chunk)
        embeddings.append(embedding)
    
    # Average the embeddings
    import numpy as np
    return np.mean(embeddings, axis=0).tolist()
```

### 2. Batch Operations

```python
async def upsert_candidates_batch(candidates: List[Candidate], job_id: str):
    """
    Batch upsert for better performance.
    """
    from app.ai.embeddings import get_pinecone_index
    
    index = get_pinecone_index()
    
    vectors = []
    for candidate in candidates:
        embedding = await generate_embedding(candidate.resume_text)
        vectors.append({
            "id": f"candidate-{candidate.id}",
            "values": embedding,
            "metadata": {
                "job_id": job_id,
                "name": candidate.name,
                "email": candidate.email,
                "skills": candidate.skills
            }
        })
    
    # Upsert in batches of 100 (Pinecone limit)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace="candidates")
```

### 3. Filtering with Metadata

```python
async def search_candidates_with_filters(
    job_embedding: List[float],
    min_experience: int = 0,
    location: Optional[str] = None,
    top_k: int = 10
):
    """
    Semantic search with metadata filters.
    """
    index = get_pinecone_index()
    
    # Build filter
    filter_dict = {}
    if min_experience > 0:
        filter_dict["experience_years"] = {"$gte": min_experience}
    if location:
        filter_dict["location"] = location
    
    results = index.query(
        vector=job_embedding,
        top_k=top_k,
        filter=filter_dict if filter_dict else None,
        include_metadata=True,
        namespace="candidates"
    )
    
    return results.matches
```

## Pinecone Index Management

### Create Index (One-Time Setup)

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-api-key")

# Create index for AARLP
pc.create_index(
    name="aarlp-embeddings",
    dimension=1536,  # text-embedding-3-small dimension
    metric="cosine",  # Cosine similarity
    spec=ServerlessSpec(
        cloud="aws",
        region="us-west-2"
    )
)
```

### Index Stats

```python
index = get_pinecone_index()
stats = index.describe_index_stats()

print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")
```

### Delete Vectors

```python
# Delete specific candidate
index.delete(ids=["candidate-123"], namespace="candidates")

# Delete all candidates for a job
index.delete(filter={"job_id": "job-123"}, namespace="candidates")

# Delete entire namespace
index.delete(delete_all=True, namespace="candidates")
```

## Optimization Techniques

### 1. Caching Embeddings

```python
# Redis-backed embedding cache (correct approach for async)
import redis
import json
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def generate_embedding_cached(text: str) -> List[float]:
    """
    Redis-backed embedding cache for async functions.
    Caching reduces OpenAI API costs significantly for repeated texts.
    """
    # Generate cache key
    cache_key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Generate and cache
    embedding = await generate_embedding(text)
    redis_client.setex(cache_key, 86400, json.dumps(embedding))  # 24h TTL
    
    return embedding

# Alternative: Store embeddings in PostgreSQL
from app.core.database import get_db

async def get_or_create_embedding(text: str, db) -> List[float]:
    """
    Store embeddings in DB to avoid regenerating.
    Useful for frequently searched job requirements.
    """
    # Check if embedding exists
    result = await db.execute(
        "SELECT embedding FROM cached_embeddings WHERE text_hash = :hash",
        {"hash": hashlib.md5(text.encode()).hexdigest()}
    )
    row = result.fetchone()
    
    if row:
        return json.loads(row[0])
    
    # Generate new embedding
    embedding = await generate_embedding(text)
    
    # Store in DB
    await db.execute(
        "INSERT INTO cached_embeddings (text_hash, embedding, created_at) VALUES (:hash, :emb, NOW())",
        {"hash": hashlib.md5(text.encode()).hexdigest(), "emb": json.dumps(embedding)}
    )
    
    return embedding
```

### 2. Approximate Nearest Neighbors

For very large datasets, use Pinecone's pod-based indexes with HNSW:

```python
# Pod-based index (for production scale)
pc.create_index(
    name="aarlp-embeddings-prod",
    dimension=1536,
    metric="cosine",
    spec=PodSpec(
        environment="us-west1-gcp",
        pod_type="p1.x1",  # Performance optimized
        pods=2,
        replicas=1
    )
)
```

## Testing Semantic Search

```python
# tests/test_semantic_search.py
import pytest

@pytest.mark.asyncio
async def test_similar_candidates_ranking():
    """Test that candidates are ranked by similarity."""
    job_text = "Python developer with FastAPI experience"
    
    candidates = [
        {"id": "1", "resume": "Python FastAPI PostgreSQL 5 years"},
        {"id": "2", "resume": "Java Spring Boot 3 years"},
        {"id": "3", "resume": "Python Django Flask 4 years"}
    ]
    
    # Generate embeddings
    job_embedding = await generate_embedding(job_text)
    
    scores = []
    for candidate in candidates:
        cand_embedding = await generate_embedding(candidate["resume"])
        similarity = cosine_similarity(job_embedding, cand_embedding)
        scores.append((candidate["id"], similarity))
    
    # Verify ranking
    scores.sort(key=lambda x: x[1], reverse=True)
    assert scores[0][0] == "1"  # Best match: Python + FastAPI
    assert scores[1][0] == "3"  # Second: Python + similar frameworks
    assert scores[2][0] == "2"  # Last: Different language

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import numpy as np
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

## Monitoring & Analytics

### Track Embedding Costs

```python
import tiktoken

def estimate_embedding_cost(text: str) -> float:
    """
    Estimate OpenAI embedding API cost.
    text-embedding-3-small: $0.02 per 1M tokens
    """
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = len(encoding.encode(text))
    cost_per_token = 0.02 / 1_000_000
    return tokens * cost_per_token

# Log costs
total_cost = 0
for candidate in candidates:
    cost = estimate_embedding_cost(candidate.resume)
    total_cost += cost
    logger.info(f"Embedding cost for {candidate.id}: ${cost:.6f}")

logger.info(f"Total embedding cost: ${total_cost:.4f}")
```

### Monitor Search Performance

```python
import time

async def search_with_metrics(query_embedding, top_k=10):
    """
    Search with performance metrics.
    """
    start = time.time()
    results = await search_similar_candidates(query_embedding, top_k=top_k)
    duration = time.time() - start
    
    logger.info(f"Search completed in {duration:.3f}s for top_{top_k}")
    
    return results
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Dimension mismatch | Verify embedding model (1536 for text-embedding-3-small) |
| Low similarity scores | Normalize text, remove stopwords, ensure quality data |
| Slow queries | Use pod-based index, add metadata filters, reduce top_k |
| API rate limits | Implement exponential backoff, batch operations |
| High costs | Cache embeddings, deduplicate similar texts |

## Related Skills

- **[workflow_management](../workflow_management/SKILL.md)** - Candidate shortlisting triggers workflow state transitions
- **[database_migrations](../database_migrations/SKILL.md)** - Adding `semantic_score` column to candidates table requires coordinated Pinecone updates
- **[jd_optimization](../jd_optimization/SKILL.md)** - JD text quality directly affects embedding quality and match accuracy
- **[api_testing](../api_testing/SKILL.md)** - Testing semantic search endpoints and ranking algorithms

---

## Resources

- Pinecone Docs: https://docs.pinecone.io/
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- OpenAI Model Deprecations: https://platform.openai.com/docs/deprecations
- AARLP Embeddings: `app/ai/embeddings.py`
- Candidate Ranking: `app/candidates/services.py`
