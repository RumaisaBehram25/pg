"""fix_email_uniqueness_per_tenant

Revision ID: a9fa0fde5213
Revises: 81e5759d6eeb
Create Date: 2025-12-25 20:27:48.776707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9fa0fde5213'
down_revision: Union[str, Sequence[str], None] = '81e5759d6eeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old unique constraint on email
    op.drop_constraint('users_email_key', 'users', type_='unique')
    
    # Create new composite unique constraint on (email, tenant_id)
    op.create_unique_constraint(
        'unique_email_per_tenant',
        'users',
        ['email', 'tenant_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the composite constraint
    op.drop_constraint('unique_email_per_tenant', 'users', type_='unique')
    
    # Restore the old constraint
    op.create_unique_constraint('users_email_key', 'users', ['email'])