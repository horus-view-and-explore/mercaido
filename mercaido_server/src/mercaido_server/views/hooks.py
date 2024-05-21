# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from pyramid.events import subscriber, BeforeRender

from sqlalchemy import select, or_

from .. import models

from pprint import pprint


@subscriber(BeforeRender)
def load_jobs(event: BeforeRender) -> None:
    if "jobs" not in event.rendering_val:
        request = event.get("request")
        jobs = request.dbsession.scalars(
            select(models.Job)
            .where(or_(models.Job.finished_at == None, models.Job.error == True))
            .order_by(models.Job.started_at)
        ).all()
        jobs = [j.as_dict() for j in jobs]  # XXX: Encode to JSON.
        event.rendering_val["jobs"] = jobs
