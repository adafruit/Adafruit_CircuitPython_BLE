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

BLE Peripheral-related classes.

* Author(s): Dan Halbert for Adafruit Industries

"""
import bleio

class PeripheralServer:
    """BLE Peripheral acting as a GATT Server"""

    def __init__(self, services, *, name='CPYUART'):
        """Create a new PeripheralServer object which runs locally.

        :param iterable services: the Service objects for services available from this peripheral.
        :param str name: The name used when advertising this peripheral
        """
        self._services = services
        self._bleio_peripheral = bleio.Peripheral(
            (service.bleio_service for service in services),
            name=name)

    @property
    def bleio_peripheral(self):
        """The native bleio.Peripheral object."""
        return self._bleio_peripheral

    @property
    def services(self):
        """Services available from this peripheral."""
        return self._services

    @property
    def name(self):
        """Advertised name."""
        return self._bleio_peripheral.name

    @property
    def connected(self):
        """True if a client is connected to this peripheral."""
        return self._bleio_peripheral.connected

    def start_advertising(self):
        """Start advertising services.
        TODO: connectable flag, and custom advertising data. May refactor this,
        pulling in broadcaster, or splitting up functionality further.
        """
        self._bleio_peripheral.start_advertising()

    def stop_advertising(self):
        """Stop advertising."""
        self._bleio_peripheral.stop_advertising()
