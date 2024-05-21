# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import ClassVar, TypeVar, Generic

from google.protobuf.message import Message as ProtobufMessage


P = TypeVar("P", bound="ProtobufMessage")


class Message(Generic[P]):
    obj: P
    TYPE: type[P]  # XXX: Can't declare this as ClassVar.

    def __repr__(self) -> str:
        return self.obj.__repr__()

    def serialize(self) -> bytes:
        return self.obj.SerializeToString()

    @classmethod
    def deserialize(cls: type[Message[P]], data: bytes) -> Message[P]:
        msg = cls.__new__(cls)
        msg.obj = cls.TYPE()
        msg.obj.ParseFromString(data)
        return msg

    @staticmethod
    def _from_pb(pb: P) -> Message[P]:
        msgtype = MessageRegistry.lookup(pb.__class__)
        msg = msgtype.__new__(msgtype)
        msg.obj = pb
        return msg


class MessageRegistry:
    _LOOKUP: ClassVar[dict[type[ProtobufMessage], type[Message]]] = {}

    @classmethod
    def register(cls, pb_type: type[ProtobufMessage], wrapper: type[Message]):
        cls._LOOKUP[pb_type] = wrapper

    @classmethod
    def lookup(cls, pb_type: type[ProtobufMessage]) -> type[Message]:
        return cls._LOOKUP[pb_type]
