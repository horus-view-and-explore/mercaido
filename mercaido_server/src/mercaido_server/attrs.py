# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

class AttrDict(dict):
    def __getattr__(self, key):
        try:
            value = self.__getitem__(key)
            if value.__class__ != self.__class__ and value.__class__ == dict:
                self[key] = value = self.__class__(value)
            return value
        except KeyError:
            raise AttributeError(f"{key} not in {self.keys()}")

    def __setattr__(self, key, value):
        self.__setitem__(key, value)
