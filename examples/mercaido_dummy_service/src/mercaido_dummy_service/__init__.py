# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import sys
import time
import threading
from queue import Queue
from random import randint
from typing import Any

from mercaido_client.mq.client import ServiceClient
from mercaido_client.pb.mercaido import (
    Attribute,
    AttributeType,
    Event,
    EventType,
    MessageType,
    PublishJob,
    Service,
)

logger = logging.getLogger(__name__)


def parse_cli_arguments(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser("mercaido_dummy_service")
    parser.add_argument(
        "--amqp",
        type=str,
        help="URL of AMQP server.",
        required=True,
    )
    parsed_args = parser.parse_args(args)
    return parsed_args


DUMMY_SERVICE_ICON = b"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#0d47a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-coffee"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>"""


def main() -> int:
    args = parse_cli_arguments(sys.argv[1:])

    logging.basicConfig(level=logging.INFO)

    # Create a description of the service.
    srv = Service(
        endpoint="mercaido.service.dummy",
        name="logger",
        description="An example dummy logger service.",
        svg=DUMMY_SERVICE_ICON,
        attributes=[
            Attribute(
                type=AttributeType.ATTRIBUTE_TYPE_RECORDING_ID,
                id="recording_id",
                display_name="Recording",
            ),
            Attribute(
                type=AttributeType.ATTRIBUTE_TYPE_FOLDER,
                id="output_folder",
                display_name="Where should the result be stored.",
            ),
            Attribute(
                type=AttributeType.ATTRIBUTE_TYPE_BOOLEAN,
                id="fail",
                display_name="Fail at a random point",
            ),
            Attribute(
                type=AttributeType.ATTRIBUTE_TYPE_MEDIA_SERVER_CONNECTION,
                id="media_server",
                display_name="Media Server connection string.",
                sensitive=True,
            ),
            Attribute(
                type=AttributeType.ATTRIBUTE_TYPE_RECORDINGS_SERVER_CONNECTION,
                id="recordings_server",
                display_name="Recordings Server connection string.",
                sensitive=True,
            ),
        ],
    )

    queue = Queue()

    # Run client in a background thread. This client receives jobs from
    # mercaido_server and put them on a queue (defined above).
    client = ServiceClient(srv, args.amqp)
    client_thread = threading.Thread(
        target=client_job_listener,
        args=[client, queue],
        daemon=True,
    )
    client_thread.start()

    try:
        # Job execution loop.
        while True:
            msg, ack = queue.get()

            # Check if this is an acceptable message.
            if msg is None:
                continue
            if not msg.request:
                logger.error("message has not request")
                continue
            if msg.request.type != MessageType.MESSAGE_TYPE_PUBLISH_JOB:
                logger.error(
                    f"message request type not supported: {msg.request.type!r}"
                )
                continue

            do_job(msg.request.publish_job, client, ack)
            queue.task_done()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        client_thread.join()


def client_job_listener(client, queue):
    client.open()
    client.register() #TODO
    with client.consume() as consumer:
        # Listen for messages and put them on the queue to be processed
        # in the job execution loop.
        for msg, ack in consumer:
            queue.put((msg, ack))
    logger.info("client job listener stopped")


def do_job(job: PublishJob, client: ServiceClient, ack: Any):
    def update(typ, **kwargs):
        # Publish an event to communicate job start, progress updates,
        # completion, and failures.
        client.publish_event(Event(job_id=job.job_id, type=typ, **kwargs))

    try:
        logger.info(f"job {job.job_id} started")
        update(EventType.EVENT_TYPE_JOB_START)
        update(EventType.EVENT_TYPE_JOB_PROGRESS, progress=0)
        logger.info(f"job {job.job_id} progress 0%")

        # TODO: What is this exactly?
        fail_attr = [attr for attr in job.services[0].attributes if attr.id == "fail"][
            0
        ]
        fail_job = fail_attr.values[0] == "True"
        fail_at = randint(1, 10)

        for n in range(1, 11):
            if fail_job and fail_at == n:
                update(
                    EventType.EVENT_TYPE_JOB_ERROR,
                    error_message="Job failed randomly as requested",
                )
                logger.info(f"job {job.job_id} failed randomly as requested")
                raise Exception("Requested fail")

            update(EventType.EVENT_TYPE_JOB_PROGRESS, progress=10 * n)
            logger.info(f"job {job.job_id} progress {10 * n}%")
            time.sleep(2)

        update(EventType.EVENT_TYPE_JOB_STOP)
        logger.info(f"job {job.job_id} completed")

        # Acknowledge successful completion of job.
        ack.ok()
    except Exception:
        logger.exception(f"job {job.job_id} failed")
        # Job failed, negative acknowledgement.
        ack.cancel()
