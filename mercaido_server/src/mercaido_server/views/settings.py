# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import sqlalchemy as sa

from pyramid.view import view_config
from pyramid.interfaces import IResponse, IRequest

from ..models import Service, MediaServer, RecordingServer, FeatureServer


class SettingsViews:
    request: IRequest

    def __init__(self, request: IRequest) -> None:
        self.request = request

    @view_config(
        route_name="settings", renderer="mercaido_server:templates/settings.jinja2"
    )
    def index(self) -> IResponse:
        media_servers = self.request.dbsession.scalar(
            sa.select(sa.func.count(MediaServer.id))
        )
        recording_servers = self.request.dbsession.scalar(
            sa.select(sa.func.count(RecordingServer.id))
        )
        feature_servers = self.request.dbsession.scalar(
            sa.select(sa.func.count(FeatureServer.id))
        )

        return dict(media_servers=media_servers, recording_servers=recording_servers, feature_servers=feature_servers)
