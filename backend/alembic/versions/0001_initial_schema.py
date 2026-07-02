"""initial workflowops schema
Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-02
"""
from __future__ import annotations
revision='0001_initial_schema'
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    from alembic import op
    from app.db.models import Base
    Base.metadata.create_all(bind=op.get_bind())
def downgrade():
    from alembic import op
    from app.db.models import Base
    Base.metadata.drop_all(bind=op.get_bind())
