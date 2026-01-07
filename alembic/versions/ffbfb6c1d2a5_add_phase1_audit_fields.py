"""add_phase1_audit_fields

Revision ID: ffbfb6c1d2a5
Revises: 6fd9772e595a
Create Date: 2026-01-06 20:25:56.418331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ffbfb6c1d2a5'
down_revision: Union[str, Sequence[str], None] = '6fd9772e595a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Add columns to claims
    op.add_column('claims', sa.Column('rx_number', sa.String(length=50), nullable=True))
    op.add_column('claims', sa.Column('fill_date', sa.Date(), nullable=True))
    op.add_column('claims', sa.Column('copay', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('claims', sa.Column('plan_paid', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('claims', sa.Column('paid_amount', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('claims', sa.Column('allowed_amount', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('claims', sa.Column('dispensing_fee', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('claims', sa.Column('ingredient_cost', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('claims', sa.Column('pharmacy_npi', sa.String(length=10), nullable=True))
    op.add_column('claims', sa.Column('prescriber_npi', sa.String(length=10), nullable=True))
    op.add_column('claims', sa.Column('pa_required', sa.Boolean(), nullable=True))
    op.add_column('claims', sa.Column('pa_reference', sa.String(length=100), nullable=True))
    op.add_column('claims', sa.Column('daw_code', sa.String(length=2), nullable=True))
    op.add_column('claims', sa.Column('reversal_indicator', sa.Boolean(), nullable=True))
    op.add_column('claims', sa.Column('reversal_reference', sa.String(length=100), nullable=True))
    op.add_column('claims', sa.Column('generic_available', sa.Boolean(), nullable=True))
    op.add_column('claims', sa.Column('drug_class', sa.String(length=100), nullable=True))
    
    # Add performance indexes to claims
    op.create_index('idx_claims_patient_drug', 'claims', ['tenant_id', 'patient_id', 'drug_code'])
    op.create_index('idx_claims_patient_drug_date', 'claims', ['tenant_id', 'patient_id', 'drug_code', 'fill_date'])
    op.create_index('idx_claims_fill_date', 'claims', ['tenant_id', 'fill_date'])
    op.create_index('idx_claims_pharmacy_npi', 'claims', ['tenant_id', 'pharmacy_npi'])
    op.create_index('idx_claims_prescriber_npi', 'claims', ['tenant_id', 'prescriber_npi'])
    op.create_index('idx_claims_rx_number', 'claims', ['tenant_id', 'rx_number'])
    
    # Add columns to rules
    op.add_column('rules', sa.Column('rule_code', sa.String(length=20), nullable=True))
    op.add_column('rules', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('rules', sa.Column('severity', sa.String(length=20), nullable=True))
    op.add_column('rules', sa.Column('recoupable', sa.Boolean(), nullable=True))
    op.add_column('rules', sa.Column('logic_type', sa.String(length=50), nullable=True))
    op.add_column('rules', sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    op.create_index('idx_rules_code', 'rules', ['tenant_id', 'rule_code'], unique=True)
    
    # Add columns to flagged_claims
    op.add_column('flagged_claims', sa.Column('run_id', sa.UUID(), nullable=True))
    op.add_column('flagged_claims', sa.Column('rule_code', sa.String(length=20), nullable=True))
    op.add_column('flagged_claims', sa.Column('severity', sa.String(length=20), nullable=True))
    op.add_column('flagged_claims', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('flagged_claims', sa.Column('evidence_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    op.create_index('idx_flagged_claims_run', 'flagged_claims', ['tenant_id', 'run_id'])
    
    # Create audit_rule_runs table
    op.create_table(
        'audit_rule_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('run_date', sa.DateTime(), nullable=False),
        sa.Column('rules_executed', sa.Integer(), server_default='0'),
        sa.Column('claims_processed', sa.Integer(), server_default='0'),
        sa.Column('flags_generated', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'])
    )
    
    op.create_index('idx_audit_runs_tenant', 'audit_rule_runs', ['tenant_id'])
    op.create_index('idx_audit_runs_job', 'audit_rule_runs', ['tenant_id', 'job_id'])
    
    # Enable RLS on audit_rule_runs
    op.execute("""
        ALTER TABLE audit_rule_runs ENABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS tenant_isolation_policy ON audit_rule_runs;
        CREATE POLICY tenant_isolation_policy ON audit_rule_runs FOR ALL 
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)
    
    # Create blocked_ndc table
    op.create_table(
        'blocked_ndc',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drug_code', sa.String(20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('blocked_date', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'])
    )
    
    op.create_index('idx_blocked_ndc_unique', 'blocked_ndc', ['tenant_id', 'drug_code'], unique=True)
    
    # Enable RLS on blocked_ndc
    op.execute("""
        ALTER TABLE blocked_ndc ENABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS tenant_isolation_policy ON blocked_ndc;
        CREATE POLICY tenant_isolation_policy ON blocked_ndc FOR ALL 
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)

def downgrade() -> None:
    """Downgrade schema."""
    # Drop new tables
    op.drop_table('blocked_ndc')
    op.drop_table('audit_rule_runs')
    
    # Drop flagged_claims columns
    op.drop_column('flagged_claims', 'evidence_json')
    op.drop_column('flagged_claims', 'category')
    op.drop_column('flagged_claims', 'severity')
    op.drop_column('flagged_claims', 'rule_code')
    op.drop_column('flagged_claims', 'run_id')
    
    # Drop rules columns
    op.drop_column('rules', 'parameters')
    op.drop_column('rules', 'logic_type')
    op.drop_column('rules', 'recoupable')
    op.drop_column('rules', 'severity')
    op.drop_column('rules', 'category')
    op.drop_column('rules', 'rule_code')
    
    # Drop claims columns
    op.drop_column('claims', 'drug_class')
    op.drop_column('claims', 'generic_available')
    op.drop_column('claims', 'reversal_reference')
    op.drop_column('claims', 'reversal_indicator')
    op.drop_column('claims', 'daw_code')
    op.drop_column('claims', 'pa_reference')
    op.drop_column('claims', 'pa_required')
    op.drop_column('claims', 'prescriber_npi')
    op.drop_column('claims', 'pharmacy_npi')
    op.drop_column('claims', 'ingredient_cost')
    op.drop_column('claims', 'dispensing_fee')
    op.drop_column('claims', 'allowed_amount')
    op.drop_column('claims', 'paid_amount')
    op.drop_column('claims', 'plan_paid')
    op.drop_column('claims', 'copay')
    op.drop_column('claims', 'fill_date')
    op.drop_column('claims', 'rx_number')