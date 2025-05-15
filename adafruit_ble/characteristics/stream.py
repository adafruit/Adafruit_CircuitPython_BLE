# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`stream`
====================================================

This module provides stream characteristics that bind readable or writable objects to the Service
object they are on.

"""

from __future__ import annotations

import _bleio

from . import Attribute, Characteristic, ComplexCharacteristic

try:
    from typing import TYPE_CHECKING, Optional, Union

    if TYPE_CHECKING:
        from circuitpython_typing import ReadableBuffer

        from adafruit_ble.characteristics import Characteristic
        from adafruit_ble.services import Service
        from adafruit_ble.uuid import UUID

except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class BoundWriteStream:
    """Writes data out to the peer."""

    def __init__(self, bound_characteristic: Characteristic) -> None:
        self.bound_characteristic = bound_characteristic

    def write(self, buf: ReadableBuffer) -> None:
        """Write data from buf out to the peer."""
        # We can only write 20 bytes at a time.
        offset = 0
        while offset < len(buf):
            self.bound_characteristic.value = buf[offset : offset + 20]
            offset += 20


class StreamOut(ComplexCharacteristic):
    """Output stream from the Service server."""

    def __init__(
        self,
        *,
        uuid: Optional[UUID] = None,
        timeout: float = 1.0,
        buffer_size: int = 64,
        properties: int = Characteristic.NOTIFY,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
    ) -> None:
        self._timeout = timeout
        self._buffer_size = buffer_size
        super().__init__(
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            max_length=buffer_size,
        )

    def bind(self, service: Service) -> Union[_bleio.CharacteristicBuffer, BoundWriteStream]:
        """Binds the characteristic to the given Service."""
        bound_characteristic = super().bind(service)
        # If we're given a remote service then we're the client and need to buffer in.
        if service.remote:
            bound_characteristic.set_cccd(notify=True)
            return _bleio.CharacteristicBuffer(
                bound_characteristic,
                timeout=self._timeout,
                buffer_size=self._buffer_size,
            )
        return BoundWriteStream(bound_characteristic)


class StreamIn(ComplexCharacteristic):
    """Input stream into the Service server."""

    def __init__(
        self,
        *,
        uuid: Optional[UUID] = None,
        timeout: float = 1.0,
        buffer_size: int = 64,
        properties: int = (Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE),
        write_perm: int = Attribute.OPEN,
    ) -> None:
        self._timeout = timeout
        self._buffer_size = buffer_size
        super().__init__(
            uuid=uuid,
            properties=properties,
            read_perm=Attribute.NO_ACCESS,
            write_perm=write_perm,
            max_length=buffer_size,
        )

    def bind(self, service: Service) -> Union[_bleio.CharacteristicBuffer, BoundWriteStream]:
        """Binds the characteristic to the given Service."""
        bound_characteristic = super().bind(service)
        # If the service is remote need to write out.
        if service.remote:
            return BoundWriteStream(bound_characteristic)
        # We're the server so buffer incoming writes.
        return _bleio.CharacteristicBuffer(
            bound_characteristic, timeout=self._timeout, buffer_size=self._buffer_size
        )
