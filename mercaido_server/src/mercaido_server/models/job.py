# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from typing import Any

from sqlalchemy import Text, JSON, String
from sqlalchemy.orm import mapped_column, Mapped

from uuid import uuid4
from proquint import convert

from .meta import Base


def readable_id():
    job_id = uuid4().hex
    chunks = [convert(job_id[i : i + 8]) for i in range(0, len(job_id), 8)]
    return "-".join(chunks)


class Job(Base):
    __tablename__: str = "jobs"
    id: Mapped[str] = mapped_column(
        String(47), init=False, primary_key=True, default=lambda: readable_id()
    )
    service_id: Mapped[str]
    attributes: Mapped[dict] = mapped_column(JSON(), insert_default=None)
    started_at: Mapped[datetime] = mapped_column(insert_default=None)
    finished_at: Mapped[datetime] = mapped_column(insert_default=None)
    error: Mapped[bool] = mapped_column(insert_default=False)
    error_msg: Mapped[str] = mapped_column(Text(), insert_default=None)

    def as_dict(self) -> dict[str, Any]:
        return dict(
            id=self.id,
            service_id=self.service_id,
            attributes=self.attributes,
            started_at=self.started_at.isoformat()
            if self.started_at is not None
            else None,
            finished_at=self.finished_at.isoformat()
            if self.finished_at is not None
            else None,
            error=self.error,
            error_msg=self.error_msg,
        )
