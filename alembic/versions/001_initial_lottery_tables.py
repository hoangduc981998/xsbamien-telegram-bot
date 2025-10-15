"""initial_lottery_tables

Revision ID: 001
Revises: 
Create Date: 2025-10-15 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lottery_results table
    op.create_table(
        'lottery_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('province_code', sa.String(length=20), nullable=False),
        sa.Column('province_name', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=10), nullable=False),
        sa.Column('draw_date', sa.Date(), nullable=False),
        sa.Column('prizes', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for lottery_results
    op.create_index('idx_province_date', 'lottery_results', ['province_code', 'draw_date'], unique=True)
    op.create_index('idx_region_date', 'lottery_results', ['region', 'draw_date'])
    op.create_index(
        'idx_draw_date_desc', 
        'lottery_results', 
        ['draw_date'], 
        postgresql_ops={'draw_date': 'DESC'}
    )
    op.create_index(op.f('ix_lottery_results_draw_date'), 'lottery_results', ['draw_date'], unique=False)
    op.create_index(op.f('ix_lottery_results_province_code'), 'lottery_results', ['province_code'], unique=False)
    op.create_index(op.f('ix_lottery_results_region'), 'lottery_results', ['region'], unique=False)
    
    # Create lo_2_so_history table
    op.create_table(
        'lo_2_so_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('lottery_result_id', sa.Integer(), nullable=False),
        sa.Column('province_code', sa.String(length=20), nullable=False),
        sa.Column('region', sa.String(length=10), nullable=False),
        sa.Column('draw_date', sa.Date(), nullable=False),
        sa.Column('number', sa.String(length=2), nullable=False),
        sa.Column('prize_type', sa.String(length=10), nullable=False),
        sa.Column('position', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for lo_2_so_history
    op.create_index(
        'idx_number_date', 
        'lo_2_so_history', 
        ['number', 'draw_date'], 
        postgresql_ops={'draw_date': 'DESC'}
    )
    op.create_index('idx_province_number_date', 'lo_2_so_history', ['province_code', 'number', 'draw_date'])
    op.create_index('idx_region_number_date', 'lo_2_so_history', ['region', 'number', 'draw_date'])
    op.create_index(
        'idx_draw_date_number', 
        'lo_2_so_history', 
        ['draw_date', 'number'], 
        postgresql_ops={'draw_date': 'DESC'}
    )
    op.create_index(op.f('ix_lo_2_so_history_draw_date'), 'lo_2_so_history', ['draw_date'], unique=False)
    op.create_index(op.f('ix_lo_2_so_history_lottery_result_id'), 'lo_2_so_history', ['lottery_result_id'], unique=False)
    op.create_index(op.f('ix_lo_2_so_history_number'), 'lo_2_so_history', ['number'], unique=False)
    op.create_index(op.f('ix_lo_2_so_history_province_code'), 'lo_2_so_history', ['province_code'], unique=False)
    op.create_index(op.f('ix_lo_2_so_history_region'), 'lo_2_so_history', ['region'], unique=False)


def downgrade() -> None:
    # Drop lo_2_so_history table
    op.drop_index(op.f('ix_lo_2_so_history_region'), table_name='lo_2_so_history')
    op.drop_index(op.f('ix_lo_2_so_history_province_code'), table_name='lo_2_so_history')
    op.drop_index(op.f('ix_lo_2_so_history_number'), table_name='lo_2_so_history')
    op.drop_index(op.f('ix_lo_2_so_history_lottery_result_id'), table_name='lo_2_so_history')
    op.drop_index(op.f('ix_lo_2_so_history_draw_date'), table_name='lo_2_so_history')
    op.drop_index('idx_draw_date_number', table_name='lo_2_so_history')
    op.drop_index('idx_region_number_date', table_name='lo_2_so_history')
    op.drop_index('idx_province_number_date', table_name='lo_2_so_history')
    op.drop_index('idx_number_date', table_name='lo_2_so_history')
    op.drop_table('lo_2_so_history')
    
    # Drop lottery_results table
    op.drop_index(op.f('ix_lottery_results_region'), table_name='lottery_results')
    op.drop_index(op.f('ix_lottery_results_province_code'), table_name='lottery_results')
    op.drop_index(op.f('ix_lottery_results_draw_date'), table_name='lottery_results')
    op.drop_index('idx_draw_date_desc', table_name='lottery_results')
    op.drop_index('idx_region_date', table_name='lottery_results')
    op.drop_index('idx_province_date', table_name='lottery_results')
    op.drop_table('lottery_results')
