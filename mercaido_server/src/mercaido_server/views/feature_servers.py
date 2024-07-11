# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.view import view_config
from pyramid.interfaces import IResponse, IRequest
from pyramid.httpexceptions import HTTPSeeOther, HTTPMethodNotAllowed, HTTPNotFound
from sqlalchemy import select

from mercaido_client.gis import FeatureServerClient

from .. import models


class FeatureServerViews:
    request: IRequest

    def __init__(self, request: IRequest) -> None:
        self.request = request

    @view_config(
        route_name="feature_servers",
        renderer="mercaido_server:templates/settings/featureservers/index.jinja2",
    )
    def index(self) -> IResponse:
        featureserver = self.request.dbsession.scalars(
            select(models.FeatureServer).limit(1)
        ).first()

        next_url = self.request.route_url("feature_servers_new")

        if featureserver is not None:
            next_url = self.request.route_url(
                "feature_servers_edit", id=featureserver.id
            )

        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="feature_servers_new",
        renderer="mercaido_server:templates/settings/featureservers/form.jinja2",
    )
    def new(self) -> IResponse:
        featureserver = models.FeatureServer()

        if self.request.method == "POST":
            featureserver.server_type = self.request.params["server_type"]
            featureserver.name = self.request.params["name"]
            featureserver.endpoint = self.request.params["endpoint"]
            featureserver.attributes = {}
            if featureserver.server_type == "geoserver":
                featureserver.attributes["geoserver_workspace"] = self.request.params[
                    "geoserver_workspace"
                ]
                featureserver.attributes["geoserver_datastore"] = self.request.params[
                    "geoserver_datastore"
                ]
            self.request.dbsession.add(featureserver)
            next_url = self.request.route_url("feature_servers")
            return HTTPSeeOther(location=next_url)

        return dict(featureserver=featureserver)

    @view_config(
        route_name="feature_servers_edit",
        renderer="mercaido_server:templates/settings/featureservers/form.jinja2",
    )
    def edit(self) -> IResponse:
        msid = int(self.request.matchdict["id"])
        featureserver = self.request.dbsession.get(models.FeatureServer, msid)

        if self.request.method == "POST":
            featureserver.server_type = self.request.params["server_type"]
            featureserver.name = self.request.params["name"]
            featureserver.endpoint = self.request.params["endpoint"]
            featureserver.attributes = {}
            if featureserver.server_type == "geoserver":
                featureserver.attributes["geoserver_workspace"] = self.request.params[
                    "geoserver_workspace"
                ]
                featureserver.attributes["geoserver_datastore"] = self.request.params[
                    "geoserver_datastore"
                ]
            next_url = self.request.route_url("feature_servers")
            return HTTPSeeOther(location=next_url)

        return dict(featureserver=featureserver)

    @view_config(route_name="feature_servers_delete")
    def delete(self) -> IResponse:
        msid = int(self.request.matchdict["id"])
        featureserver = self.request.dbsession.get(models.FeatureServer, msid)

        if self.request.method == "POST":
            self.request.dbsession.delete(featureserver)
            next_url = self.request.route_url("feature_servers")
            return HTTPSeeOther(location=next_url)

        return HTTPMethodNotAllowed()

    @view_config(
        route_name="feature_servers_layers",
        renderer="mercaido_server:templates/settings/featureservers/layers.jinja2",
    )
    def layers(self) -> IResponse:
        fsid = int(self.request.matchdict["id"])
        featureserver = self.request.dbsession.get(models.FeatureServer, fsid)

        if featureserver is None:
            return HTTPNotFound()

        client = FeatureServerClient(featureserver.endpoint)

        client.open()
        layers = client.get_layers()

        return dict(client=client, layers=layers, featureserver=featureserver)
