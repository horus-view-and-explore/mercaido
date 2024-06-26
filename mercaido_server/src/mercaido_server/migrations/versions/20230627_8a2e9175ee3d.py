# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

"""MediaServer and RecordingServer models

Revision ID: 8a2e9175ee3d
Revises: 
Create Date: 2023-06-27 12:22:17.112264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a2e9175ee3d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "media_servers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_servers")),
    )
    op.create_table(
        "recording_servers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host", sa.String(), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("database", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recording_servers")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("recording_servers")
    op.drop_table("media_servers")
    # ### end Alembic commands ###
