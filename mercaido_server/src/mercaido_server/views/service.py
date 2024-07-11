# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from typing import Any
from functools import reduce

import sqlalchemy as sa
from pyramid.view import view_config
from pyramid.interfaces import IResponse, IRequest
from pyramid.httpexceptions import HTTPSeeOther, HTTPNotFound

import mercaido_client.pb.mercaido as messages

from psycopg2 import connect, OperationalError
from horus_db import Recordings, Recording

from google.protobuf.json_format import MessageToDict

from .. import models


class ServiceViews:
    request: IRequest

    def __init__(self, context, request: IRequest) -> None:
        self.context = context
        self.request = request

    @view_config(
        route_name="service",
        renderer="mercaido_server:templates/service.jinja2",
    )
    def show(self) -> IResponse:
        service_id = self.request.matchdict["service"]
        service = self.request.dbsession.scalar(
            sa.select(models.Service).where(models.Service.ident == service_id),
        )

        if service is None:
            raise HTTPNotFound()

        service = service.data

        if self.request.method == "POST":
            self._create_job(service, self.request.params.dict_of_lists())
            next_url = self.request.route_url("service", service=service_id)
            return HTTPSeeOther(location=next_url)

        mediaserver = self.request.dbsession.scalars(
            sa.select(models.MediaServer).limit(1)
        ).first()
        recordingserver = self.request.dbsession.scalars(
            sa.select(models.RecordingServer).limit(1)
        ).first()
        featureserver = self.request.dbsession.scalars(
            sa.select(models.FeatureServer).limit(1)
        ).first()
        recordings = None

        if recordingserver is not None:
            recordings = self._get_recordings(recordingserver.connection_string)

        return {
            "service": service,
            "mediaserver": mediaserver,
            "recordingserver": recordingserver,
            "featureserver": featureserver,
            "recordings": recordings,
        }

    def _create_job(self, service: messages.Service, params: dict[str, Any]) -> None:
        # FIXME: It's a bit weird to reuse an unrelated object (service)
        # to fill another object (publish_job). Bug-prone I guess.
        for attr in service.attributes:
            if attr.type == messages.AttributeType.ATTRIBUTE_TYPE_BOOLEAN:
                attr.values = [str(attr.id in params)]
            elif attr.type == messages.AttributeType.ATTRIBUTE_TYPE_FEATURESERVER:
                attr.values = self._feature_server_tuple(int(params[attr.id][0]))
            else:
                attr.values = params[attr.id]

        job = self.request.dbsession.scalars(
            sa.insert(models.Job).returning(models.Job),
            [
                {
                    "service_id": service.endpoint,
                    # XXX: Can also use the protobuf encode/decode column type.
                    "attributes": self._attributes_to_dict(service.attributes),
                }
            ],
        )

        publish_job = messages.PublishJob(
            job_id=job.first().id,
            services=[service],
        )

        with self.request.publish_job_client() as client:
            client.publish(service.endpoint, publish_job)

        for attr in service.attributes:
            attr.values = []

    def _get_recordings(self, connection_string: str) -> list[Recording] | None:
        try:
            connection = connect(connection_string)
            recordings = []
            cursor = Recordings(connection).all()
            recording = Recording(cursor)

            while recording is not None:
                recordings.append(dict(id=recording.id, text=recording.directory))
                recording = Recording(cursor)

            recordings.sort(key=lambda r: r["text"])
            return recordings
        except OperationalError as e:
            print(f"Error connecting to recording server: {e}")
            return None

    def _attributes_to_dict(
        self, attributes: list[messages.Attribute]
    ) -> dict[str, Any]:
        def deconstruct_attribute(result, attr):
            if not attr.sensitive:
                result[attr.id] = {
                    "type": attr.type,
                    "displayName": attr.display_name,
                    "values": [value for value in attr.values],
                }
            return result

        return reduce(deconstruct_attribute, attributes, {})

    def _feature_server_tuple(self, id: int) -> list[str]:
        featureserver = self.request.dbsession.get(models.FeatureServer, id)
        attrs = {
            "wfs_endpoint": featureserver.endpoint,
            "server_type": featureserver.server_type,
        }

        attrs |= featureserver.attributes

        return [item for prop in attrs.items() for item in prop]
