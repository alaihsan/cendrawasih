"""Add category field to courses

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    # Add category column to course table
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(50), nullable=False, server_default='General'))


def downgrade():
    # Remove category column from course table
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.drop_column('category')
