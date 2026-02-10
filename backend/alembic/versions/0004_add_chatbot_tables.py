from alembic import op
import sqlalchemy as sa


revision = "0004_add_chatbot_tables"
down_revision = "0003_add_dashboard_sharing_versioning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create chat_messages table
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create query_history table
    op.create_table(
        "query_history",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("sql_query", sa.Text(), nullable=True),
        sa.Column("datasource_id", sa.Integer(), sa.ForeignKey("datasources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("execution_time", sa.Float(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("success", sa.String(), nullable=False, server_default="true"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("query_history")
    op.drop_table("chat_messages")
    op.drop_table("conversations")
