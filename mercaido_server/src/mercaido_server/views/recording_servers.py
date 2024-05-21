# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.view import view_config
from pyramid.interfaces import IResponse, IRequest
from pyramid.httpexceptions import HTTPSeeOther, HTTPMethodNotAllowed
from sqlalchemy import select

from .. import models


class RecordingServerViews:
    request: IRequest

    def __init__(self, request: IRequest) -> None:
        self.request = request

    @view_config(
        route_name="recording_servers",
        renderer="mercaido_server:templates/settings/recordingservers/index.jinja2",
    )
    def index(self) -> IResponse:
        recordingserver = self.request.dbsession.scalars(
            select(models.RecordingServer).limit(1)
        ).first()

        next_url = self.request.route_url("recording_servers_new")

        if recordingserver is not None:
            next_url = self.request.route_url(
                "recording_servers_edit", id=recordingserver.id
            )

        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="recording_servers_new",
        renderer="mercaido_server:templates/settings/recordingservers/form.jinja2",
    )
    def new(self) -> IResponse:
        recordingserver = models.RecordingServer()

        if self.request.method == "POST":
            recordingserver.host = self.request.params["host"]
            recordingserver.port = self.request.params["port"]
            recordingserver.database = self.request.params["database"]
            recordingserver.username = self.request.params["username"]
            recordingserver.password = self.request.params["password"]

            self.request.dbsession.add(recordingserver)
            next_url = self.request.route_url("recording_servers")
            return HTTPSeeOther(location=next_url)

        return dict(recordingserver=recordingserver)

    @view_config(
        route_name="recording_servers_edit",
        renderer="mercaido_server:templates/settings/recordingservers/form.jinja2",
    )
    def edit(self) -> IResponse:
        msid = int(self.request.matchdict["id"])
        recordingserver = self.request.dbsession.get(models.RecordingServer, msid)

        if self.request.method == "POST":
            recordingserver.host = self.request.params["host"]
            recordingserver.port = self.request.params["port"]
            recordingserver.database = self.request.params["database"]
            recordingserver.username = self.request.params["username"]
            recordingserver.password = self.request.params["password"]

            next_url = self.request.route_url("recording_servers")
            return HTTPSeeOther(location=next_url)

        return dict(recordingserver=recordingserver)

    @view_config(route_name="recording_servers_delete")
    def delete(self) -> IResponse:
        rsid = int(self.request.matchdict["id"])
        recordingserver = self.request.dbsession.get(models.RecordingServer, rsid)

        if self.request.method == "POST":
            self.request.dbsession.delete(recordingserver)
            next_url = self.request.route_url("recording_servers")
            return HTTPSeeOther(location=next_url)

        return HTTPMethodNotAllowed()
