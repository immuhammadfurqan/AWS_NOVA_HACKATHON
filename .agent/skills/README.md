# AARLP Skills Directory

This directory contains specialized skills that enhance AI assistant capabilities for the AARLP platform.

## Available Skills

### 1. **JD Optimization** (`jd_optimization/`)
Optimize AI-generated job descriptions for SEO, ATS compliance, and conversion.

**Use when:**
- Enhancing AI-generated JDs
- Preparing JDs for external job boards
- Improving application conversion rates
- Ensuring Google for Jobs compatibility

**Key features:**
- SEO optimization checklist
- ATS compliance validation
- Readability scoring
- Bias detection
- Industry-specific enhancements

---

### 2. **Workflow Management** (`workflow_management/`)
Master LangGraph workflows, state transitions, and checkpoint handling.

**Use when:**
- Adding new workflow nodes
- Debugging state transitions
- Implementing human-in-the-loop patterns
- Managing workflow checkpoints
- Testing workflow logic

**Key features:**
- Pydantic state management
- Node development patterns
- Conditional routing (edges)
- Checkpoint pause/resume
- Error handling strategies

---

### 3. **Database Migrations** (`database_migrations/`)
Safely create and deploy Alembic database migrations.

**Use when:**
- Modifying database schema
- Adding/removing columns
- Creating indexes
- Data migrations
- Rolling back changes

**Key features:**
- Auto-generation from models
- Manual migration patterns
- Testing strategies
- Rollback procedures
- Production deployment checklists

---

### 4. **API Testing** (`api_testing/`)
Comprehensive testing for FastAPI endpoints with pytest.

**Use when:**
- Writing unit tests
- Testing authentication flows
- Integration testing
- End-to-end workflow tests
- Performance testing

**Key features:**
- Test fixtures setup
- Auth testing patterns
- Async test support
- Mocking external services
- CI/CD integration

---

### 5. **Semantic Search** (`semantic_search/`)
Manage Pinecone vector operations for candidate matching.

**Use when:**
- Implementing semantic search
- Ranking candidates
- Working with embeddings
- Optimizing search performance
- Debugging similarity scores

**Key features:**
- Embedding generation
- Vector upsert/query
- Hybrid ranking algorithms
- Batch operations
- Metadata filtering

---

### 6. **Frontend Development** (`frontend_development/`)
Build Next.js 14 components with TypeScript and Tailwind.

**Use when:**
- Creating new UI components
- Implementing dark/light themes
- Optimizing frontend performance
- Building forms with validation
- Adding client-side interactivity

**Key features:**
- Server/Client component patterns
- Theme support (glassmorphism)
- TypeScript best practices
- Performance optimization
- State management

---

## How to Use Skills

When you need assistance with any of these areas, I'll automatically:
1. Read the relevant skill file
2. Apply the documented patterns and best practices
3. Follow the checklists and guidelines
4. Use the code examples as templates

## Adding New Skills

To create a new skill:

1. Create a folder: `.agent/skills/your_skill_name/`
2. Add `SKILL.md` with YAML frontmatter:
```markdown
---
name: your_skill_name
description: Brief description of what this skill does
---

# Skill Name

## Purpose
Detailed explanation...
```

3. (Optional) Add supporting files:
   - `scripts/` - Helper scripts
   - `examples/` - Reference code
   - `resources/` - Templates, configs

## Skill Structure

Each skill follows this format:

- **YAML Frontmatter**: Name and description
- **Purpose**: What the skill helps with
- **When to Use**: Specific scenarios
- **Patterns/Examples**: Code templates and best practices
- **Common Issues**: Troubleshooting guide
- **Resources**: Links to docs and AARLP files

## Platform-Specific Context

All skills are tailored for:
- **Backend**: FastAPI, SQLAlchemy, LangGraph, Pinecone
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Database**: PostgreSQL, Alembic migrations
- **AI**: OpenAI GPT-4, text-embedding-3-small
- **Architecture**: Clean Architecture, Domain-Driven Design

## Quick Reference

| Skill | Primary Files | Key Commands |
|-------|---------------|--------------|
| JD Optimization | `app/ai/jd_generator.py` | `POST /jobs/{id}/regenerate-jd` |
| Workflow | `app/workflow/` | `pytest tests/workflow/ -v` |
| Migrations | `alembic/versions/` | `alembic revision --autogenerate` |
| API Testing | `tests/` | `pytest tests/ --cov=app` |
| Semantic Search | `app/ai/embeddings.py` | Use Pinecone index methods |
| Frontend | `frontend/` | `npm run dev` |

## Contributing

To improve existing skills:
1. Update the relevant `SKILL.md` file
2. Add new patterns/examples based on real usage
3. Update troubleshooting sections with discovered issues
4. Keep code examples aligned with current codebase

---

**Last Updated**: 2026-02-03
**Total Skills**: 6
