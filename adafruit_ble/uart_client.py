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
from bleio import Central, CharacteristicBuffer
from .uart import NUS_SERVICE_UUID, NUS_RX_CHAR_UUID, NUS_TX_CHAR_UUID

class UARTClient:
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
        self._buffer_size = buffer_size
        self._timeout = timeout
        self._read_char = self._write_char = self._read_buffer = None
        self._central = Central()

    def connect(self, address, timeout):
        """Try to connect to the peripheral at the given address.

        :param bleio.Address address: The address of the peripheral to connect to
        :param float/int timeout: Try to connect for timeout seconds.
        """
        self._central.connect(address, timeout, service_uuids=(NUS_SERVICE_UUID,))

        # Connect succeeded. Get the remote characteristics we need, which were
        # found during discovery.

        for characteristic in self._central.remote_services[0].characteristics:
            # Since we're remote we receive on tx and send on rx.
            # The names are from the point of view of the server.
            if characteristic.uuid == NUS_RX_CHAR_UUID:
                self._write_char = characteristic
            elif characteristic.uuid == NUS_TX_CHAR_UUID:
                self._read_char = characteristic
        if not self._write_char or not self._read_char:
            raise OSError("Remote UART missing needed characteristic")
        self._read_buffer = CharacteristicBuffer(self._read_char,
                                                 timeout=self._timeout,
                                                 buffer_size=self._buffer_size)

    def disconnect(self):
        """Disconnect from the peripheral."""
        self._central.disconnect()
        self._read_char = self._write_char = self._read_buffer = None

    @property
    def connected(self):
        """True if we are connected to a peripheral."""
        return self._central.connected

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
