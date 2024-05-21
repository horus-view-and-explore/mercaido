# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import pytest
import pika.exceptions
from pika.exchange_type import ExchangeType

from mercaido_client.mq.client import BlockingClient
from mercaido_client.pb.mercaido import (
    MessageBase,
    MessageType,
    RequestBase,
)
from mercaido_client.testing_utils import random_string


def test_client_with_connection_error():
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        BlockingClient("amqp://guest:guest@127.0.0.1:44672/%2F").open()


def test_producer_and_consumer(rabbitmq_server):
    exchange_name = f"exchange-{random_string()}"
    queue_name = f"queue-{random_string()}"

    msg_send = MessageBase(
        recipient="blep",
        request=RequestBase(
            type=MessageType.MESSAGE_TYPE_REGISTER_SERVICES,
        ),
    )
    msg_recv = None

    with (
        BlockingClient(rabbitmq_server.url()) as client1,
        BlockingClient(rabbitmq_server.url()) as client2,
        client1.temporary_exchange(exchange_name, ExchangeType.topic) as exchange,
        client1.temporary_queue(queue_name, exchange.name, ["test.*"]) as q1,
    ):
        client1.publish(exchange_name, "test.pub", msg_send)
        with client2.consume(queue_name, timeout=1.0) as consumer:
            for msg, ack in consumer:
                if msg is None:
                    break
                msg_recv = msg
                ack.ok()

    assert msg_recv is not None
    assert compare_messages(msg_recv, msg_send)


def compare_messages(a, b):
    a_blob = a.obj.SerializeToString(deterministic=True)
    b_blob = b.obj.SerializeToString(deterministic=True)
    return a_blob == b_blob
