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
`adafruit_ble.uart`
====================================================

UART-style communication.

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import UUID, Characteristic, Service, Peripheral, CharacteristicBuffer


class UARTServer:
    """
    Provide UART-like functionality via the Nordic NUS service.

    :param int timeout:  the timeout in seconds to wait
      for the first character and between subsequent characters.
    :param int buffer_size: buffer up to this many bytes.
      If more bytes are received, older bytes will be discarded.

    Example::

        from adafruit_ble.uart import UARTServer
        uart = UARTServer()
        uart.start_advertising()

        # Wait for a connection.
        while not uart.connected:
            pass

        uart.write('abc')
    """

    NUS_SERVICE_UUID = UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    NUS_RX_CHAR_UUID = UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
    NUS_TX_CHAR_UUID = UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

    def __init__(self, timeout=1.0, buffer_size=64):
        """Define the NUS service and start advertising it."""
        self._nus_tx_char = Characteristic(self.NUS_TX_CHAR_UUID, notify=True)
        self._nus_rx_char = Characteristic(self.NUS_RX_CHAR_UUID,
                                           write=True, write_no_response=True)

        nus_uart_service = Service(self.NUS_SERVICE_UUID, (self._nus_tx_char, self._nus_rx_char))

        self._periph = Peripheral((nus_uart_service,))
        self._rx_buffer = CharacteristicBuffer(self._nus_rx_char,
                                               timeout=timeout, buffer_size=buffer_size)

    def start_advertising(self):
        """Start advertising the service. When a client connects, advertising will stop.
        When the client disconnects, restart advertising by calling ``start_advertising()`` again.
        """
        self._periph.start_advertising()

    def stop_advertising(self):
        """Stop advertising the service."""
        self._periph.stop_advertising()

    @property
    def connected(self):
        """True if someone connected to the server."""
        return self._periph.connected

    def read(self, nbytes=None):
        """
        Read characters. If ``nbytes`` is specified then read at most that many bytes.
        Otherwise, read everything that arrives until the connection times out.
        Providing the number of bytes expected is highly recommended because it will be faster.

        :return: Data read
        :rtype: bytes or None
        """
        return self._rx_buffer.read(nbytes)

    def readinto(self, buf, nbytes=None):
        """
        Read bytes into the ``buf``. If ``nbytes`` is specified then read at most
        that many bytes. Otherwise, read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)
        """
        return self._rx_buffer.readinto(buf, nbytes)

    def readline(self):
        """
        Read a line, ending in a newline character.

        :return: the line read
        :rtype: int or None
        """
        return self._rx_buffer.readline()

    @property
    def in_waiting(self):
        """The number of bytes in the input buffer, available to be read."""
        return self._rx_buffer.in_waiting

    def reset_input_buffer(self):
        """Discard any unread characters in the input buffer."""
        self._rx_buffer.reset_input_buffer()

    def write(self, buf):
        """Write a buffer of bytes."""
        self._nus_tx_char.value = buf
