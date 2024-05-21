# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import json
import logging
from dataclasses import asdict
from typing import Any
from queue import Empty
from datetime import datetime, timezone

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.interfaces import IRequest, IResponse
from sqlalchemy import select, delete

from .. import models
import mercaido_client.pb.mercaido as messages


logger = logging.getLogger(__name__)


class JobViews:
    request: IRequest

    def __init__(self, request: IRequest) -> None:
        self.request = request

    def _job_event_stream(self, jobs: list[dict[str, Any]]):
        sse = SSE()

        yield sse.retry(100)
        yield sse.event("job-list", jobs)

        # XXX: When does this stop?
        with self.request.event_listener_client() as client, client.consume(
            timeout=1
        ) as consumer:
            for msg, ack in consumer:
                if msg is None:
                    yield sse.event(
                        "job-ping",
                        {"timestamp": datetime.now(timezone.utc).isoformat()},
                    )
                    continue

                # Skip incomplete messages.
                if (
                    msg.request is None
                    or msg.request.event is None
                    or msg.request.event.job_id is None
                ):
                    logger.error(f"incomplete event message: {msg!r}")
                    ack.ok()
                    continue

                # Handle events.
                event = msg.request.event
                match event.type:
                    case messages.EventType.EVENT_TYPE_JOB_START:
                        self.request.tm.begin()
                        job = self.request.dbsession.scalars(
                            select(models.Job).where(models.Job.id == event.job_id)
                        ).one()
                        self.request.tm.abort()
                        yield sse.event("job-started", job.as_dict())
                    case messages.EventType.EVENT_TYPE_JOB_STOP:
                        yield sse.event(
                            "job-stopped",
                            {
                                "id": event.job_id,
                                "error_message": event.error_message,
                                "error": event.error_message is not None,
                            },
                        )
                    case messages.EventType.EVENT_TYPE_JOB_ERROR:
                        pass  # ignore
                    case messages.EventType.EVENT_TYPE_JOB_PROGRESS:
                        yield sse.event(
                            "job-progress",
                            {"id": event.job_id, "progress": event.progress},
                        )
                    case _:
                        logger.error(f"unknown event type: {event.type!r}")

                ack.ok()

    @view_config(route_name="job_events")
    def job_events(self) -> IResponse:
        running_jobs = self.request.dbsession.scalars(
            select(models.Job).order_by(models.Job.started_at)
        ).all()

        running_jobs = [job.as_dict() for job in running_jobs]

        response: IResponse = self.request.response
        response.content_type = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"

        response.app_iter = self._job_event_stream(running_jobs)

        return response

    @view_config(
        route_name="job_clear_finished",
        renderer="json",
        request_method="POST",
        require_csrf=False,
    )
    def job_clear_finished(self) -> IResponse:
        deleted_jobs = self.request.dbsession.scalars(
            delete(models.Job)
            .where(models.Job.finished_at != None)  # noqa: E711
            .returning(models.Job.id)
        ).all()
        return dict(success=True, deleted_jobs=deleted_jobs)

    @view_config(
        route_name="job_delete",
        renderer="json",
        request_method="POST",
        require_csrf=False,
    )
    def job_delete(self) -> IResponse:
        job_id = self.request.matchdict["id"]
        self.request.dbsession.execute(
            delete(models.Job).where(models.Job.id == job_id)
        )
        return dict(success=True, deleted_job=job_id)


class SSE:
    _id: int

    def __init__(self):
        self._id = -1

    def _encode(self, **kwargs) -> bytes:
        # FIXME: It "data" contains newlines, split the value and put
        # it on muldiple lines prefixed with "data: "
        # FIXME: Only allow SSE fields id, event, data, retry.
        def convert(v):
            if isinstance(v, (dict, list, tuple)):
                v = json.dumps(v)
            return v

        buf = "\n".join(f"{k}: {convert(v)}" for k, v in kwargs.items())
        return (buf + "\n\n").encode("utf-8")

    def retry(self, n: int) -> bytes:
        return self._encode(retry=n)

    def event(self, name: str, data: Any) -> bytes:
        self._id += 1
        return self._encode(id=self._id, event=name, data=data)
