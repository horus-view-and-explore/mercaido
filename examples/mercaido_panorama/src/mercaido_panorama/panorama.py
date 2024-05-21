# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import os

import psycopg2

from typing import Callable

from mercaido_client.pb.mercaido import Event, EventType, PublishJob
from horus_db import Frames, Frame
from horus_media import ImageRequestBuilder, ImageProvider
from horus_media import Client, Mode, Scales


class Panorama:
    job: PublishJob

    def __init__(self, job: PublishJob, on_event: Callable[[Event], None]) -> None:
        self.job = job
        self.on_event = on_event

    def execute(self):
        for service in self.job.services:
            if service.name == "Panorama Export":
                self.export(service)

    def export(self, service):
        self._send_start_event()

        properties = {}
        for att in service.attributes:
            properties[att.id] = att.values

        db_conn = psycopg2.connect(properties["recordings_server"][0])
        client = Client(properties["media_server"][0], 10)

        frames = Frames(db_conn)
        image_provider = ImageProvider()

        # Get frames
        with frames.query(
            recordingid=int(properties["recordingid"][0]),
            order_by="index",
        ) as results:
            out_dir = properties["outputfolder"][0]

            if not os.path.isdir(out_dir):
                if os.path.exists(out_dir):
                    msg = f"Output {out_dir} exists, but it is not a directory"
                    self._send_error_event(msg)
                    raise msg
                os.makedirs(out_dir)

            for frame in Frame.iter(results):
                if frame is None:
                    self._send_finished_event()
                    print("No frames!")
                    exit()

                # Set parameters
                mode = Mode.panoramic
                scale = Scales.Px_4096

                # Get the image
                request_builder = ImageRequestBuilder(frame.recordingid, frame.uuid)
                request = client.fetch(request_builder.build(mode, scale))
                result = image_provider.fetch(request)

                filename = f"{out_dir}/panoramic_{frame.index:06}.jpg"

                with open(filename, "wb") as f:
                    f.write(result.image.getvalue())
                    result.image.close()

                self._send_progress_event((results.rownumber / results.rowcount) * 100)

            self._send_finished_event()

    def _send_start_event(self) -> None:
        event = Event(type=EventType.EVENT_TYPE_JOB_START)
        event.job_id = self.job.job_id
        self.on_event(event)

    def _send_finished_event(self) -> None:
        event = Event(type=EventType.EVENT_TYPE_JOB_STOP)
        event.job_id = self.job.job_id
        self.on_event(event)

    def _send_error_event(self, message: str) -> None:
        event = Event(type=EventType.EVENT_TYPE_JOB_ERROR)
        event.error_message = message
        event.job_id = self.job.job_id
        self.on_event(event)

    def _send_progress_event(self, percent: float) -> None:
        event = Event(type=EventType.EVENT_TYPE_JOB_PROGRESS)
        event.progress = percent
        event.job_id = self.job.job_id
        self.on_event(event)
