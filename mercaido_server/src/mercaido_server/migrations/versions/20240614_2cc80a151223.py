"""Add api_url and name columns to FeatureServer model

Revision ID: 2cc80a151223
Revises: 230c147444f1
Create Date: 2024-06-14 15:24:27.716022

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2cc80a151223"
down_revision = "230c147444f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "feature_servers",
        sa.Column("name", sa.String(), nullable=False, server_default=""),
    )
    op.add_column("feature_servers", sa.Column("attributes", sa.JSON(), nullable=True))
    op.add_column(
        "feature_servers",
        sa.Column("server_type", sa.String(), nullable=False, server_default="generic"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("feature_servers", "server_type")
    op.drop_column("feature_servers", "api_endpoint")
    op.drop_column("feature_servers", "name")
    # ### end Alembic commands ###