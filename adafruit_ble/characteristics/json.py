# SPDX-FileCopyrightText: 2022 Mark Raleson
#
# SPDX-License-Identifier: MIT

"""
`json`
====================================================

This module provides a JSON characteristic for reading/writing JSON serializable Python values.

"""

from __future__ import annotations

import json

from . import Attribute, Characteristic

try:
    from typing import TYPE_CHECKING, Any, Optional, Type

    if TYPE_CHECKING:
        from circuitpython_typing import ReadableBuffer

        from adafruit_ble.services import Service
        from adafruit_ble.uuid import UUID

except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class JSONCharacteristic(Characteristic):
    """JSON string characteristic for JSON serializable values of a limited size (max_length)."""

    def __init__(
        self,
        *,
        uuid: Optional[UUID] = None,
        properties: int = Characteristic.READ,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        initial_value: Optional[ReadableBuffer] = None,
    ) -> None:
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
    def pack(value: Any) -> bytes:
        """Converts a JSON serializable python value into a utf-8 encoded JSON string."""
        return json.dumps(value).encode("utf-8")

    @staticmethod
    def unpack(value: ReadableBuffer) -> Any:
        """Converts a utf-8 encoded JSON string into a python value."""
        return json.loads(str(value, "utf-8"))

    def __get__(self, obj: Optional[Service], cls: Optional[Type[Service]] = None) -> Any:
        if obj is None:
            return self
        return self.unpack(super().__get__(obj, cls))

    def __set__(self, obj: Service, value: Any) -> None:
        super().__set__(obj, self.pack(value))
