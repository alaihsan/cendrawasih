"""Add quiz models

Revision ID: 0cbea75fddf3
Revises: 2cff31e550b4
Create Date: 2026-03-12 10:45:15.123456

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0cbea75fddf3'
down_revision = '2cff31e550b4'
branch_labels = None
depends_on = None


def upgrade():
    # Create quiz_question table
    op.create_table('quiz_question',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lesson.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create quiz_option table
    op.create_table('quiz_option',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('option_text', sa.String(length=255), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['quiz_question.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create quiz_attempt table
    op.create_table('quiz_attempt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lesson.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('quiz_attempt')
    op.drop_table('quiz_option')
    op.drop_table('quiz_question')
