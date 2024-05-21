# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from . import Card


class MediaServerCard(Card):  # FIXME: Rename to MediaServerCard
    def title(self) -> str:
        return "Media Server"

    def description(self) -> str:
        return "Configure the connection to the Horus Media Server"

    def svg(self) -> str:
        return """<svg viewBox="0 0 64 64" version="1.0" xmlns="http://www.w3.org/2000/svg" style="background-color: #ffffff;">
          <rect x="16" y="16" width="32" height="32" fill="#2ea3f2" />
        </svg>"""

    def endpoint(self) -> str:
        return self.request.route_path("media_servers")
