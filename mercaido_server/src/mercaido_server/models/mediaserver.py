# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from sqlalchemy.orm import mapped_column, Mapped

from .meta import Base


class MediaServer(Base):
    __tablename__: str = "media_servers"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    endpoint: Mapped[str] = mapped_column(unique=False, nullable=False, default=None)
