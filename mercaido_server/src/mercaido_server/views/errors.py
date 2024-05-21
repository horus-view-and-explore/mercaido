# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.view import notfound_view_config
from pyramid.interfaces import IRequest, IResponse


@notfound_view_config(renderer="mercaido_server:templates/404.jinja2")
def notfound(request: IRequest) -> IResponse:
    request.response.status = 404
    return {}
