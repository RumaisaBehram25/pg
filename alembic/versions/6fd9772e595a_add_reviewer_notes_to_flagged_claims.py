"""add_reviewer_notes_to_flagged_claims

Revision ID: 6fd9772e595a
Revises: a9fa0fde5213
Create Date: 2025-12-31 19:57:49.969528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fd9772e595a'
down_revision: Union[str, Sequence[str], None] = 'a9fa0fde5213'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('flagged_claims', 
        sa.Column('reviewer_notes', sa.Text(), nullable=True)
    )

def downgrade():
    op.drop_column('flagged_claims', 'reviewer_notes')