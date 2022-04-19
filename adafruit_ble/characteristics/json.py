# SPDX-FileCopyrightText: 2022 Mark Raleson
#
# SPDX-License-Identifier: MIT

"""
`json`
====================================================

This module provides a JSON characteristic for reading/writing JSON serializable Python values.

"""

import json
from . import Attribute
from . import Characteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class JSONCharacteristic(Characteristic):
    """JSON string characteristic for JSON serializable values of a limited size (max_length)."""

    def __init__(
        self,
        *,
        uuid=None,
        properties=Characteristic.READ,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        initial_value=None,
    ):
        super().__init__(
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            max_length=512,
            fixed_length=False,
            initial_value=self.pack(initial_value),
        )

    @staticmethod
    def pack(value):
        """Converts a JSON serializable python value into a utf-8 encoded JSON string."""
        return json.dumps(value).encode("utf-8")

    @staticmethod
    def unpack(value):
        """Converts a utf-8 encoded JSON string into a python value."""
        return json.loads(str(value, "utf-8"))

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return self.unpack(super().__get__(obj, cls))

    def __set__(self, obj, value):
        super().__set__(obj, self.pack(value))
