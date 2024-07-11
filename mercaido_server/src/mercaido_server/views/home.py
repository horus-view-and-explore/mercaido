# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import sqlalchemy as sa
from pyramid.view import view_config
from pyramid.interfaces import IRequest, IResponse

from ..models import Service, MediaServer, RecordingServer, FeatureServer

from .cards.service import ServiceCard


@view_config(route_name="home", renderer="mercaido_server:templates/home.jinja2")
def home(request: IRequest) -> IResponse:
    services = request.dbsession.scalars(
        sa.select(Service).order_by(Service.ident)
    ).all()
    service_cards = [ServiceCard(request, service.data) for service in services]

    media_servers = request.dbsession.scalar(sa.select(sa.func.count(MediaServer.id)))
    recording_servers = request.dbsession.scalar(
        sa.select(sa.func.count(RecordingServer.id))
    )
    feature_servers = request.dbsession.scalar(
        sa.select(sa.func.count(FeatureServer.id))
    )

    configured = (
        (media_servers > 0) and (recording_servers > 0) and (feature_servers > 0)
    )

    return {
        "configured": configured,
        "media_servers": media_servers > 0,
        "recording_servers": recording_servers > 0,
        "feature_servers": feature_servers > 0,
        "service_cards": service_cards,
    }
