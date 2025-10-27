"""add messages table

Revision ID: add_messages
Revises: add_alerts_history
Create Date: 2025-01-25 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_messages'
down_revision = 'add_alerts_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('recipient_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('attachments', sa.JSON(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('read_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('ix_messages_recipient_id', 'messages', ['recipient_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_messages_created_at', 'messages')
    op.drop_index('ix_messages_recipient_id', 'messages')
    op.drop_index('ix_messages_sender_id', 'messages')
    op.drop_index('ix_messages_conversation_id', 'messages')
    op.drop_table('messages')