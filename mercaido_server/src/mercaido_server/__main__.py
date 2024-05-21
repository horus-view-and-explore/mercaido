# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import argparse
import sys
from pathlib import Path

import alembic
import alembic.command
import alembic.config
from pika.exchange_type import ExchangeType
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from mercaido_client.mq.client import (
    BlockingClient,
    MAIN_EXCHANGE,
    EVENTS_EXCHANGE,
    DISPATCHER_QUEUE,
)

from .attrs import AttrDict
from .models.meta import Base as BaseModel
from .dispatcher import Dispatcher


def main():
    args = parse_cli_arguments(sys.argv[1:])

    try:
        if not args.config.exists():
            raise CommandError(f"does not exist: {args.config}")
        setup_logging(str(args.config))
        settings = get_appsettings(str(args.config))
        ctx = AttrDict(args=args, settings=settings)
        args.func(ctx)
    except CommandError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def parse_cli_arguments(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser("mercaido_server")

    parser.add_argument(
        "-c",
        "--config",
        type=abspath,
        help="path to configuration file.",
        required=True,
    )

    subparsers = parser.add_subparsers(required=True)

    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations.")
    migrate_parser.set_defaults(func=migrate)

    message_queue_migrate_parser = subparsers.add_parser(
        "message-queue-migrate",
        help="Initialize or update message exchanges and queues.",
    )
    message_queue_migrate_parser.set_defaults(func=message_queue_migrate)

    dispatcher_parser = subparsers.add_parser("dispatcher", help="Run dispatcher process.")
    dispatcher_parser.set_defaults(func=dispatcher_command)

    parsed_args = parser.parse_args(args)

    return parsed_args


class CommandError(Exception):
    pass


def abspath(s: str) -> Path:
    return Path(s).absolute()


def migrate(ctx: AttrDict):
    cfg = alembic.config.Config(str(ctx.args.config))

    # These two settins don't change.
    cfg.set_main_option("script_location", "mercaido_server:migrations")
    cfg.set_main_option("file_template", "%%(year)d%%(month).2d%%(day).2d_%%(rev)s")

    engine = engine_from_config(ctx.settings)

    with engine.begin() as connection:
        # Pass connection to Alembic environment.
        cfg.attributes["connection"] = connection
        # Run migration.
        alembic.command.upgrade(cfg, "head")


def message_queue_migrate(ctx: AttrDict) -> None:
    # XXX: This migrate command does no migration yet. We'll handle
    # migration manually here, I guess.

    with BlockingClient(ctx.settings["amqp.url"]) as client:
        client.exchange(
            MAIN_EXCHANGE.name,
            MAIN_EXCHANGE.type,
            MAIN_EXCHANGE.durable,
        )
        client.exchange(
            EVENTS_EXCHANGE.name,
            EVENTS_EXCHANGE.type,
            EVENTS_EXCHANGE.durable,
        )
        client.queue(
            DISPATCHER_QUEUE.name,
            DISPATCHER_QUEUE.exchange,
            binding_keys=DISPATCHER_QUEUE.binding_keys,
        )


def dispatcher_command(ctx: AttrDict) -> None:
    dispatcher = Dispatcher(
        ctx.settings["amqp.url"],
        ctx.settings["sqlalchemy.url"],
    )

    try:
        dispatcher.run()
    except KeyboardInterrupt:
        dispatcher.stop()


if __name__ == "__main__":
    main()
