# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped

from mercaido_client.pb.mercaido import Service as ServiceMessage

from .meta import Base


class Service(Base):
    __tablename__: str = "services"

    ident: Mapped[str] = mapped_column(primary_key=True)
    last_seen: Mapped[datetime] = mapped_column(insert_default=None)
    data: Mapped[ServiceMessage]
