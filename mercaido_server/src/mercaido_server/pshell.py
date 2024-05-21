# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from . import models


def setup(env):
    request = env["request"]

    request.tm.begin()

    env["tm"] = request.tm
    env["dbsession"] = request.dbsession
    env["models"] = models
