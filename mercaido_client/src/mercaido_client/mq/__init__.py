# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import logging
from threading import Event
from typing import Callable, Any, ClassVar

from pika import SelectConnection, URLParameters, BasicProperties
from pika.channel import Channel
from pika.exchange_type import ExchangeType
from pika.frame import Method
from pika.exceptions import ChannelClosedByClient
from pika.spec import Basic

from mercaido_client.pb.message import MessageRegistry
from mercaido_client.pb.mercaido import MessageBase

logger = logging.getLogger(__name__)


class Connection:
    DEFAULT_CONNECT_TIMEOUT: ClassVar[float] = 10.0

    _url: str
    _connection: SelectConnection
    _channel: Channel
    _queue_name: str
    _exclusive: bool
    _routing_key: str
    _consumer_tag: str
    _consuming: bool = False  # FIXME: Unused.
    _closing: bool = False
    _on_message_callback: Callable[[MessageBase], None]

    _connect_event: Event
    _is_connected: bool
    _error: Exception | None

    EXCHANGE: str = "mercaido"

    def __init__(
        self, url: str, queue_name: str, routing_key: str, exclusive: bool = False
    ) -> None:
        self._url = url
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._exclusive = exclusive

        self._connect_event = Event()
        self._is_connected = False
        self._error = None

    def connect(self) -> SelectConnection:
        connection_params = URLParameters(self._url)
        return SelectConnection(
            parameters=connection_params,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_close,
        )

    def wait_until_connected(self, timeout: float | None=None) -> bool:
        if timeout is None:
            timeout = self.DEFAULT_CONNECT_TIMEOUT
        result = self._connect_event.wait(timeout)
        self._is_connected = result and self._error is None
        return self._is_connected

    def wait_until_connected_or_error(self, timeout: float | None=None) -> bool:
        result = self.wait_until_connected(timeout)
        if self._error is not None:
            raise self._error
        return result

    def is_connected(self) -> bool:
        return self._is_connected

    def error(self) -> Exception | None:
        return self._error

    # XXX: Can't figure out the type of 'connection' arg of the
    # _on_connection_* functions.

    def _on_connection_open(self, connection: Any) -> None:
        logger.info(f"Connection opened to {connection.params.host}")
        self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_open_error(
        self, connection: Any, error: Exception | str
    ) -> None:
        if not isinstance(error, Exception):
            error = RuntimeError(error)
        self._error = error
        self._connect_event.set()
        logger.error(f"Error connecting to {connection.params.host}: {error}")
        self._connection.ioloop.stop()

    def _on_connection_close(
        self, connection: Any, reason: Exception
    ) -> None:
        logger.info(f"Connection to {connection.params.host} closed: {reason}")
        self._connection.ioloop.stop()

    def _on_channel_open(self, channel: Channel) -> None:
        self._channel = channel
        self._channel.add_on_close_callback(self._on_channel_close)
        self._setup_exchange(self.EXCHANGE)

    def _on_channel_close(self, channel: Channel, reason: Exception) -> None:
        if isinstance(reason, ChannelClosedByClient):
            logger.info("Channel closed")
        else:
            logger.error(f"Channel closed unexpectedly, closing connection: {reason}")
        self._connection.close()

    def _setup_exchange(self, exchange_name: str) -> None:
        logger.info(f"Declaring exchange '{exchange_name}'")
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=ExchangeType.topic,
            auto_delete=False,
            callback=self._on_exchange_declare,
        )

    def _on_exchange_declare(self, _frame: Method) -> None:
        logger.info("Exchange declared")
        self._setup_queue()

    def _setup_queue(self) -> None:
        logger.info(f"Declaring queue '{self._queue_name}'")
        self._channel.queue_declare(
            queue=self._queue_name,
            exclusive=self._exclusive,
            auto_delete=True,
            callback=self._on_queue_declare,
        )

    def _on_queue_declare(self, _frame: Method) -> None:
        logger.info(
            f"Queue '{self._queue_name}' declared, binding with routing key {self._routing_key}..."
        )
        self._channel.queue_bind(
            queue=self._queue_name,
            exchange=self.EXCHANGE,
            routing_key=self._routing_key,
            callback=self._on_queue_bind,
        )

    def _on_queue_bind(self, _frame: Method) -> None:
        logger.info(f"Queue '{self._queue_name}' bound")
        self._set_qos()

    def _set_qos(self) -> None:
        self._channel.basic_qos(prefetch_count=1, callback=self._on_qos_ok)

    def _on_qos_ok(self, _frame: Method):
        logger.info("QoS set")
        self._start_consuming()

    def _on_consumer_cancelled(self, frame: Method) -> None:
        logger.info(f"Consumer cancelled remotely, shutting down: {frame}")
        if getattr(self, "_channel", None):
            self._channel.close()

    def _on_message(
        self,
        channel: Channel,
        basic_deliver: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        logger.debug(f"Message received on {channel.channel_number}: {body!r}")
        if self._on_message_callback is not None:
            message = MessageBase.deserialize(body)
            # FIXME: Types.
            self._on_message_callback(message)  # type: ignore
        logger.debug(f"Acknowledging message on {channel.channel_number}")
        assert basic_deliver.delivery_tag is not None  # No auto-ack.
        self._ack_message(basic_deliver.delivery_tag)

    def _ack_message(self, delivery_tag: int) -> None:
        self._channel.basic_ack(delivery_tag)

    def _on_cancel(self, _frame: Method) -> None:
        logger.info(f"Consumer {self._consumer_tag} cancelled")
        self._consuming = False
        self._channel.close()

    def _start_consuming(self) -> None:
        logger.info(f"Starting {self._queue_name}")
        self._connect_event.set()
        self._channel.add_on_cancel_callback(self._on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(
            self._queue_name, self._on_message
        )
        self._consuming = True
        logger.info(f"Consuming messages as {self._consumer_tag}")

    def _stop_consuming(self) -> None:
        if self._channel:
            logger.info("Sending cancel message to RabbitMQ")
            self._channel.basic_cancel(self._consumer_tag, callback=self._on_cancel)

    def run(self) -> None:
        self._connection = self.connect()
        self._connection.ioloop.start()

    def _do_stop(self) -> None:
        if not self._closing:
            # TODO: Set _consuming = False
            self._connect_event.clear()
            self._is_connected = False
            self._closing = True
            logger.info("Stopping...")
            self._stop_consuming()

    def stop(self) -> None:
        self._connection.ioloop.add_callback_threadsafe(self._do_stop)

    def send(self, recipient: str, message: bytes) -> None:
        logger.debug(f"Sending message of {len(message)} bytes to {recipient}")
        self._connection.ioloop.add_callback_threadsafe(
            lambda: self._channel.basic_publish(
                exchange=self.EXCHANGE, routing_key=recipient, body=message
            )
        )

    def send_message(self, message: MessageBase) -> None:
        self.send(message.recipient, message.serialize())

    def set_on_message_callback(self, callback: Callable[[MessageBase], None]) -> None:
        self._on_message_callback = callback
