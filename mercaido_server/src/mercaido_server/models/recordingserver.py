# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from sqlalchemy.orm import mapped_column, Mapped

from .meta import Base


class RecordingServer(Base):
    __tablename__: str = "recording_servers"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    host: Mapped[str] = mapped_column(nullable=False, default=None)
    port: Mapped[int] = mapped_column(nullable=False, default=5432)
    database: Mapped[str] = mapped_column(nullable=False, default=None)
    username: Mapped[str] = mapped_column(nullable=False, default=None)
    password: Mapped[str] = mapped_column(nullable=False, default=None)

    @property
    def connection_string(self):
        return f"host={self.host} port={self.port} dbname={self.database} user={self.username} password={self.password}"
