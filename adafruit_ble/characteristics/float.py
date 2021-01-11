# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`float`
====================================================

This module provides float characteristics that are usable directly as attributes.

"""

from . import Attribute
from . import StructCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class FloatCharacteristic(StructCharacteristic):
    """32-bit float"""

    def __init__(
        self,
        *,
        uuid=None,
        properties=0,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        initial_value=None
    ):
        if initial_value is not None:
            initial_value = (initial_value,)
        super().__init__(
            "<f",
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            initial_value=initial_value,
        )

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return super().__get__(obj)[0]

    def __set__(self, obj, value):
        super().__set__(obj, (value,))
