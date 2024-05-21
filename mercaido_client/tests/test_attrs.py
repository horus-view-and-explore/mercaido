# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import pytest

from mercaido_client.attrs import AttrDict


def test_attrdict():
    d = AttrDict()
    d.a = 1
    assert "a" in d
    d["b"] = 1
    assert "b" in d
    d.c = {"x": 2}
    assert d.c.x == 2


def test_attrdict_missing_attr():
    d = AttrDict()

    with pytest.raises(AttributeError):
        d.a
