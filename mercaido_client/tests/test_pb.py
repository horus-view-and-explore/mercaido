# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from mercaido_client.pb.mercaido import (
    AttributeType,
    Attribute,
    MessageBase,
    PublishJob,
    RegisterServices,
    RequestBase,
    ResponseBase,
    Service,
)


def test_init():
    Attribute(type=AttributeType.ATTRIBUTE_TYPE_TEXT)
    MessageBase()
    PublishJob(job_id="42")
    RegisterServices()
    RequestBase()
    ResponseBase()
    Service()
