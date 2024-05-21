# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

"""Add attributes to job

Revision ID: e47930380209
Revises: af2d025ce718
Create Date: 2023-09-08 13:43:52.389621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e47930380209"
down_revision = "af2d025ce718"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("attributes", sa.JSON(), nullable=False))


def downgrade() -> None:
    op.drop_column("jobs", "attributes")
