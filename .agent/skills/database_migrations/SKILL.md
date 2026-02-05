---
name: database_migrations
description: Safely create, test, and deploy Alembic database migrations for AARLP
---

# Database Migration Management Skill

## Purpose
Handle all database schema changes for the AARLP platform using Alembic. This skill ensures safe, reversible migrations that work in development, staging, and production environments.

## Quick Reference

```bash
# Create new migration
alembic revision --autogenerate -m "Add column to jobs table"

# Review generated migration
# Edit: alembic/versions/xxxx_add_column_to_jobs_table.py

# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history --verbose
```

## Migration Workflow

### 1. Pre-Migration Checklist
- [ ] SQLAlchemy models updated in `app/*/models.py`
- [ ] Changes documented in migration message
- [ ] Backwards compatibility considered
- [ ] Data migration plan (if needed)
- [ ] Rollback strategy defined
- [ ] Staging environment available for testing

### 2. Creating Migrations

#### Auto-Generate from Models
```bash
# Alembic compares DB with SQLAlchemy models
alembic revision --autogenerate -m "descriptive_message"
```

**Example Messages:**
- `"Add status column to jobs table"`
- `"Create candidates table with FK to jobs"`
- `"Add index on job_id and created_at"`
- `"Rename column title to job_title"`

#### Manual Migration (Complex Changes)
```bash
alembic revision -m "migrate_data_from_old_to_new_format"
```

### 3. Review Generated Migration

**Always review auto-generated migrations!** Alembic may miss:
- Data migrations
- Index drops/creates
- Column renames (sees as drop + add)
- Constraint changes

```python
# alembic/versions/abc123_add_status.py

def upgrade() -> None:
    """
    ALWAYS review auto-generated code.
    Add data migrations if needed.
    """
    # Auto-generated
    op.add_column('jobs', sa.Column('status', sa.String(), nullable=True))
    
    # YOU MUST ADD: Set default value for existing rows
    op.execute("UPDATE jobs SET status = 'PENDING' WHERE status IS NULL")
    
    # Then make it non-nullable
    op.alter_column('jobs', 'status', nullable=False)


def downgrade() -> None:
    """
    CRITICAL: Always implement downgrade.
    Never use pass or raise NotImplementedError in production.
    """
    op.drop_column('jobs', 'status')
```

### 4. Testing Migrations

#### Local Testing
```bash
# 1. Backup your database
pg_dump aarlp > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Apply migration
alembic upgrade head

# 3. Verify schema
psql aarlp -c "\d jobs"

# 4. Test application
uvicorn app.main:app --reload
# Run tests
pytest tests/ -v

# 5. Test rollback
alembic downgrade -1

# 6. Verify data integrity
# Check that critical data is intact
```

#### Staging Testing
```bash
# On staging server
git pull origin main
alembic upgrade head
systemctl restart aarlp-api
# Monitor logs for errors
```

## Common Migration Patterns

### Pattern 1: Adding a Column

```python
def upgrade() -> None:
    # Add nullable first
    op.add_column('jobs', sa.Column('salary_range', sa.String(), nullable=True))
    
    # Populate existing rows with default
    op.execute("UPDATE jobs SET salary_range = 'Competitive' WHERE salary_range IS NULL")
    
    # Then make NOT NULL if needed
    op.alter_column('jobs', 'salary_range', nullable=False)

def downgrade() -> None:
    op.drop_column('jobs', 'salary_range')
```

### Pattern 2: Renaming a Column

```python
def upgrade() -> None:
    # Alembic sees rename as drop + add, which loses data!
    # Use alter_column instead
    op.alter_column('jobs', 'jd_content', new_column_name='description')

def downgrade() -> None:
    op.alter_column('jobs', 'description', new_column_name='jd_content')
```

### Pattern 3: Adding Foreign Key

```python
def upgrade() -> None:
    # 1. Add column first (nullable)
    op.add_column('candidates', sa.Column('job_id', sa.UUID(), nullable=True))
    
    # 2. Populate with data migration
    op.execute("""
        UPDATE candidates c
        SET job_id = (SELECT id FROM jobs WHERE jobs.id = c.job_id_temp)
    """)
    
    # 3. Make NOT NULL
    op.alter_column('candidates', 'job_id', nullable=False)
    
    # 4. Add foreign key constraint
    op.create_foreign_key(
        'fk_candidates_job_id',
        'candidates', 'jobs',
        ['job_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    op.drop_constraint('fk_candidates_job_id', 'candidates', type_='foreignkey')
    op.drop_column('candidates', 'job_id')
```

### Pattern 4: Adding Index

```python
def upgrade() -> None:
    # Add index for common query patterns
    op.create_index(
        'ix_jobs_status_created_at',
        'jobs',
        ['status', 'created_at'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_jobs_status_created_at', table_name='jobs')
```

### Pattern 5: Data Migration

```python
def upgrade() -> None:
    """Migrate data from old format to new format."""
    
    # Use op.execute for SQL
    op.execute("""
        UPDATE jobs
        SET requirements = jsonb_build_object(
            'required', requirements_old,
            'preferred', '{}'::jsonb
        )
        WHERE requirements_old IS NOT NULL
    """)
    
    # Or use ORM with bind
    from sqlalchemy.orm import Session
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Query and update
    jobs = session.execute("SELECT id, old_field FROM jobs").fetchall()
    for job_id, old_value in jobs:
        new_value = transform_value(old_value)
        session.execute(
            "UPDATE jobs SET new_field = :val WHERE id = :id",
            {"val": new_value, "id": job_id}
        )
    
    session.commit()

def downgrade() -> None:
    # Reverse data migration
    op.execute("""
        UPDATE jobs
        SET requirements_old = requirements->>'required'
        WHERE requirements IS NOT NULL
    """)
```

### Pattern 6: Enum Changes

```python
# ADDING enum value (safe in production)
def upgrade() -> None:
    # ALTER TYPE ADD VALUE cannot run in transaction block
    # Must commit first
    op.execute("COMMIT")
    op.execute("ALTER TYPE job_status ADD VALUE IF NOT EXISTS 'ARCHIVED'")

def downgrade() -> None:
    # Cannot simply remove enum values in PostgreSQL
    # See "Enum Removal Pattern" below for full approach
    pass  # Document in migration message why downgrade is no-op


# REMOVING enum value (complex - use this pattern)
def upgrade() -> None:
    """
    Remove 'DEPRECATED_STATUS' from job_status enum.
    
    Strategy:
    1. Create new enum without deprecated value
    2. Alter column to new enum type
    3. Drop old enum
    4. Rename new enum to original name
    """
    # 1. Create new enum type
    op.execute("""
        CREATE TYPE job_status_new AS ENUM (
            'PENDING', 'ACTIVE', 'ARCHIVED'
            -- Excluded: 'DEPRECATED_STATUS'
        )
    """)
    
    # 2. Migrate data (if any rows use deprecated value, update first)
    op.execute("""
        UPDATE jobs
        SET status = 'ARCHIVED'
        WHERE status = 'DEPRECATED_STATUS'
    """)
    
    # 3. Alter column to use new enum
    op.execute("""
        ALTER TABLE jobs
        ALTER COLUMN status TYPE job_status_new
        USING status::text::job_status_new
    """)
    
    # 4. Drop old enum and rename new one
    op.execute("DROP TYPE job_status")
    op.execute("ALTER TYPE job_status_new RENAME TO job_status")

def downgrade() -> None:
    """Reverse: Add back the removed enum value."""
    op.execute("COMMIT")
    op.execute("ALTER TYPE job_status ADD VALUE 'DEPRECATED_STATUS'")
    
    # Optionally restore data if you tracked which rows had it
    # (requires a migration_history table or similar)
```

## AARLP-Specific Patterns

### Jobs Table Changes

```python
# When modifying Job model (app/jobs/models.py)
from app.jobs.models import Job

def upgrade() -> None:
    # Example: Add workflow_status column
    op.add_column('jobs', 
        sa.Column('workflow_status', sa.String(), nullable=True)
    )
    
    # Default for existing jobs
    op.execute("UPDATE jobs SET workflow_status = 'PENDING'")
    op.alter_column('jobs', 'workflow_status', nullable=False)

def downgrade() -> None:
    op.drop_column('jobs', 'workflow_status')
```

### Candidates Table Changes

```python
def upgrade() -> None:
    # Add semantic match score
    op.add_column('candidates',
        sa.Column('semantic_score', sa.Float(), nullable=True)
    )
    
    # IMPORTANT: When adding semantic_score, also ensure
    # Pinecone index is updated to store scores
    # See semantic_search skill for coordinated updates
    
    # Create index for ranking queries
    op.create_index(
        'ix_candidates_job_id_semantic_score',
        'candidates',
        ['job_id', sa.text('semantic_score DESC')]
    )

def downgrade() -> None:
    # Before dropping column, consider:
    # 1. Backing up semantic score data
    # 2. Clearing Pinecone metadata that references scores
    op.drop_index('ix_candidates_job_id_semantic_score')
    op.drop_column('candidates', 'semantic_score')
```

## Production Deployment

### Pre-Deployment

1. **Review Migration**
   ```bash
   # Check SQL that will be run
   alembic upgrade head --sql
   ```

2. **Timing Considerations**
   - Large table alterations? Use `CONCURRENTLY` for indexes
   - Data migrations? Estimate duration on staging
   - Breaking changes? Plan downtime window

3. **Backup Strategy**
   ```bash
   # Full backup before migration
   pg_dump aarlp_production > backup_pre_migration_$(date +%Y%m%d).sql
   ```

### During Deployment

```bash
# 1. Put app in maintenance mode (optional)
# 2. Create backup
pg_dump aarlp_production > /backups/pre_migration.sql

# 3. Run migration
alembic upgrade head

# 4. Verify
alembic current
psql aarlp_production -c "\d+ jobs"  # Check schema

# 5. Restart application
systemctl restart aarlp-api

# 6. Monitor logs
journalctl -u aarlp-api -f

# 7. Quick smoke test
curl http://localhost:8000/health
```

### Rollback Plan

```bash
# IF migration fails:

# 1. Downgrade migration
alembic downgrade -1

# 2. Restore from backup (if needed)
psql aarlp_production < /backups/pre_migration.sql

# 3. Rollback code
git revert <commit>
git push

# 4. Restart application
systemctl restart aarlp-api
```

## Advanced Techniques

### Concurrent Index Creation (No Locks)

```python
def upgrade() -> None:
    # CREATE INDEX CONCURRENTLY cannot run in transaction
    from alembic import op
    
    op.execute("COMMIT")  # End transaction
    op.execute("""
        CREATE INDEX CONCURRENTLY ix_jobs_created_at 
        ON jobs (created_at)
    """)

def downgrade() -> None:
    op.execute("COMMIT")
    op.execute("DROP INDEX CONCURRENTLY ix_jobs_created_at")
```

### Multi-Step Migrations (Large Tables)

```python
# Step 1: Add column (nullable)
def upgrade() -> None:
    op.add_column('jobs', sa.Column('new_field', sa.String(), nullable=True))

# Step 2 (separate migration): Populate data
def upgrade() -> None:
    # Batch update to avoid locking entire table
    op.execute("""
        UPDATE jobs
        SET new_field = old_field
        WHERE new_field IS NULL
        LIMIT 10000
    """)
    # Run multiple times or in background job

# Step 3 (separate migration): Make NOT NULL
def upgrade() -> None:
    op.alter_column('jobs', 'new_field', nullable=False)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Target database is not up to date" | Run `alembic upgrade head` first |
| "Can't locate revision ABC" | Check `alembic_version` table, ensure all revisions exist |
| Migration auto-generates drop table | Review carefully! Likely model removed |
| Circular import in migration | Import models inside functions, not at module level |
| Enum change breaks | Use raw SQL with `op.execute()` |
| Foreign key constraint fails | Ensure referenced rows exist, use data migration |

## Testing Migrations

```python
# tests/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config

def test_migration_upgrade_downgrade():
    """Test that migrations are reversible."""
    config = Config("alembic.ini")
    
    # Upgrade
    command.upgrade(config, "head")
    
    # Downgrade
    command.downgrade(config, "-1")
    
    # Re-upgrade
    command.upgrade(config, "head")
```

## Best Practices Checklist

- [ ] Always review auto-generated migrations
- [ ] Implement proper `downgrade()` (never use `pass`)
- [ ] Add data migrations for existing rows
- [ ] Test on staging before production
- [ ] Backup database before migration
- [ ] Use descriptive migration messages
- [ ] Add indexes for new columns with queries
- [ ] Handle NULL values properly
- [ ] Consider performance on large tables
- [ ] Document breaking changes in migration

## Related Skills

- **[semantic_search](../semantic_search/SKILL.md)** - When adding `semantic_score` column, coordinate Pinecone index updates
- **[workflow_management](../workflow_management/SKILL.md)** - GraphState schema changes require checkpoint migration strategy
- **[api_testing](../api_testing/SKILL.md)** - Test migrations with data fixtures

---

## Resources

- Alembic Docs: https://alembic.sqlalchemy.org/
- PostgreSQL Enum Docs: https://www.postgresql.org/docs/current/datatype-enum.html
- AARLP Models: `app/*/models.py`
- Migration History: `alembic/versions/`
- Database Config: `app/core/database.py`
