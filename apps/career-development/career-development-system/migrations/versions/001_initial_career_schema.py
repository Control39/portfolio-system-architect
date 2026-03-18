"""Initial career schema migration

Revision ID: 001
Revises: 
Create Date: 2024-10-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tables from postgres/init/01-career-schema.sql
    op.execute("""
    CREATE TABLE IF NOT EXISTS competency_markers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
        evidence_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """)
    
    op.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL,
        level INTEGER NOT NULL CHECK (level BETWEEN 0 AND 5) DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """)
    
    # Indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_markers_status ON competency_markers(status);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS competency_markers CASCADE;")
    op.execute("DROP TABLE IF EXISTS skills CASCADE;")

