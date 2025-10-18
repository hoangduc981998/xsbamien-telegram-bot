"""Add notification_log table

Revision ID: add_notification_log
Revises: add_subscriptions
Create Date: 2025-10-18 08:20:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_notification_log'
down_revision = 'add_subscriptions'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_log table
    op.create_table(
        'notification_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('province_code', sa.String(10), nullable=False),
        sa.Column('result_date', sa.Date(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('total_sent', sa.Integer(), default=0),
        sa.Column('success_count', sa.Integer(), default=0),
        sa.Column('failed_count', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unique index to prevent duplicate sends
    op.create_index(
        'idx_notification_unique',
        'notification_log',
        ['province_code', 'result_date'],
        unique=True
    )


def downgrade():
    op.drop_index('idx_notification_unique')
    op.drop_table('notification_log')
