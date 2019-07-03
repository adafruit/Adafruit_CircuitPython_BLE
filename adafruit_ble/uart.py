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
`adafruit_ble.uart`
====================================================

BLE UART-style communication. Common definitions.

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import UUID, CharacteristicBuffer




class UART:
    """
    Common superclass for Nordic UART Service (NUS) clients or servers.
    Not for general use: use `UARTServer` and `UARTClient` for Peripheral and Central,
    respectively.

    :param read_characteristic Characteristic: Characteristic to read from
    :param write_characteristic Characteristic: Characteristic to write to
    :param int timeout:  the timeout in seconds to wait
      for the first character and between subsequent characters
    :param int buffer_size: buffer up to this many bytes.
      If more bytes are received, older bytes will be discarded.
    """

    NUS_SERVICE_UUID = UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    """Nordic UART Service UUID"""
    NUS_RX_CHAR_UUID = UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
    """Nordic UART Service RX Characteristic UUID"""
    NUS_TX_CHAR_UUID = UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
    """Nordic UART Service TX Characteristic UUID"""

    def __init__(self, *, read_characteristic, write_characteristic, timeout=5.0, buffer_size=64):
        self._read_char = read_characteristic
        self._write_char = write_characteristic
        self._read_buffer = CharacteristicBuffer(self._read_char,
                                                 timeout=timeout, buffer_size=buffer_size)

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
