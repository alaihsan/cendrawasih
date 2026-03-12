"""Add hls_path to lesson

Revision ID: 2cff31e550b4
Revises: c3d4e5f6a7b8
Create Date: 2026-03-12 10:22:42.385485

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2cff31e550b4'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lesson', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hls_path', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('lesson', schema=None) as batch_op:
        batch_op.drop_column('hls_path')
