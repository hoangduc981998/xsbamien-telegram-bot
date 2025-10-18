"""Add user_subscriptions table

Revision ID: add_subscriptions
Revises: e9b97f837935
Create Date: 2025-10-18 07:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'add_subscriptions'
down_revision = 'e9b97f837935'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_subscriptions table
    op.create_table(
        'user_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('province_code', sa.String(10), nullable=False),
        sa.Column('notification_time', sa.String(5), nullable=True, comment='HH:MM format'),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    op.create_index('idx_user_subscriptions_province', 'user_subscriptions', ['province_code'])
    op.create_index('idx_user_subscriptions_active', 'user_subscriptions', ['is_active'])


def downgrade():
    op.drop_index('idx_user_subscriptions_active')
    op.drop_index('idx_user_subscriptions_province')
    op.drop_index('idx_user_subscriptions_user_id')
    op.drop_table('user_subscriptions')
