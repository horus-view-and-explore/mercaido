# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from typing import Optional

from pyramid.interfaces import IRequest

from mercaido_client.pb.mercaido import Service

from . import Card


class ServiceCard(Card):
    _service: Service

    def __init__(self, request: IRequest, service: Optional[Service]) -> None:
        self._service = service
        super().__init__(request)

    @property
    def service(self) -> Service:
        return self._service

    def title(self) -> str:
        return self.service.name

    def description(self) -> str:
        return self.service.description

    def svg(self) -> str:
        return self.service.svg

    def endpoint(self) -> str:
        return self.request.route_path("service", service=self.service.endpoint)
