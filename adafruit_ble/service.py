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

BLE Service-related classes.

* Author(s): Dan Halbert for Adafruit Industries

"""
import bleio

class Service:
    """BLE Service"""

    def __init__(self, uuid, characteristics, *, secondary=False):
        """Create a new Service object identified with the specified UUID.

        :param UUID uuid: The uuid of the service
        :param iterable characteristics: the Characteristic objects for this service
        :param bool secondary: If the service is a secondary one
        """
        self._uuid = uuid
        self._characteristics = characteristics
        self._bleio_service = bleio.Service(
            uuid.bleio_uuid,
            (char.bleio_characteristic for char in characteristics),
            secondary=secondary)

    @property
    def uuid(self):
        """UUID of this service."""
        return self._uuid

    @property
    def bleio_service(self):
        """The native bleio.Service object."""
        return self._bleio_service

    @property
    def secondary(self):
        """This is a secondary service."""
        return self._bleio_service.secondary
