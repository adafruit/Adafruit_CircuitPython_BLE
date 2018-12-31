
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

BLE Characteristic-related classes.

* Author(s): Dan Halbert for Adafruit Industries

"""
import bleio

class Characteristic:
    """BLE Characteristic"""

    def __init__(self, uuid, *, broadcast=False, indicate=False, notify=False,
                 read=False, write=False, write_no_response=False):
        """Create a new Characteristic object identified with the specified UUID,
        with properties defined by the keyword arguments.

        :param UUID uuid: The uuid of the characteristic
        :param bool broadcast: Allowed in advertising packets
        :param bool indicate: Server will indicate to the client when the value is set
           and wait for a response
        :param bool notify: Server will notify thE Client when the value is set
        :param bool read: Clients may read this characteristic
        :param bool write: Clients may write this characteristic; a response will be sent back
        :param bool write_no_response: Clients may write this characteristic;
           no response will be sent back
        """
        self._uuid = uuid
        self._bleio_char = bleio.Characteristic(
            uuid.bleio_uuid,
            broadcast=broadcast,
            indicate=indicate,
            notify=notify,
            read=read,
            write=write,
            write_no_response=write_no_response)

    @property
    def uuid(self):
        """UUID of this characteristic."""
        return self._uuid

    @property
    def bleio_characteristic(self):
        """The native bleio.Characteristic object."""
        return self._bleio_char

    @property
    def broadcast(self):
        """This characteristic is allowed in advertising packets."""
        return self._bleio_char.broadcast

    @property
    def indicate(self):
        """Server will indicate to the client when the value is set and wait for a response."""
        return self._bleio_char.indicate

    @property
    def notify(self):
        """Server will notify the client when the value is set."""
        return self._bleio_char.notify

    @property
    def read(self):
        """Client reads allowed."""
        return self._bleio_char.read

    @property
    def write(self):
        """Client writes allowed."""
        return self._bleio_char.write

    @property
    def write_no_response(self):
        """Client writes allowed, but will not be acknowledged."""
        return self._bleio_char.write_no_response

    @property
    def value(self):
        """Return this characteristic's value as a bytes object."""
        return self._bleio_char.value

    @value.setter
    def value(self, value):
        """Set this characteristic's value. The value is a bytes or bytearray object."""
        self._bleio_char.value = value
