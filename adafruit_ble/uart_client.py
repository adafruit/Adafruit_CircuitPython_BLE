 # The MIT License (MIT)
#
# Copyright (c) 2019 Dan Halbert for Adafruit Industries
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
`adafruit_ble.uart_client`
====================================================

UART-style communication by a Central as a GATT Client

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import Characteristic, Central
from .uart import UART

class UARTClient(UART):
    """
    Provide UART-like functionality via the Nordic NUS service.

    :param int timeout:  the timeout in seconds to wait
      for the first character and between subsequent characters.
    :param int buffer_size: buffer up to this many bytes.
      If more bytes are received, older bytes will be discarded.
    :param str name: Name to advertise for server. If None, use default Peripheral name.

    Example::

        from adafruit_ble.uart_client import UARTClient
        from adafruit_ble.scanner import Scanner, ScanEntry

        scanner = Scanner()
        uarts = ScanEntry.with_service_uuid(scanner.scan_unique(3), UART.NUS_SERVICE_UUID)
        if not uarts:
            raise ValueError("No UART for connection")

        uart_client = UARTClient()
        uart_client.connect(uarts[0].address, 5, service_uuids=(UART.NUS_SERVICE_UUID,))

        uart_client.write('abc')
    """

    def __init__(self, *, timeout=5.0, buffer_size=64):
        # Since we're remote we receive on tx and send on rx. The names
        # are from the point of view of the server.
        super().__init__(read_characteristic=Characteristic(UART.NUS_TX_CHAR_UUID),
                         write_characteristic=Characteristic(UART.NUS_RX_CHAR_UUID),
                         timeout=timeout, buffer_size=buffer_size)

        self._central = Central()

    @property
    def connected(self):
        """True if we are connected to a peripheral."""
        return self._central.connected

    def connect(self, address, timeout):
        """Try to connect to the peripheral at the given address.

        :param bleio.Address address: The address of the peripheral to connect to
        :param float/int timeout: Try to connect for timeout seconds.
        """
        self._central.connect(address, timeout, service_uuids=(UART.NUS_SERVICE_UUID,))

    def disconnect(self):
        """Disconnect from the peripheral."""
        self._central.disconnect()
