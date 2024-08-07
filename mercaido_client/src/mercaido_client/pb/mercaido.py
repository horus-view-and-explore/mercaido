# Generated by mercaido_client/scripts/pbgen.py.  DO NOT EDIT!
# Any modifications will be lost when this script is rerun.

from __future__ import annotations

from typing import Optional, cast
from enum import IntEnum
from itertools import islice
import mercaido_client.pb.mercaido_pb2
from .message import (
    Message,
    MessageRegistry,
)


class MessageType(IntEnum):
    MESSAGE_TYPE_UNSPECIFIED = 0
    MESSAGE_TYPE_EVENT = 2
    MESSAGE_TYPE_REGISTER_SERVICES = 3
    MESSAGE_TYPE_PUBLISH_JOB = 4


class AttributeType(IntEnum):
    ATTRIBUTE_TYPE_UNSPECIFIED = 0
    ATTRIBUTE_TYPE_TEXT = 1
    ATTRIBUTE_TYPE_FILE = 2
    ATTRIBUTE_TYPE_FOLDER = 3
    ATTRIBUTE_TYPE_SELECTION = 4
    ATTRIBUTE_TYPE_RECORDING_ID = 5
    ATTRIBUTE_TYPE_RECORDINGS_SERVER_CONNECTION = 6
    ATTRIBUTE_TYPE_MEDIA_SERVER_CONNECTION = 7
    ATTRIBUTE_TYPE_NUMBER = 8
    ATTRIBUTE_TYPE_BOOLEAN = 9
    ATTRIBUTE_TYPE_FEATURESERVER = 10


class EventType(IntEnum):
    EVENT_TYPE_UNSPECIFIED = 0
    EVENT_TYPE_JOB_START = 1
    EVENT_TYPE_JOB_STOP = 2
    EVENT_TYPE_JOB_ERROR = 3
    EVENT_TYPE_JOB_PROGRESS = 4


class Attribute(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.Attribute  # type: ignore[attr-defined]

    def __init__(
        self,
        *,
        values: Optional[list[str]] = None,
        type: AttributeType,
        sensitive: Optional[bool] = None,
        id: Optional[str] = None,
        display_description: Optional[str] = None,
        display_name: Optional[str] = None,
    ):
        self.obj = self.TYPE()
        if values is not None:
            self.obj.values[:] = values
        self.obj.type = type
        if sensitive is not None:
            self.obj.sensitive = sensitive
        if id is not None:
            self.obj.id = id
        if display_description is not None:
            self.obj.display_description = display_description
        if display_name is not None:
            self.obj.display_name = display_name

    @property
    def values(self) -> list[str]:
        return self.obj.values

    @values.setter
    def values(self, value: list[str]):
        self.obj.values[:] = value

    @values.deleter
    def values(self) -> None:
        self.obj.ClearField("values")

    def values_as_dict(self) -> dict[str, str]:
        if len(self.values) == 0:
            return {}
        elif len(self.values) % 2 != 0:
            raise ValueError(
                "Field `Attribute.values` should contain an even amount of items representing alternating keys and values"
            )

        def _it_to_tuples(it):
            while pair := tuple(islice(it, 2)):
                yield pair

        iterator = iter(self.values)
        return dict([pair for pair in _it_to_tuples(iterator)])

    @property
    def type(self) -> AttributeType:
        return self.obj.type

    @type.setter
    def type(self, value: AttributeType):
        self.obj.type = value

    @type.deleter
    def type(self) -> None:
        self.obj.ClearField("type")

    @property
    def sensitive(self) -> bool:
        return self.obj.sensitive

    @sensitive.setter
    def sensitive(self, value: bool):
        self.obj.sensitive = value

    @sensitive.deleter
    def sensitive(self) -> None:
        self.obj.ClearField("sensitive")

    @property
    def id(self) -> str:
        return self.obj.id

    @id.setter
    def id(self, value: str):
        self.obj.id = value

    @id.deleter
    def id(self) -> None:
        self.obj.ClearField("id")

    @property
    def display_description(self) -> str:
        return self.obj.display_description

    @display_description.setter
    def display_description(self, value: str):
        self.obj.display_description = value

    @display_description.deleter
    def display_description(self) -> None:
        self.obj.ClearField("display_description")

    @property
    def display_name(self) -> str:
        return self.obj.display_name

    @display_name.setter
    def display_name(self, value: str):
        self.obj.display_name = value

    @display_name.deleter
    def display_name(self) -> None:
        self.obj.ClearField("display_name")


class Event(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.Event  # type: ignore[attr-defined]

    def __init__(
        self,
        *,
        type: EventType,
        error_message: Optional[str] = None,
        progress: Optional[float] = None,
        job_id: Optional[str] = None,
    ):
        self.obj = self.TYPE()
        self.obj.type = type
        if error_message is not None:
            self.obj.error_message = error_message
        if progress is not None:
            self.obj.progress = progress
        if job_id is not None:
            self.obj.job_id = job_id

    @property
    def type(self) -> EventType:
        return self.obj.type

    @type.setter
    def type(self, value: EventType):
        self.obj.type = value

    @type.deleter
    def type(self) -> None:
        self.obj.ClearField("type")

    @property
    def error_message(self) -> str:
        return self.obj.error_message

    @error_message.setter
    def error_message(self, value: str):
        self.obj.error_message = value

    @error_message.deleter
    def error_message(self) -> None:
        self.obj.ClearField("error_message")

    @property
    def progress(self) -> float:
        return self.obj.progress

    @progress.setter
    def progress(self, value: float):
        self.obj.progress = value

    @progress.deleter
    def progress(self) -> None:
        self.obj.ClearField("progress")

    @property
    def job_id(self) -> str:
        return self.obj.job_id

    @job_id.setter
    def job_id(self, value: str):
        self.obj.job_id = value

    @job_id.deleter
    def job_id(self) -> None:
        self.obj.ClearField("job_id")


class MessageBase(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.MessageBase  # type: ignore[attr-defined]

    def __init__(
        self,
        *,
        response: Optional[ResponseBase] = None,
        request: Optional[RequestBase] = None,
        recipient: Optional[str] = None,
    ):
        self.obj = self.TYPE()
        if response is not None:
            self.obj.response.CopyFrom(response.obj)
        if request is not None:
            self.obj.request.CopyFrom(request.obj)
        if recipient is not None:
            self.obj.recipient = recipient

    @property
    def response(self) -> ResponseBase:
        return cast(ResponseBase, self._from_pb(self.obj.response))

    @response.setter
    def response(self, value: ResponseBase):
        self.obj.response.CopyFrom(value.obj)

    @response.deleter
    def response(self) -> None:
        self.obj.ClearField("response")

    @property
    def request(self) -> RequestBase:
        return cast(RequestBase, self._from_pb(self.obj.request))

    @request.setter
    def request(self, value: RequestBase):
        self.obj.request.CopyFrom(value.obj)

    @request.deleter
    def request(self) -> None:
        self.obj.ClearField("request")

    @property
    def recipient(self) -> str:
        return self.obj.recipient

    @recipient.setter
    def recipient(self, value: str):
        self.obj.recipient = value

    @recipient.deleter
    def recipient(self) -> None:
        self.obj.ClearField("recipient")


class PublishJob(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.PublishJob  # type: ignore[attr-defined]

    def __init__(self, *, services: Optional[list[Service]] = None, job_id: str):
        self.obj = self.TYPE()
        if services is not None:
            self.obj.services.extend([m.obj for m in services])
        self.obj.job_id = job_id

    @property
    def services(self) -> list[Service]:
        return cast(list[Service], [self._from_pb(m) for m in self.obj.services])

    @services.setter
    def services(self, value: list[Service]):
        del self.obj.services[:]
        self.obj.services.extend([m.obj for m in value])

    @services.deleter
    def services(self) -> None:
        self.obj.ClearField("services")

    @property
    def job_id(self) -> str:
        return self.obj.job_id

    @job_id.setter
    def job_id(self, value: str):
        self.obj.job_id = value

    @job_id.deleter
    def job_id(self) -> None:
        self.obj.ClearField("job_id")


class RegisterServices(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.RegisterServices  # type: ignore[attr-defined]

    def __init__(self, *, services: Optional[list[Service]] = None):
        self.obj = self.TYPE()
        if services is not None:
            self.obj.services.extend([m.obj for m in services])

    @property
    def services(self) -> list[Service]:
        return cast(list[Service], [self._from_pb(m) for m in self.obj.services])

    @services.setter
    def services(self, value: list[Service]):
        del self.obj.services[:]
        self.obj.services.extend([m.obj for m in value])

    @services.deleter
    def services(self) -> None:
        self.obj.ClearField("services")


class RequestBase(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.RequestBase  # type: ignore[attr-defined]

    def __init__(
        self,
        *,
        event: Optional[Event] = None,
        publish_job: Optional[PublishJob] = None,
        register_services: Optional[RegisterServices] = None,
        type: Optional[MessageType] = None,
    ):
        self.obj = self.TYPE()
        if event is not None:
            self.obj.event.CopyFrom(event.obj)
        if publish_job is not None:
            self.obj.publish_job.CopyFrom(publish_job.obj)
        if register_services is not None:
            self.obj.register_services.CopyFrom(register_services.obj)
        if type is not None:
            self.obj.type = type

    @property
    def event(self) -> Event:
        return cast(Event, self._from_pb(self.obj.event))

    @event.setter
    def event(self, value: Event):
        self.obj.event.CopyFrom(value.obj)

    @event.deleter
    def event(self) -> None:
        self.obj.ClearField("event")

    @property
    def publish_job(self) -> PublishJob:
        return cast(PublishJob, self._from_pb(self.obj.publish_job))

    @publish_job.setter
    def publish_job(self, value: PublishJob):
        self.obj.publish_job.CopyFrom(value.obj)

    @publish_job.deleter
    def publish_job(self) -> None:
        self.obj.ClearField("publish_job")

    @property
    def register_services(self) -> RegisterServices:
        return cast(RegisterServices, self._from_pb(self.obj.register_services))

    @register_services.setter
    def register_services(self, value: RegisterServices):
        self.obj.register_services.CopyFrom(value.obj)

    @register_services.deleter
    def register_services(self) -> None:
        self.obj.ClearField("register_services")

    @property
    def type(self) -> MessageType:
        return self.obj.type

    @type.setter
    def type(self, value: MessageType):
        self.obj.type = value

    @type.deleter
    def type(self) -> None:
        self.obj.ClearField("type")


class ResponseBase(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.ResponseBase  # type: ignore[attr-defined]

    def __init__(
        self, *, success: Optional[bool] = None, type: Optional[MessageType] = None
    ):
        self.obj = self.TYPE()
        if success is not None:
            self.obj.success = success
        if type is not None:
            self.obj.type = type

    @property
    def success(self) -> bool:
        return self.obj.success

    @success.setter
    def success(self, value: bool):
        self.obj.success = value

    @success.deleter
    def success(self) -> None:
        self.obj.ClearField("success")

    @property
    def type(self) -> MessageType:
        return self.obj.type

    @type.setter
    def type(self, value: MessageType):
        self.obj.type = value

    @type.deleter
    def type(self) -> None:
        self.obj.ClearField("type")


class Service(Message):
    TYPE = mercaido_client.pb.mercaido_pb2.Service  # type: ignore[attr-defined]

    def __init__(
        self,
        *,
        attributes: Optional[list[Attribute]] = None,
        svg: Optional[str] = None,
        description: Optional[str] = None,
        name: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        self.obj = self.TYPE()
        if attributes is not None:
            self.obj.attributes.extend([m.obj for m in attributes])
        if svg is not None:
            self.obj.svg = svg
        if description is not None:
            self.obj.description = description
        if name is not None:
            self.obj.name = name
        if endpoint is not None:
            self.obj.endpoint = endpoint

    @property
    def attributes(self) -> list[Attribute]:
        return cast(list[Attribute], [self._from_pb(m) for m in self.obj.attributes])

    @attributes.setter
    def attributes(self, value: list[Attribute]):
        del self.obj.attributes[:]
        self.obj.attributes.extend([m.obj for m in value])

    @attributes.deleter
    def attributes(self) -> None:
        self.obj.ClearField("attributes")

    @property
    def svg(self) -> str:
        return self.obj.svg

    @svg.setter
    def svg(self, value: str):
        self.obj.svg = value

    @svg.deleter
    def svg(self) -> None:
        self.obj.ClearField("svg")

    @property
    def description(self) -> str:
        return self.obj.description

    @description.setter
    def description(self, value: str):
        self.obj.description = value

    @description.deleter
    def description(self) -> None:
        self.obj.ClearField("description")

    @property
    def name(self) -> str:
        return self.obj.name

    @name.setter
    def name(self, value: str):
        self.obj.name = value

    @name.deleter
    def name(self) -> None:
        self.obj.ClearField("name")

    @property
    def endpoint(self) -> str:
        return self.obj.endpoint

    @endpoint.setter
    def endpoint(self, value: str):
        self.obj.endpoint = value

    @endpoint.deleter
    def endpoint(self) -> None:
        self.obj.ClearField("endpoint")


MessageRegistry.register(mercaido_client.pb.mercaido_pb2.Attribute, Attribute)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.Event, Event)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.MessageBase, MessageBase)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.PublishJob, PublishJob)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.RegisterServices, RegisterServices)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.RequestBase, RequestBase)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.ResponseBase, ResponseBase)  # type: ignore[attr-defined]
MessageRegistry.register(mercaido_client.pb.mercaido_pb2.Service, Service)  # type: ignore[attr-defined]
