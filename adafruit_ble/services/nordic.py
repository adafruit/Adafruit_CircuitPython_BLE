# SPDX-FileCopyrightText: 2019 Dan Halbert for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`nordic`
====================================================

This module provides Services used by Nordic Semiconductors.

"""

from __future__ import annotations

from ..characteristics.stream import StreamIn, StreamOut
from ..uuid import VendorUUID
from . import Service

try:
    from typing import TYPE_CHECKING, Optional

    if TYPE_CHECKING:
        import _bleio
        from circuitpython_typing import ReadableBuffer, WriteableBuffer

except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class UARTService(Service):
    """
    Provide UART-like functionality via the Nordic NUS service.

    See ``examples/ble_uart_echo_test.py`` for a usage example.
    """

    uuid = VendorUUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    _server_tx = StreamOut(
        uuid=VendorUUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
        timeout=1.0,
        # 512 is the largest negotiated MTU-3 value for all CircuitPython ports.
        buffer_size=512,
    )
    _server_rx = StreamIn(
        uuid=VendorUUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
        timeout=1.0,
        # 512 is the largest negotiated MTU-3 value for all CircuitPython ports.
        buffer_size=512,
    )

    def __init__(self, service: Optional[_bleio.Service] = None) -> None:
        super().__init__(service=service)
        self.connectable = True
        if not service:
            self._rx = self._server_rx
            self._tx = self._server_tx
        else:
            # If we're a client then swap the characteristics we use.
            self._tx = self._server_rx
            self._rx = self._server_tx

    def deinit(self):
        """The characteristic buffers must be deinitialized when no longer needed.
        Otherwise they will leak storage.
        """
        for obj in (self._tx, self._rx):
            if hasattr(obj, "deinit"):
                obj.deinit()

    def read(self, nbytes: Optional[int] = None) -> Optional[bytes]:
        """
        Read characters. If ``nbytes`` is specified then read at most that many bytes.
        Otherwise, read everything that arrives until the connection times out.
        Providing the number of bytes expected is highly recommended because it will be faster.

        :return: Data read
        :rtype: bytes or None
        """
        return self._rx.read(nbytes)

    def readinto(self, buf: WriteableBuffer, nbytes: Optional[int] = None) -> Optional[int]:
        """
        Read bytes into the ``buf``. If ``nbytes`` is specified then read at most
        that many bytes. Otherwise, read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)
        """
        return self._rx.readinto(buf, nbytes)

    def readline(self) -> Optional[bytes]:
        """
        Read a line, ending in a newline character.

        :return: the line read
        :rtype: bytes or None
        """
        return self._rx.readline()

    @property
    def in_waiting(self) -> int:
        """The number of bytes in the input buffer, available to be read."""
        return self._rx.in_waiting

    def reset_input_buffer(self) -> None:
        """Discard any unread characters in the input buffer."""
        self._rx.reset_input_buffer()

    def write(self, buf: ReadableBuffer) -> None:
        """Write a buffer of bytes."""
        self._tx.write(buf)
