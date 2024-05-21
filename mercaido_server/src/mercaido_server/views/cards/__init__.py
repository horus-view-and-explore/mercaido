# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from pyramid.interfaces import IRequest


# FIXME: All modules can be moved into one module.


class Card(ABC):
    _request: IRequest

    def __init__(self, request: IRequest) -> None:
        self._request = request
        super().__init__()

    @property
    def request(self) -> IRequest:
        return self._request

    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def svg(self) -> str:
        pass

    @abstractmethod
    def endpoint(self) -> str:
        pass
