# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

"""Horus Mercaido"""
from __future__ import annotations

from typing import Any

from pyramid.config import Configurator
from pyramid.interfaces import ISettings

__version__ = "0.1.0"


def main(global_config: Any, **settings: ISettings):
    with Configurator(settings=settings) as config:
        config.include("pyramid_jinja2")
        # config.include(".registry")
        config.include(".security")
        config.include(".mq")
        config.include(".routes")
        config.include(".models")
        config.scan(".views")

    return config.make_wsgi_app()
