# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from datetime import timezone

from sqlalchemy.types import TypeDecorator, LargeBinary, DateTime

from mercaido_client.pb.message import Message
from mercaido_client.pb.mercaido import (
    MessageBase,
    Service as ServiceMessage,
)


class MessageMixin:
    message_type = Message  # placeholder

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, self.message_type):
                raise TypeError(f"expected {self.message_type}, but got {type(value)}")
            value = value.serialize()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = self.message_type.deserialize(value)
        return value


class ServiceMessageColumnType(MessageMixin, TypeDecorator):
    impl = LargeBinary
    cache_ok = True
    message_type = ServiceMessage


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value
