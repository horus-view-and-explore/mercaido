# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.schema import MetaData

from mercaido_client.pb.mercaido import Service as ServiceMessage

from .types import ServiceMessageColumnType, TZDateTime


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })
    type_annotation_map = {
        ServiceMessage: ServiceMessageColumnType,
        datetime: TZDateTime,
    }
