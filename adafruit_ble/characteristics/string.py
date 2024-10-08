# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`string`
====================================================

This module provides string characteristics.

"""

from __future__ import annotations

from . import Attribute, Characteristic

TYPE_CHECKING = False
try:
    from typing import TYPE_CHECKING, Optional, Type, Union, overload

    if TYPE_CHECKING:
        from circuitpython_typing import ReadableBuffer

        from adafruit_ble.services import Service
        from adafruit_ble.uuid import StandardUUID, VendorUUID

        Uuid = Union[StandardUUID, VendorUUID]

except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class StringCharacteristic(Characteristic):
    """UTF-8 Encoded string characteristic."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        uuid: Optional[Uuid] = None,
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
            initial_value=initial_value,
        )

    if TYPE_CHECKING:

        @overload
        def __get__(
            self, obj: None, cls: Optional[Type[Service]] = None
        ) -> Characteristic:
            ...

        @overload
        def __get__(self, obj: Service, cls: Optional[Type[Service]] = None) -> str:
            ...

    def __get__(
        self, obj: Optional[Service], cls: Optional[Type[Service]] = None
    ) -> Union[Characteristic, str]:
        if obj is None:
            return self
        return str(super().__get__(obj, cls), "utf-8")

    def __set__(self, obj: Service, value: str) -> None:
        super().__set__(obj, value.encode("utf-8"))


class FixedStringCharacteristic(Characteristic):
    """Fixed strings are set once when bound and unchanged after."""

    def __init__(
        self, *, uuid: Optional[Uuid] = None, read_perm: int = Attribute.OPEN
    ) -> None:
        super().__init__(
            uuid=uuid,
            properties=Characteristic.READ,
            read_perm=read_perm,
            write_perm=Attribute.NO_ACCESS,
            fixed_length=True,
        )

    if TYPE_CHECKING:

        @overload
        def __get__(
            self, obj: None, cls: Optional[Type[Service]] = None
        ) -> Characteristic:
            ...

        @overload
        def __get__(self, obj: Service, cls: Optional[Type[Service]] = None) -> str:
            ...

    def __get__(
        self, obj: Optional[Service], cls: Optional[Type[Service]] = None
    ) -> Union[Characteristic, str]:
        if obj is None:
            return self
        return str(super().__get__(obj, cls), "utf-8")
