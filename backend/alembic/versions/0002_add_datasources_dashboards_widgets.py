from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_add_datasources_dashboards_widgets"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    datasource_type_enum = postgresql.ENUM("file", "postgresql", "mysql", "mongodb", "rest_api", name="datasourcetype")
    datasource_type_enum.create(op.get_bind(), checkfirst=True)
    
    widget_type_enum = postgresql.ENUM(
        "line_chart", "bar_chart", "pie_chart", "area_chart", "table", "heatmap", "metric", "text",
        name="widgettype"
    )
    widget_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create datasources table
    op.create_table(
        "datasources",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", datasource_type_enum, nullable=False),
        sa.Column("connection_config", sa.JSON(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("host", sa.String(), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("database_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("api_url", sa.String(), nullable=True),
        sa.Column("api_key", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create dashboards table
    op.create_table(
        "dashboards",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("layout_config", sa.JSON(), nullable=True),
        sa.Column("is_public", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_shared", sa.Boolean(), default=False, nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create dashboard_datasources association table
    op.create_table(
        "dashboard_datasources",
        sa.Column("dashboard_id", sa.Integer(), sa.ForeignKey("dashboards.id"), primary_key=True),
        sa.Column("datasource_id", sa.Integer(), sa.ForeignKey("datasources.id"), primary_key=True),
    )
    
    # Create widgets table
    op.create_table(
        "widgets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", widget_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("datasource_id", sa.Integer(), sa.ForeignKey("datasources.id"), nullable=True),
        sa.Column("position_x", sa.Integer(), default=0, nullable=False),
        sa.Column("position_y", sa.Integer(), default=0, nullable=False),
        sa.Column("width", sa.Integer(), default=4, nullable=False),
        sa.Column("height", sa.Integer(), default=3, nullable=False),
        sa.Column("dashboard_id", sa.Integer(), sa.ForeignKey("dashboards.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("widgets")
    op.drop_table("dashboard_datasources")
    op.drop_table("dashboards")
    op.drop_table("datasources")
    
    # Drop enum types
    sa.Enum(name="widgettype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="datasourcetype").drop(op.get_bind(), checkfirst=True)
