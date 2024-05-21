#!/usr/bin/env python3

import shutil
import subprocess
import sys


def main():
    if not (shutil.which("podman") or shutil.which("docker")):
        print("WARNING: podman/docker not found, it is used to run RabbitMQ.")

    # Handle subcommands.
    match sys.argv[1:]:
        case ["rabbitmq", "start", *args]:
            run(rabbitmq_start_command())

        case ["rabbitmq", "stop", *args]:
            run(rabbitmq_stop_command())

        case _:
            print(f"usage: {sys.argv[0]} ...")
            print("    rabbitmq start | stop    Stop and stop rabbitmq in Background.")


def run(args):
    cp = subprocess.run(args)
    if cp.returncode != 0:
        sys.exit(cp.returncode)


def rabbitmq_start_command():
    cmd = ["docker"]
    podman_cmd = shutil.which("podman")
    if podman_cmd:
        cmd = [podman_cmd, "container"]

    cmd.extend(
        [
            "run",
            "--rm",
            "--detach",
            "--name",
            "mercaido_rabbitmq",
            "-p",
            "15672:15672",
            "-p",
            "5672:5672",
            "docker.io/rabbitmq:3-management",
        ]
    )

    return cmd


def rabbitmq_stop_command():
    cmd = ["docker"]

    podman = shutil.which("podman")
    if podman:
        cmd = [podman, "container"]

    cmd.extend(["stop", "mercaido_rabbitmq"])

    return cmd


if __name__ == "__main__":
    main()
