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
`adafruit_ble.uart_server`
====================================================

UART-style communication: Peripheral acting as a GATT Server.

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import Attribute, Characteristic, CharacteristicBuffer, Peripheral, Service
from .advertising import ServerAdvertisement
from .uart import NUS_SERVICE_UUID, NUS_RX_CHAR_UUID, NUS_TX_CHAR_UUID

class UARTServer:
    """
    Provide UART-like functionality via the Nordic NUS service.

    :param int timeout:  the timeout in seconds to wait
      for the first character and between subsequent characters.
    :param int buffer_size: buffer up to this many bytes.
      If more bytes are received, older bytes will be discarded.
    :param str name: Name to advertise for server. If None, use default Peripheral name.

    Example::

        from adafruit_ble.uart_server import UARTServer
        uart = UARTServer()
        uart.start_advertising()

        # Wait for a connection.
        while not uart.connected:
            pass

        uart.write('abc')
    """

    def __init__(self, *, timeout=1.0, buffer_size=64, name=None):
        self._periph = Peripheral(name)
        service = Service.add_to_peripheral(self._periph, NUS_SERVICE_UUID)

        self._read_char = Characteristic.add_to_service(
            service, NUS_RX_CHAR_UUID,
            properties=Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE,
            read_perm=Attribute.NO_ACCESS, write_perm=Attribute.OPEN)

        self._write_char = Characteristic.add_to_service(
            service, NUS_TX_CHAR_UUID,
            properties=Characteristic.NOTIFY,
            read_perm=Attribute.OPEN, write_perm=Attribute.NO_ACCESS)

        self._read_buffer = CharacteristicBuffer(self._read_char,
                                                 timeout=timeout, buffer_size=buffer_size)


        self._advertisement = ServerAdvertisement(self._periph)

    def start_advertising(self):
        """Start advertising the service. When a client connects, advertising will stop.
        When the client disconnects, restart advertising by calling ``start_advertising()`` again.
        """
        self._periph.start_advertising(self._advertisement.advertising_data_bytes,
                                       scan_response=self._advertisement.scan_response_bytes)

    def stop_advertising(self):
        """Stop advertising the service."""
        self._periph.stop_advertising()

    @property
    def connected(self):
        """True if someone connected to the server."""
        return self._periph.connected

    def disconnect(self):
        """Disconnect from peer."""
        self._periph.disconnect()

    def read(self, nbytes=None):
        """
        Read characters. If ``nbytes`` is specified then read at most that many bytes.
        Otherwise, read everything that arrives until the connection times out.
        Providing the number of bytes expected is highly recommended because it will be faster.

        :return: Data read
        :rtype: bytes or None
        """
        return self._read_buffer.read(nbytes)

    def readinto(self, buf, nbytes=None):
        """
        Read bytes into the ``buf``. If ``nbytes`` is specified then read at most
        that many bytes. Otherwise, read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)
        """
        return self._read_buffer.readinto(buf, nbytes)

    def readline(self):
        """
        Read a line, ending in a newline character.

        :return: the line read
        :rtype: int or None
        """
        return self._read_buffer.readline()

    @property
    def in_waiting(self):
        """The number of bytes in the input buffer, available to be read."""
        return self._read_buffer.in_waiting

    def reset_input_buffer(self):
        """Discard any unread characters in the input buffer."""
        self._read_buffer.reset_input_buffer()

    def write(self, buf):
        """Write a buffer of bytes."""
        # We can only write 20 bytes at a time.
        offset = 0
        while offset < len(buf):
            self._write_char.value = buf[offset:offset+20]
            offset += 20
