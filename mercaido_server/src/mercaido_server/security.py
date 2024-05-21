# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.config import Configurator


def includeme(config: Configurator):
    config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    config.set_default_csrf_options(require_csrf=True)
