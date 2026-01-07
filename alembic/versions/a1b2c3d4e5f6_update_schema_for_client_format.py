"""Update schema for client CSV format

Revision ID: a1b2c3d4e5f6
Revises: ffbfb6c1d2a5
Create Date: 2026-01-07 02:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ffbfb6c1d2a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename claim_number to claim_id to match client schema
    op.alter_column('claims', 'claim_number', new_column_name='claim_id')
    
    # Add new fields from client schema
    op.add_column('claims', sa.Column('usual_and_customary', sa.Numeric(10, 2), nullable=True))
    op.add_column('claims', sa.Column('plan_id', sa.String(100), nullable=True))
    op.add_column('claims', sa.Column('state', sa.String(2), nullable=True))
    op.add_column('claims', sa.Column('claim_status', sa.String(20), nullable=True))  # PAID or REVERSED
    op.add_column('claims', sa.Column('submitted_at', sa.DateTime, nullable=True))
    op.add_column('claims', sa.Column('reversal_date', sa.Date, nullable=True))
    
    # Rename drug_code to ndc to match client schema  
    op.alter_column('claims', 'drug_code', new_column_name='ndc')
    
    # Rename copay to copay_amount to match client schema
    op.alter_column('claims', 'copay', new_column_name='copay_amount')
    
    # Rename plan_paid to plan_paid_amount to match client schema
    op.alter_column('claims', 'plan_paid', new_column_name='plan_paid_amount')
    
    # Drop fields not in client schema (keeping for backwards compatibility, just nullable)
    # We're NOT dropping these columns since rules might reference them
    # Instead, we'll make sure the CSV parser handles the mapping
    
    # Update existing claim_status based on reversal_indicator
    op.execute("""
        UPDATE claims 
        SET claim_status = CASE 
            WHEN reversal_indicator = true THEN 'REVERSED' 
            ELSE 'PAID' 
        END
        WHERE claim_status IS NULL
    """)


def downgrade() -> None:
    # Rename back
    op.alter_column('claims', 'claim_id', new_column_name='claim_number')
    op.alter_column('claims', 'ndc', new_column_name='drug_code')
    op.alter_column('claims', 'copay_amount', new_column_name='copay')
    op.alter_column('claims', 'plan_paid_amount', new_column_name='plan_paid')
    
    # Drop new columns
    op.drop_column('claims', 'usual_and_customary')
    op.drop_column('claims', 'plan_id')
    op.drop_column('claims', 'state')
    op.drop_column('claims', 'claim_status')
    op.drop_column('claims', 'submitted_at')
    op.drop_column('claims', 'reversal_date')

