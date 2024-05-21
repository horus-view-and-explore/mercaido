# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import secrets
import shutil
import string
import subprocess
import threading
import time
import logging
from typing import NamedTuple

import pika
import pika.exceptions
import pytest


RABBITMQ_DEFAULT_AMQP_PORT = 5672
RABBITMQ_DEFAULT_HTTP_PORT = 15672


@pytest.fixture(scope="session")
def rabbitmq_server():
    server = RabbitMQServer(RABBITMQ_DEFAULT_HTTP_PORT, RABBITMQ_DEFAULT_AMQP_PORT)
    server.start()
    try:
        yield server.connection_details
    finally:
        server.stop()


class RabbitMQServer:
    class ConnectionDetails(NamedTuple):
        host: str
        amqp_port: int
        http_port: int

        def url(self):
            return f"amqp://guest:guest@{self.host}:{self.amqp_port}/%2F"

    _proc: None | subprocess.Popen
    _thread: None | threading.Thread

    def __init__(self, http_port: int, amqp_port: int) -> None:
        self._proc = None
        self._thread = None
        logger_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        self._logger = logging.getLogger(logger_name)

        self._man = self._get_container_manager()
        self._name = f"rabbitmq-{random_string()}"
        self._cmd = [
            *self._man,
            "run",
            "--rm",
            "--quiet",
            "--name",
            self._name,
            "-p",
            f"15672:{http_port}",
            "-p",
            f"5672:{amqp_port}",
            "docker.io/rabbitmq:3-management",
        ]

        self.connection_details = self.ConnectionDetails(
            "127.0.0.1",
            amqp_port,
            http_port,
        )

    def start(self) -> None:
        if self._proc is not None:
            raise RuntimeError("server is already running")

        self._proc = subprocess.Popen(
            self._cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self._thread = threading.Thread(
            target=self._collect_stdout,
            args=(self._proc, self._logger),
        )
        self._thread.start()

        result = _wait_for_server_bootup(self.connection_details.url())
        if not result:
            raise RuntimeError("RabbitMQ was unable to start.")

    def stop(self) -> None:
        if self._proc is None:
            raise RuntimeError("server is NOT running")
        assert self._thread is not None

        self._proc.terminate()

        try:
            self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._proc.kill()

        self._thread.join()

        self._proc = None
        self._thread = None

    @staticmethod
    def _get_container_manager() -> list[str]:
        cmd = shutil.which("podman") or shutil.which("docker")
        if cmd is None:
            raise RuntimeError("cannot find Docker or Podman")
        return [cmd]

    @staticmethod
    def _collect_stdout(proc: subprocess.Popen, logger: logging.Logger) -> None:
        if proc.stdout is None:
            raise RuntimeError("proc has no stdout?")
        for line in iter(proc.stdout.readline, b""):
            logger.debug(line.decode("utf-8"))


def random_string(n: int = 7) -> str:
    return "".join(
        secrets.choice(string.ascii_uppercase + string.ascii_lowercase)
        for i in range(n)
    )


def _wait_for_server_bootup(url: str, retries: int=15) -> bool:
    params = pika.URLParameters(url)
    is_connected = False

    for n in range(retries):
        try:
            conn = pika.BlockingConnection(params)
            if conn.is_open:
                conn.close()
                is_connected = True
                break
        except pika.exceptions.AMQPConnectionError:
            time.sleep(1)

    return is_connected
