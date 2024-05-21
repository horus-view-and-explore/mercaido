# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.config import Configurator


def includeme(config: Configurator):
    config.add_static_view(
        name="static", path="mercaido_server:static", cache_max_age=14400
    )
    config.add_route("home", "/")
    config.add_route("media_servers", "/settings/media_servers")
    config.add_route("media_servers_new", "/settings/media_servers/new")
    config.add_route("media_servers_edit", "/settings/media_servers/{id}/edit")
    config.add_route("media_servers_delete", "/settings/media_servers/{id}/delete")
    config.add_route("recording_servers", "/settings/recording_servers")
    config.add_route("recording_servers_new", "/settings/recording_servers/new")
    config.add_route("recording_servers_edit", "/settings/recording_servers/{id}/edit")
    config.add_route(
        "recording_servers_delete", "/settings/recording_servers/{id}/delete"
    )
    config.add_route("service", "/service/{service}")
    config.add_route("job_events", "/events/job")
    config.add_route("job_clear_finished", "/jobs/clear/finished")
    config.add_route("job_delete", "/jobs/{id}/delete")
