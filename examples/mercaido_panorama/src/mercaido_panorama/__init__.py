# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import sys
import threading
import traceback
from queue import Queue

from mercaido_client.mq.client import ServiceClient, Ack
from mercaido_client.pb.mercaido import (
    Attribute,
    AttributeType,
    EventType,
    MessageType,
    Service,
    Event,
    PublishJob
)

from pprint import pformat
from concurrent.futures import ThreadPoolExecutor

from .panorama import Panorama

logger = logging.getLogger(__name__)


class PanoramaService:
    def __init__(self, service_id: str, url: str):
        self.service_id = service_id
        self.work_queue = Queue()
        # self.url = url
        service = Service(
            endpoint=self.service_id,
            name="Panorama Export",
            description="Export imagery to jpeg panorama imagery",
            svg="""
        <svg version="1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" enable-background="new 0 0 48 48">
        <path fill="#F57C00" d="M4,9v32c0,0,8.4-3,20-3s20,3,20,3V9c0,0-6.7,3-20,3S4,9,4,9z"/>
        <path fill="#942A09" d="M24,34c0.1,0,0.3,0,0.4,0L15,19L6.9,36.2C10.3,35.3,16.5,34,24,34z"/>
        <path fill="#BF360C" d="M24,34c3.3,0,6.3,0.2,9,0.6l-8-11.8l-7.8,11.5C19.3,34.1,21.6,34,24,34z"/>
        <path fill="#E65100" d="M40.7,36L35,26.5l-5,7.8C34.5,34.7,38.2,35.4,40.7,36z"/>
        <ellipse fill="#FFF9C4" cx="36" cy="19.5" rx="2" ry="2.5"/>
        </svg>
        """,
            attributes=[
                Attribute(
                    type=AttributeType.ATTRIBUTE_TYPE_RECORDING_ID,
                    id="recordingid",
                    display_name="Recording",
                ),
                Attribute(
                    type=AttributeType.ATTRIBUTE_TYPE_FOLDER,
                    id="outputfolder",
                    display_name="Output folder",
                ),
                Attribute(
                    type=AttributeType.ATTRIBUTE_TYPE_MEDIA_SERVER_CONNECTION,
                    id="media_server",
                    display_name="Media Server",
                    sensitive=True,
                ),
                Attribute(
                    type=AttributeType.ATTRIBUTE_TYPE_RECORDINGS_SERVER_CONNECTION,
                    id="recordings_server",
                    display_name="Recordings Server",
                    sensitive=True,
                ),
            ],
        )
        self.client = ServiceClient(service, url)
        self.client_thread = threading.Thread()

    def run(self) -> None:
        logger.info(f"{self.service_id} -> Starting")
        self.client_thread = threading.Thread(
            target=self.client_job_listener,
            daemon=True
        )
        self.client_thread.start()
        self.work()

    def stop(self) -> None:
        logger.info(f"{self.service_id} -> Stopping")
        self.client.close()
        self.client_thread.join()

    def client_job_listener(self):
        self.client.open()
        self.client.register()
        with self.client.consume() as consumer:
            for msg, ack in consumer:
                self.work_queue.put((msg, ack))
        logger.info(f"{self.service_id} -> client job listener stopped")

    def work(self):
        logger.info(f"{self.service_id} -> Starting work queue")
        # consume work
        with (
            ThreadPoolExecutor(max_workers=1) as executor,
        ):
            while True:
                item, ack = self.work_queue.get()
                logger.debug(f"{self.service_id} -> Received message")
                logger.debug(f"{pformat(item)}")

                if item.request.type == MessageType.MESSAGE_TYPE_PUBLISH_JOB:
                    # work = Panorama(item, )
                    # work.execute()
                    executor.submit(self._execute, item.request.publish_job, ack)

    def _execute(self, job: PublishJob, ack: Ack):
        try:
            panorama = Panorama(job, self.client.publish_event)
            panorama.execute()

        except Exception as err:
            logger.error(f"{self.service_id} -> {pformat(err)}")
            logger.error("".join(traceback.format_exception(err)))
            ack.cancel()

def main() -> int:
    args = parse_cli_arguments(sys.argv[1:])

    logging.basicConfig(style="{")
    logging.getLogger("mercaido_panorama").setLevel(logging.INFO)

    service = PanoramaService(
        "horus.mercaido.panorama", args.amqp
    )

    try:
        service.run()
    except KeyboardInterrupt:
        service.stop()


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
