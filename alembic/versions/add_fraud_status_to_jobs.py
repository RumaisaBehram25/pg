"""Add fraud status fields to ingestion_jobs

Revision ID: add_fraud_status
Revises: a1b2c3d4e5f6
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_fraud_status'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ingestion_jobs', sa.Column('fraud_status', sa.String(20), server_default='pending'))
    op.add_column('ingestion_jobs', sa.Column('fraud_flags_count', sa.Integer(), server_default='0'))
    op.add_column('ingestion_jobs', sa.Column('fraud_started_at', sa.DateTime(), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('fraud_completed_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('ingestion_jobs', 'fraud_completed_at')
    op.drop_column('ingestion_jobs', 'fraud_started_at')
    op.drop_column('ingestion_jobs', 'fraud_flags_count')
    op.drop_column('ingestion_jobs', 'fraud_status')





