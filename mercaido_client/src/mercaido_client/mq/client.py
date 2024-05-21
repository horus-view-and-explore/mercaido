# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import logging
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from typing import Optional
from uuid import uuid4

from pika import URLParameters
from pika.adapters.blocking_connection import (
    BlockingConnection,
    BlockingChannel,
)
from pika.exchange_type import ExchangeType

from ..attrs import AttrDict
from ..pb.mercaido import (
    MessageBase,
    MessageType,
    RegisterServices,
    RequestBase,
    Service,
    Event,
    PublishJob,
)

logger = logging.getLogger(__name__)


MAIN_EXCHANGE = AttrDict(
    name="mercaido.main",
    type=ExchangeType.topic,
    durable=True,
)

EVENTS_EXCHANGE = AttrDict(
    name="mercaido.broadcast",
    type=ExchangeType.fanout,
    durable=True,
)

_DISPATCHER_NAME = "mercaido.dispatcher"
DISPATCHER_QUEUE = AttrDict(
    name=_DISPATCHER_NAME,
    exchange=MAIN_EXCHANGE.name,
    binding_keys=[_DISPATCHER_NAME],
    durable=True,
)

DISPATCHER_ROUTING_KEY = _DISPATCHER_NAME
DISCOVERY_ROUTING_KEY = "mercaido.discovery"
SERVICE_BINDING_KEYS_PART = [DISCOVERY_ROUTING_KEY]


class ClientError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Ack:
    _channel: BlockingChannel
    _delivery_tag: int

    def ok(self) -> None:
        self._channel.connection.add_callback_threadsafe(
            partial(self._channel.basic_ack, delivery_tag=self._delivery_tag)
        )

    def cancel(self) -> None:
        self._channel.connection.add_callback_threadsafe(
            partial(self._channel.basic_nack, delivery_tag=self._delivery_tag)
        )


class BlockingClient:
    DEFAULT_INACTIVITY_TIMEOUT: float = 40.0

    @dataclass(frozen=True, slots=True)
    class State:
        connection: BlockingConnection
        channel: BlockingChannel

    _state: State | None
    _params: URLParameters

    def __init__(self, url: str) -> None:
        self._state = None
        self._params = URLParameters(url)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    def open(self) -> None:
        if self._state is not None:
            raise ClientError("connection already open")
        connection = BlockingConnection(self._params)
        connection.add_on_connection_blocked_callback(
            self._on_connection_blocked_callback
        )
        connection.add_on_connection_unblocked_callback(
            self._on_connection_unblocked_callback
        )
        channel = connection.channel()
        self._state = self.State(connection, channel)

    def close(self) -> None:
        if self._state is None:
            raise ClientError("connection already closed")
        self._state.channel.close()
        self._state.connection.close()
        self._state = None

    def is_open(self):
        return self._state is not None

    def _on_connection_blocked_callback(self, connection, method):
        logger.warning(f"connection {connection} blocked: {method=}")

    def _on_connection_unblocked_callback(self, connection, method):
        logger.warning(f"connection {connection} unblocked: {method=}")

    def exchange(
        self,
        exchange_name: str,
        exchange_type: ExchangeType,
        durable: bool = True,
    ) -> AttrDict:
        if self._state is None:
            raise ClientError("connection closed")
        self._state.channel.exchange_declare(
            exchange_name,
            exchange_type,
            durable=durable,
        )
        return AttrDict(name=exchange_name, type=exchange_type)

    def queue(
        self,
        queue_name: str,
        exchange_name: str,
        binding_keys: list[str],
        durable: bool = True,
    ) -> AttrDict:
        if self._state is None:
            raise ClientError("connection closed")
        self._state.channel.queue_declare(
            queue=queue_name,
            durable=durable,
        )
        for binding_key in binding_keys:
            self._state.channel.queue_bind(
                queue_name,
                routing_key=binding_key,
                exchange=exchange_name,
            )
        return AttrDict(name=queue_name, binding_keys=binding_keys)

    @contextmanager
    def temporary_exchange(self, *args, **kwargs) -> Generator[AttrDict, None, None]:
        result = self.exchange(*args, durable=False, **kwargs)
        try:
            yield result
        finally:
            self._state.channel.exchange_delete(result.name)  # type: ignore

    @contextmanager
    def temporary_queue(self, *args, **kwargs) -> Generator[AttrDict, None, None]:
        result = self.queue(*args, durable=False, **kwargs)
        try:
            yield result
        finally:
            self._state.channel.queue_delete(result.name)  # type: ignore

    def publish(self, exchange: str, routing_key: str, msg: MessageBase) -> None:
        if self._state is None:
            raise ClientError("connection closed")
        # TODO: Durable message.
        self._state.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=msg.serialize(),
        )

    @contextmanager
    def consume(
        self, queue: str, timeout: Optional[float] = DEFAULT_INACTIVITY_TIMEOUT
    ):
        if self._state is None:
            raise ClientError("connection closed")

        channel = self._state.connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.add_on_return_callback(self._on_channel_return_callback)

        if self._state is None:
            raise ClientError("connection closed")
        try:
            yield self._consume_generator(channel, queue, timeout)
        finally:
            channel.cancel()

    def _consume_generator(self, channel: BlockingChannel, queue: str, timeout: float):
        assert self._state is not None
        consumer = channel.consume(queue, inactivity_timeout=timeout)
        for method_frame, header_frame, body in consumer:
            if method_frame is None:
                yield None, None
                continue

            if header_frame.reply_to:
                raise NotImplementedError("reply_to implemented")

            assert body is not None  # method_frame is already checked.
            assert method_frame.delivery_tag is not None
            # TODO: Use content-type.
            msg = MessageBase.deserialize(body)
            ack = Ack(channel, method_frame.delivery_tag)
            yield msg, ack

    def _on_channel_return_callback(
        self,
        channel: BlockingChannel,
        method,
        properties,
        body,
    ) -> None:
        logger.warning(f"message returned on channel {channel}: {method=}")


class ServiceClient:
    _service: Service
    _client: BlockingClient

    def __init__(self, service: Service, url: str) -> None:
        self._service = service
        self._client = BlockingClient(url)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    def open(self):
        self._client.open()

    def close(self):
        # XXX: Allow client to be closed from other threads.
        self._client._state.channel.connection.add_callback_threadsafe(
            self._client.close
        )

    def register(self) -> None:
        self._client.queue(
            queue_name=self._service.endpoint,
            exchange_name=MAIN_EXCHANGE.name,
            binding_keys=[self._service.endpoint] + SERVICE_BINDING_KEYS_PART,
        )
        self._client.publish(
            MAIN_EXCHANGE.name,
            DISPATCHER_ROUTING_KEY,
            MessageBase(
                recipient=DISPATCHER_QUEUE.name,
                request=RequestBase(
                    type=MessageType.MESSAGE_TYPE_REGISTER_SERVICES,
                    register_services=RegisterServices(
                        services=[self._service],
                    ),
                ),
            ),
        )

    # TODO: unregister.
    # TODO: pong.

    def publish_event(self, event: Event) -> None:
        tsc = self._client._state.channel.connection.add_callback_threadsafe
        msg = MessageBase(
            request=RequestBase(
                type=MessageType.MESSAGE_TYPE_EVENT,
                event=event,
            ),
        )
        tsc(
            partial(
                self._client.publish, MAIN_EXCHANGE.name, DISPATCHER_ROUTING_KEY, msg
            )
        )
        tsc(partial(self._client.publish, EVENTS_EXCHANGE.name, "", msg))

    @contextmanager
    def consume(self, timeout: Optional[float] = None):
        with self._client.consume(self._service.endpoint, timeout) as consumer:
            yield consumer


class PublishJobClient:
    _client: BlockingClient

    def __init__(self, url: str) -> None:
        self._client = BlockingClient(url)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    def open(self):
        self._client.open()

    def close(self):
        self._client.close()

    def publish(self, endpoint: str, publish_job: PublishJob) -> None:
        # FIXME: Currently directly send to the service. Better to
        # send it to the dispatcher for storage, sanity checking, and
        # forwarding.
        self._client.publish(
            MAIN_EXCHANGE.name,
            endpoint,  # Routing key is the same as the endpoint.
            MessageBase(
                recipient=endpoint,
                request=RequestBase(
                    type=MessageType.MESSAGE_TYPE_PUBLISH_JOB,
                    publish_job=publish_job,
                ),
            ),
        )


class EventListenerClient:
    _client: BlockingClient

    def __init__(self, url: str) -> None:
        self._client = BlockingClient(url)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    def open(self):
        self._client.open()

    def close(self):
        self._client.close()

    @contextmanager
    def consume(self, timeout: Optional[float] = None):
        name = f"mercaido.events.{uuid4().hex}"
        exch = EVENTS_EXCHANGE.name

        # TODO: Enable auto-ack, easier for dumb listeners.
        with self._client.temporary_queue(name, exch, [""]):
            with self._client.consume(name, timeout) as consumer:
                yield consumer
