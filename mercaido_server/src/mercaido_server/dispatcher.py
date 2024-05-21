# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from mercaido_client.mq.client import BlockingClient, DISPATCHER_QUEUE
from mercaido_client.pb.mercaido import MessageType, MessageBase, EventType

from . import models


logger = logging.getLogger(__name__)


class Dispatcher:
    _mq: BlockingClient
    _queue: str

    def __init__(self, amqp_url: str, db_url: str) -> None:
        self._db = sa.create_engine(db_url)
        self._mq = BlockingClient(amqp_url)
        self._queue = DISPATCHER_QUEUE.name
        self._handlers = {
            MessageType.MESSAGE_TYPE_REGISTER_SERVICES: self._handle_register_service,
            MessageType.MESSAGE_TYPE_EVENT: self._handle_event,
            MessageType.MESSAGE_TYPE_PUBLISH_JOB: self._handle_publish_job,
        }

    def run(self):
        with self._mq, self._mq.consume(self._queue) as consumer:
            for msg, ack in consumer:
                if msg is None:
                    continue
                try:
                    self._handlers[msg.request.type](msg)
                    ack.ok()
                except KeyError:
                    logger.error(f"unknown request type: {msg.request.type!r}")
                    ack.cancel()
                except Exception:
                    logger.exception("request handler failed")
                    ack.cancel()

    def stop(self):
        pass

    def _handle_register_service(self, msg: MessageBase) -> None:
        with self._db.begin() as db:
            for service in msg.request.register_services.services:
                ident = service.endpoint
                kwargs = {
                    "last_seen": now(),
                    "data": service,
                }
                db.execute(
                    sqlite_upsert(models.Service)
                    .values(ident=ident, **kwargs)
                    .on_conflict_do_update(
                        index_elements=[models.Service.ident],
                        set_=kwargs,
                    )
                )
                logger.info(
                    f"registered service: endpoint={service.endpoint} (ident) "
                    f"name={service.name}"
                )

    def _handle_event(self, msg: MessageBase) -> None:
        if (
            msg.request is None
            or msg.request.event is None
            or msg.request.event.job_id is None
        ):
            logger.error(f"incomplete event message: {msg!r}")
            return

        event = msg.request.event
        kwargs = {}

        # FIXME: Updating started_at/finished_at here is not the time
        # a job started or finished, but the time its notification of
        # that action arrived at the dispatcher.
        match event.type:
            case EventType.EVENT_TYPE_JOB_START:
                kwargs.update(started_at=now())
            case EventType.EVENT_TYPE_JOB_STOP:
                kwargs.update(finished_at=now(), error_msg=None, error=False)
            case EventType.EVENT_TYPE_JOB_ERROR:
                kwargs.update(
                    finished_at=now(), error=True, error_msg=event.error_message
                )
            case EventType.EVENT_TYPE_JOB_PROGRESS:
                pass  # ignore
            case _:
                logger.error(f"unknown event type: {event.type!r}")

        if kwargs:
            with self._db.begin() as db:
                db.execute(
                    sa.update(models.Job)
                    .where(models.Job.id == event.job_id)
                    .values(**kwargs)
                )

    def _handle_publish_job(self, msg: MessageBase) -> None:
        print("TODO _handle_publish_job", msg)
        pass  # TODO: Copy and pass to service. Save to DB.


def now():
    return datetime.now(timezone.utc)
