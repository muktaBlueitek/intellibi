from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_add_dashboard_sharing_versioning"
down_revision = "0002_add_datasources_dashboards_widgets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for share permissions
    share_permission_enum = postgresql.ENUM("view", "edit", "admin", name="sharepermission")
    share_permission_enum.create(op.get_bind(), checkfirst=True)
    
    # Add versioning columns to dashboards table
    op.add_column("dashboards", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("dashboards", sa.Column("current_version_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dashboards_current_version_id",
        "dashboards",
        "dashboard_versions",
        ["current_version_id"],
        ["id"]
    )
    
    # Create dashboard_shares table
    op.create_table(
        "dashboard_shares",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("dashboard_id", sa.Integer(), sa.ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("permission", share_permission_enum, nullable=False, server_default="view"),
        sa.Column("shared_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_dashboard_shares_dashboard_user", "dashboard_shares", ["dashboard_id", "user_id"], unique=True)
    
    # Create dashboard_versions table
    op.create_table(
        "dashboard_versions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("dashboard_id", sa.Integer(), sa.ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("version_number", sa.Integer(), nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("layout_config", sa.JSON(), nullable=True),
        sa.Column("widgets_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("comment", sa.Text(), nullable=True),
    )
    op.create_index("ix_dashboard_versions_dashboard_version", "dashboard_versions", ["dashboard_id", "version_number"], unique=True)


def downgrade() -> None:
    # Drop tables
    op.drop_table("dashboard_versions")
    op.drop_table("dashboard_shares")
    
    # Drop columns from dashboards
    op.drop_constraint("fk_dashboards_current_version_id", "dashboards", type_="foreignkey")
    op.drop_column("dashboards", "current_version_id")
    op.drop_column("dashboards", "version")
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS sharepermission")
