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
`adafruit_ble.current_time_client`
====================================================

UART-style communication by a Central as a GATT Client

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import Peripheral, UUID
from .advertising import SolicitationAdvertisement

class CurrentTimeClient:
    """
    Set up a peripheral that advertises for Current Time Service,
    and connects if found.

    :param str name: Name to advertise for server. If None, use default Peripheral name.

    Example::

        from adafruit_ble.current_time_client import SolicitationAdvertisement

        cts_client = CurrentTimeClient()
        cts_client.start_advertising()
        while not cts_client.connected:
            pass
        print(cts_client.time)
    """

    CTS_UUID = UUID(0x1805)

    def __init__(self, name="CTSClient", tx_power=0):
        self._periph = Peripheral()
        self._advertisement = SolicitationAdvertisement(name, (self.CTS_UUID,), tx_power=tx_power)

    def start_advertising(self):
        """Start advertising to solicit a central that supports Current Time Service."""
        self._periph.start_advertising(self._advertisement.advertising_data_bytes,
                                       scan_response=self._advertisement.scan_response_bytes)

    def stop_advertising(self):
        """Stop advertising the service."""
        self._periph.stop_advertising()

    @property
    def connected(self):
        """True if a central connected to this peripheral."""
        return self._periph.connected

    def pair(self):
        """Pair with the connected central."""
        pass

    @property
    def time(self):
        """Get the current time from the server."""
        return None
