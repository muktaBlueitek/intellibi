"""add performance indexes

Revision ID: 0005
Revises: 0004
Create Date: 2026-02-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    # Composite indexes for common query patterns
    
    # Dashboards: owner_id + updated_at for user dashboard lists
    op.create_index(
        'ix_dashboards_owner_updated',
        'dashboards',
        ['owner_id', 'updated_at'],
        unique=False
    )
    
    # Widgets: dashboard_id + created_at for widget ordering
    op.create_index(
        'ix_widgets_dashboard_created',
        'widgets',
        ['dashboard_id', 'created_at'],
        unique=False
    )
    
    # DataSources: owner_id + is_active for active datasource queries
    op.create_index(
        'ix_datasources_owner_active',
        'datasources',
        ['owner_id', 'is_active'],
        unique=False
    )
    
    # QueryHistory: user_id + created_at for user query history
    op.create_index(
        'ix_query_history_user_created',
        'query_history',
        ['user_id', 'created_at'],
        unique=False
    )
    
    # QueryHistory: datasource_id + success for datasource analytics
    op.create_index(
        'ix_query_history_datasource_success',
        'query_history',
        ['datasource_id', 'success'],
        unique=False
    )
    
    # Conversations: user_id + updated_at for conversation lists
    op.create_index(
        'ix_conversations_user_updated',
        'conversations',
        ['user_id', 'updated_at'],
        unique=False
    )
    
    # ChatMessages: conversation_id + created_at for message ordering
    op.create_index(
        'ix_chat_messages_conversation_created',
        'chat_messages',
        ['conversation_id', 'created_at'],
        unique=False
    )
    
    # DashboardShares: dashboard_id + user_id for access checks
    op.create_index(
        'ix_dashboard_shares_dashboard_user',
        'dashboard_shares',
        ['dashboard_id', 'user_id'],
        unique=False
    )


def downgrade():
    op.drop_index('ix_dashboard_shares_dashboard_user', table_name='dashboard_shares')
    op.drop_index('ix_chat_messages_conversation_created', table_name='chat_messages')
    op.drop_index('ix_conversations_user_updated', table_name='conversations')
    op.drop_index('ix_query_history_datasource_success', table_name='query_history')
    op.drop_index('ix_query_history_user_created', table_name='query_history')
    op.drop_index('ix_datasources_owner_active', table_name='datasources')
    op.drop_index('ix_widgets_dashboard_created', table_name='widgets')
    op.drop_index('ix_dashboards_owner_updated', table_name='dashboards')
