---
name: api_testing
description: Test FastAPI endpoints with pytest, including auth, jobs, candidates, and workflow APIs
---

# API Testing Skill

## Purpose
Comprehensively test the AARLP FastAPI backend using pytest. This skill covers unit tests, integration tests, authentication flows, and end-to-end workflow testing.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication endpoints
├── test_jobs.py             # Job CRUD operations
├── test_candidates.py       # Candidate management
├── test_careers.py          # Public careers page
├── workflow/
│   ├── test_nodes.py        # Workflow node functions
│   ├── test_edges.py        # Conditional routing
│   └── test_state_validation.py
└── integration/
    └── test_full_workflow.py  # End-to-end tests
```

## Setup Test Environment

### conftest.py (Core Fixtures)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.config import get_settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/aarlp_test"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Provide clean database session for each test."""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for protected routes."""
    # Create test user
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
    client.post("/auth/register", json=user_data)
    
    # Verify OTP (mock)
    client.post("/auth/verify-otp", json={
        "email": "test@example.com",
        "otp": "123456"  # Use test OTP
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
```

## Testing Authentication

### test_auth.py

```python
import pytest

class TestRegistration:
    """Test user registration flow."""
    
    def test_register_success(self, client):
        """Successful registration returns 201."""
        response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # Never return password
        assert data["is_verified"] is False
    
    def test_register_duplicate_email(self, client):
        """Cannot register with existing email."""
        # First registration
        client.post("/auth/register", json={
            "email": "duplicate@example.com",
            "password": "Pass123!",
            "full_name": "User One"
        })
        
        # Second registration (should fail)
        response = client.post("/auth/register", json={
            "email": "duplicate@example.com",
            "password": "Pass456!",
            "full_name": "User Two"
        })
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Invalid email format rejected."""
        response = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "Pass123!",
            "full_name": "Test"
        })
        
        assert response.status_code == 422  # Pydantic validation error

class TestLogin:
    """Test authentication flow."""
    
    def test_login_success(self, client, test_db):
        """Successful login returns access token."""
        # Create and verify user first
        create_verified_user(client, "user@test.com", "Pass123!")
        
        response = client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "Pass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client):
        """Wrong password returns 401."""
        create_verified_user(client, "user@test.com", "CorrectPass")
        
        response = client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "WrongPass"
        })
        
        assert response.status_code == 401
    
    def test_login_unverified_user(self, client):
        """Unverified users cannot login."""
        # Register but don't verify
        client.post("/auth/register", json={
            "email": "unverified@test.com",
            "password": "Pass123!",
            "full_name": "Unverified"
        })
        
        response = client.post("/auth/login", json={
            "email": "unverified@test.com",
            "password": "Pass123!"
        })
        
        assert response.status_code == 403
        assert "not verified" in response.json()["detail"].lower()
```

## Testing Jobs API

### test_jobs.py

```python
import pytest

class TestJobCreation:
    """Test job creation and workflow initiation."""
    
    def test_create_job_success(self, client, auth_headers):
        """Successfully create job with AI generation."""
        response = client.post(
            "/jobs/create",
            headers=auth_headers,
            json={
                "title": "Senior Backend Engineer",
                "company_name": "TechCorp",
                "location": "San Francisco, CA",
                "employment_type": "FULL_TIME",
                "experience_level": "SENIOR"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Senior Backend Engineer"
        assert data["workflow_status"] == "GENERATE_JD"
    
    def test_create_job_unauthorized(self, client):
        """Cannot create job without auth."""
        response = client.post("/jobs/create", json={
            "title": "Engineer",
            "company_name": "Test"
        })
        
        assert response.status_code == 401

class TestJobRetrieval:
    """Test job listing and detail endpoints."""
    
    def test_list_jobs(self, client, auth_headers):
        """List all jobs for authenticated user."""
        # Create test jobs
        for i in range(3):
            client.post(
                "/jobs/create",
                headers=auth_headers,
                json={"title": f"Job {i}", "company_name": "Test"}
            )
        
        response = client.get("/jobs/", headers=auth_headers)
        
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) >= 3
    
    def test_get_job_detail(self, client, auth_headers):
        """Get specific job details."""
        # Create job
        create_response = client.post(
            "/jobs/create",
            headers=auth_headers,
            json={"title": "Test Job", "company_name": "Test"}
        )
        job_id = create_response.json()["id"]
        
        # Get details
        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["id"] == job_id
    
    def test_get_job_unauthorized(self, client, auth_headers):
        """Cannot view another user's job."""
        # Create user 2 and their job
        user2_headers = create_user_and_login(client, "user2@test.com")
        job_response = client.post(
            "/jobs/create",
            headers=user2_headers,
            json={"title": "Private Job", "company_name": "Test"}
        )
        job_id = job_response.json()["id"]
        
        # Try to access with user 1
        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        
        assert response.status_code == 404  # Not found (security)

class TestJobUpdate:
    """Test job modification endpoints."""
    
    def test_update_jd(self, client, auth_headers, test_db):
        """Update job description content."""
        job_id = create_test_job(client, auth_headers)
        
        response = client.put(
            f"/jobs/{job_id}/jd",
            headers=auth_headers,
            json={
                "content": "Updated JD content",
                "responsibilities": ["Task 1", "Task 2"],
                "requirements": {"required": ["Python"], "preferred": ["FastAPI"]}
            }
        )
        
        assert response.status_code == 200
        assert "Updated JD content" in response.json()["content"]
    
    def test_regenerate_jd_with_feedback(self, client, auth_headers):
        """Regenerate JD with recruiter feedback."""
        job_id = create_test_job(client, auth_headers)
        
        response = client.post(
            f"/jobs/{job_id}/regenerate-jd",
            headers=auth_headers,
            json={
                "feedback": "Add more focus on remote work and salary transparency"
            }
        )
        
        assert response.status_code == 200
        # Verify workflow triggered
        status = client.get(f"/jobs/{job_id}/status", headers=auth_headers)
        assert status.json()["current_node"] == "generate_jd"
```

## Testing Workflow Integration

### test_full_workflow.py

```python
import pytest
import asyncio
from app.workflow.engine import WorkflowEngine
from app.workflow.state import GraphState, JobDescriptionState, ApprovalStatus

@pytest.mark.asyncio
class TestWorkflowIntegration:
    """Test complete workflow execution."""
    
    async def test_jd_generation_flow(self, client, auth_headers):
        """Test JD generation and approval."""
        # 1. Create job (triggers workflow)
        response = client.post(
            "/jobs/create",
            headers=auth_headers,
            json={"title": "Engineer", "company_name": "Test"}
        )
        job_id = response.json()["id"]
        
        # 2. Wait for JD generation (poll status)
        await self._wait_for_node(client, auth_headers, job_id, "wait_jd_approval")
        
        # 3. Get generated JD
        jd_response = client.get(
            f"/jobs/{job_id}/jd",
            headers=auth_headers
        )
        assert jd_response.status_code == 200
        assert len(jd_response.json()["content"]) > 100  # Has content
        
        # 4. Approve JD
        approve_response = client.post(
            f"/jobs/{job_id}/approve-jd",
            headers=auth_headers
        )
        assert approve_response.status_code == 200
        
        # 5. Verify workflow progressed
        status = client.get(f"/jobs/{job_id}/status", headers=auth_headers)
        assert status.json()["current_node"] != "wait_jd_approval"
    
    async def test_candidate_shortlisting(self, client, auth_headers):
        """Test candidate ranking and shortlisting."""
        job_id = create_test_job(client, auth_headers)
        
        # Add mock candidates
        client.post(
            f"/jobs/{job_id}/mock/add-applicants",
            headers=auth_headers,
            json={"count": 10}
        )
        
        # Get candidates with scores
        response = client.get(
            f"/jobs/{job_id}/candidates",
            headers=auth_headers
        )
        
        candidates = response.json()
        assert len(candidates) == 10
        assert all("semantic_score" in c for c in candidates)
        # Verify sorted by score
        scores = [c["semantic_score"] for c in candidates]
        assert scores == sorted(scores, reverse=True)
    
    async def _wait_for_node(self, client, headers, job_id, target_node, timeout=30):
        """Poll job status until reaches target node."""
        for _ in range(timeout):
            response = client.get(f"/jobs/{job_id}/status", headers=headers)
            if response.json()["current_node"] == target_node:
                return
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Workflow did not reach {target_node}")
```

## Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async database operations."""
    from app.jobs.services import JobService
    
    service = JobService(db_session)
    job = await service.create_job(job_input)
    
    assert job.id is not None
```

## Mocking External Services

```python
from unittest.mock import patch, AsyncMock

@patch('app.ai.client.get_openai_client')
def test_jd_generation_mocked(mock_client, client, auth_headers):
    """Test JD generation with mocked OpenAI."""
    # Mock OpenAI response
    mock_client.return_value.chat.completions.create = AsyncMock(
        return_value=MockChatCompletion(
            choices=[MockChoice(
                message=MockMessage(content="Generated JD content")
            )]
        )
    )
    
    response = client.post("/jobs/create", headers=auth_headers, json={...})
    
    # Verify OpenAI was called
    mock_client.return_value.chat.completions.create.assert_called_once()
```

## Performance Testing

```python
import time

def test_list_jobs_performance(client, auth_headers):
    """Ensure job listing is fast with many jobs."""
    # Create 100 jobs
    for i in range(100):
        client.post("/jobs/create", headers=auth_headers, json={
            "title": f"Job {i}", "company_name": "Test"
        })
    
    # Time the query
    start = time.time()
    response = client.get("/jobs/?page=1&limit=50", headers=auth_headers)
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.5  # Should be under 500ms
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_jobs.py -v

# Specific test
pytest tests/test_jobs.py::TestJobCreation::test_create_job_success -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Parallel execution
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Only failed tests
pytest --lf

# Verbose output
pytest tests/ -vv
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: aarlp_test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

- [ ] Use fixtures for common setup (database, auth, test data)
- [ ] Mock external services (OpenAI, Pinecone, Twilio)
- [ ] Test both success and failure cases
- [ ] Test edge cases (empty data, invalid IDs, unauthorized access)
- [ ] Use parametrized tests for similar test cases
- [ ] Keep tests isolated (no shared state between tests)
- [ ] Clean database after each test
- [ ] Use meaningful test names (describe what is being tested)
- [ ] Assert specific values, not just status codes
- [ ] Test error messages content
- [ ] Verify database state changes
- [ ] Test async code properly with `pytest-asyncio`

---

## Related Skills

- **[workflow_management](../workflow_management/SKILL.md)** - Testing workflow nodes and state transitions end-to-end
- **[database_migrations](../database_migrations/SKILL.md)** - Use test database fixtures that match migration state
- **[semantic_search](../semantic_search/SKILL.md)** - Mock Pinecone queries in candidate ranking tests
- **[jd_optimization](../jd_optimization/SKILL.md)** - Test JD regeneration API flows

---

## Resources

- Pytest Docs: https://docs.pytest.org/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- AARLP Tests: `tests/`
- Fixtures: `tests/conftest.py`
