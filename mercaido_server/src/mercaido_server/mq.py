# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from functools import partial
from contextlib import contextmanager

from mercaido_client.mq.client import PublishJobClient, EventListenerClient
from pyramid.config import Configurator
from pyramid.interfaces import IRequest

from .attrs import AttrDict


def includeme(config: Configurator):
    url = config.get_settings()["amqp.url"]

    @contextmanager
    def publish_job_client(request: IRequest):
        with PublishJobClient(url) as client:
            yield client

    @contextmanager
    def event_listener_client(request: IRequest):
        with EventListenerClient(url) as client:
            yield client

    config.add_request_method(publish_job_client)
    config.add_request_method(event_listener_client)
