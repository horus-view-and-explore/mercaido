# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.view import view_config
from pyramid.interfaces import IResponse, IRequest
from pyramid.httpexceptions import HTTPSeeOther, HTTPMethodNotAllowed
from sqlalchemy import select

from .. import models


class MediaServerViews:
    request: IRequest

    def __init__(self, request: IRequest) -> None:
        self.request = request

    @view_config(
        route_name="media_servers",
        renderer="mercaido_server:templates/settings/mediaservers/index.jinja2",
    )
    def index(self) -> IResponse:
        mediaserver = self.request.dbsession.scalars(
            select(models.MediaServer).limit(1)
        ).first()

        next_url = self.request.route_url("media_servers_new")

        if mediaserver is not None:
            next_url = self.request.route_url("media_servers_edit", id=mediaserver.id)

        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="media_servers_new",
        renderer="mercaido_server:templates/settings/mediaservers/form.jinja2",
    )
    def new(self) -> IResponse:
        mediaserver = models.MediaServer()

        if self.request.method == "POST":
            mediaserver.endpoint = self.request.params["endpoint"]
            self.request.dbsession.add(mediaserver)
            next_url = self.request.route_url("media_servers")
            return HTTPSeeOther(location=next_url)

        return dict(mediaserver=mediaserver)

    @view_config(
        route_name="media_servers_edit",
        renderer="mercaido_server:templates/settings/mediaservers/form.jinja2",
    )
    def edit(self) -> IResponse:
        msid = int(self.request.matchdict["id"])
        mediaserver = self.request.dbsession.get(models.MediaServer, msid)

        if self.request.method == "POST":
            mediaserver.endpoint = self.request.params["endpoint"]
            next_url = self.request.route_url("media_servers")
            return HTTPSeeOther(location=next_url)

        return dict(mediaserver=mediaserver)

    @view_config(route_name="media_servers_delete")
    def delete(self) -> IResponse:
        msid = int(self.request.matchdict["id"])
        mediaserver = self.request.dbsession.get(models.MediaServer, msid)

        if self.request.method == "POST":
            self.request.dbsession.delete(mediaserver)
            next_url = self.request.route_url("media_servers")
            return HTTPSeeOther(location=next_url)

        return HTTPMethodNotAllowed()
