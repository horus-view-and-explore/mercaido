# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

# FIXME: All modules can be moved into one module.

import logging

from sqlalchemy import engine_from_config, Engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry
from sqlalchemy.orm import sessionmaker, Session, configure_mappers
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, ISettings

import zope.sqlalchemy

# Import models here to make sure they are attached to `Base.metadata` before
# any initialisation routines.
# The `noqa: F401` comment after each line is to tell Ruff to stop complaining
from .mediaserver import MediaServer  # noqa: F401
from .recordingserver import RecordingServer  # noqa: F401
from .job import Job  # noqa: F401
from .service import Service  # noqa: F401
from .featureserver import FeatureServer  # noqa: F401


logger = logging.getLogger(__name__)

configure_mappers()


@event.listens_for(Engine, "connect")
def setup_sqlite(connection: DBAPIConnection, connection_record: ConnectionPoolEntry):
    logger.info("Setting up SQLite")
    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine(settings: ISettings, prefix="sqlalchemy.") -> Engine:
    return engine_from_config(settings, prefix)


def get_session_factory(engine: Engine) -> sessionmaker:
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(
    session_factory: sessionmaker, transaction_manager, request: IRequest = None
) -> Session:
    dbsession = session_factory(info={"request": request})
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config: Configurator) -> None:
    """
    Initialize the models
    """

    settings = config.get_settings()
    settings["tm.manager_hook"] = "pyramid_tm.explicit_manager"

    config.include("pyramid_tm")
    config.include("pyramid_retry")
    dbengine = settings.get("dbengine")
    if not dbengine:
        dbengine = get_engine(settings)

    session_factory = get_session_factory(dbengine)
    config.registry["dbsession_factory"] = session_factory

    def dbsession(request: IRequest) -> Session:
        dbsession = request.environ.get("app.dbsession")
        if dbsession is None:
            dbsession = get_tm_session(session_factory, request.tm, request=request)

        return dbsession

    config.add_request_method(dbsession, reify=True)
