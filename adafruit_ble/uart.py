# The MIT License (MIT)
#
# Copyright (c) 2018 Dan Halbert for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_ble.uuid`
====================================================

UART-style communication.

* Author(s): Dan Halbert for Adafruit Industries

"""

import bleio

from .uuid import UUID
from .characteristic import Characteristic
from .service import Service
from .peripheral_server import PeripheralServer

class UARTService:
    """Provide UART-like functionality via the Nordic NUS service."""

    NUS_SERVICE_UUID = UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    NUS_RX_CHAR_UUID = UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
    NUS_TX_CHAR_UUID = UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

    def __init__(self):
        """Define the NUS service and start advertising it."""
        self._nus_tx_char = Characteristic(self.NUS_TX_CHAR_UUID, notify=True)
        self._nus_rx_char = Characteristic(self.NUS_RX_CHAR_UUID,
                                           write=True, write_no_response=True)

        nus_uart_service = Service(self.NUS_SERVICE_UUID, (self._nus_tx_char, self._nus_rx_char))

        self._periph = PeripheralServer((nus_uart_service,))
        self._rx_buffer = bleio.CharacteristicBuffer(self._nus_rx_char.bleio_characteristic, 64)

        self._periph.start_advertising()

    @property
    def connected(self):
        """Has someone connected to the service?"""
        return self._periph.connected

    def read(self):
        """Read the next available byte from the buffered input.
        Return None if nothing is available.
        """
        return self._rx_buffer.read()

    def write(self, bytes_to_write):
        """Write a buffer of bytes."""
        self._nus_tx_char.value = bytes_to_write
