# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`string`
====================================================

This module provides string characteristics.

"""

from . import Attribute
from . import Characteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class StringCharacteristic(Characteristic):
    """UTF-8 Encoded string characteristic."""

    def __init__(
        self,
        *,
        uuid=None,
        properties=Characteristic.READ,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        initial_value=None
    ):
        super().__init__(
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            max_length=512,
            fixed_length=False,
            initial_value=initial_value,
        )

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return str(super().__get__(obj, cls), "utf-8")

    def __set__(self, obj, value):
        super().__set__(obj, value.encode("utf-8"))


class FixedStringCharacteristic(Characteristic):
    """Fixed strings are set once when bound and unchanged after."""

    def __init__(self, *, uuid=None, read_perm=Attribute.OPEN):
        super().__init__(
            uuid=uuid,
            properties=Characteristic.READ,
            read_perm=read_perm,
            write_perm=Attribute.NO_ACCESS,
            fixed_length=True,
        )

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return str(super().__get__(obj, cls), "utf-8")
