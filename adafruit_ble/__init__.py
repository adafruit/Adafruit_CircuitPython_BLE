# The MIT License (MIT)
#
# Copyright (c) 2019 Dan Halbert for Adafruit Industries
# Copyright (c) 2019 Scott Shawcroft for Adafruit Industries
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
`adafruit_ble`
====================================================

This module provides higher-level BLE (Bluetooth Low Energy) functionality,
building on the native `_bleio` module.

* Author(s): Dan Halbert and Scott Shawcroft for Adafruit Industries

Implementation Notes
--------------------

**Hardware:**

   Adafruit Feather nRF52840 Express <https://www.adafruit.com/product/4062>

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

import board
import _bleio

from .services import Service
from .advertising import Advertisement

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class BLEConnection:
    """This represents a connection to a peer BLE device.

       It acts as a map from a Service type to a Service instance for the connection.
    """
    def __init__(self, connection):
        self._connection = connection
        self._discovered_services = {}
        """These are the bare remote services from _bleio."""

        self._constructed_services = {}
        """These are the Service instances from the library that wrap the remote services."""

    def _discover_remote(self, uuid):
        remote_service = None
        if uuid in self._discovered_services:
            remote_service = self._discovered_services[uuid]
        else:
            results = self._connection.discover_remote_services((uuid.bleio_uuid,))
            if results:
                remote_service = results[0]
                self._discovered_services[uuid] = remote_service
        return remote_service

    def __contains__(self, key):
        uuid = key
        if hasattr(key, "uuid"):
            uuid = key.uuid
        return self._discover_remote(uuid) is not None

    def __getitem__(self, key):
        uuid = key
        maybe_service = False
        if hasattr(key, "uuid"):
            uuid = key.uuid
            maybe_service = True

        remote_service = self._discover_remote(uuid)

        if uuid in self._constructed_services:
            return self._constructed_services[uuid]
        if remote_service:
            constructed_service = None
            if maybe_service:
                constructed_service = key(service=remote_service)
                self._constructed_services[uuid] = constructed_service
            return constructed_service

        raise KeyError("{!r} object has no service {}".format(self, key))

    @property
    def connected(self):
        """True if the connection to the peer is still active."""
        return self._connection.connected

    def disconnect(self):
        """Disconnect from peer."""
        self._connection.disconnect()

class BLERadio:
    """The BLERadio class enhances the normal `_bleio.Adapter`.

       It uses the library's `Advertisement` classes and the `BLEConnection` class."""

    def __init__(self, adapter=None):
        if not adapter:
            adapter = _bleio.adapter
        self._adapter = adapter
        self._current_advertisement = None
        self._connection_cache = {}

    def start_advertising(self, advertisement, scan_response=None, **kwargs):
        """Starts advertising the given advertisement.

            It takes most kwargs of `_bleio.Adapter.start_advertising`."""
        scan_response_data = None
        if scan_response:
            scan_response_data = bytes(scan_response)
        self._adapter.start_advertising(bytes(advertisement),
                                        scan_response=scan_response_data,
                                        connectable=advertisement.connectable,
                                        **kwargs)

    def stop_advertising(self):
        """Stops advertising."""
        self._adapter.stop_advertising()

    def start_scan(self, *advertisement_types, **kwargs):
        """Starts scanning. Returns an iterator of advertisement objects of the types given in
           advertisement_types. The iterator will block until an advertisement is heard or the scan
           times out.

           If any ``advertisement_types`` are given, only Advertisements of those types are produced
           by the returned iterator. If none are given then `Advertisement` objects will be
           returned."""
        prefixes = b""
        if advertisement_types:
            prefixes = b"".join(adv.prefix for adv in advertisement_types)
        for entry in self._adapter.start_scan(prefixes=prefixes, **kwargs):
            adv_type = Advertisement
            for possible_type in advertisement_types:
                if possible_type.matches(entry) and issubclass(possible_type, adv_type):
                    adv_type = possible_type
            advertisement = adv_type.from_entry(entry)
            if advertisement:
                yield advertisement

    def stop_scan(self):
        """Stops any active scan.

           The scan results iterator will return any buffered results and then raise StopIteration
           once empty."""
        self._adapter.stop_scan()

    def connect(self, advertisement, *, timeout=4):
        """Initiates a `BLEConnection` to the peer that advertised the given advertisement."""
        connection = self._adapter.connect(advertisement.address, timeout=timeout)
        self._connection_cache[connection] = BLEConnection(connection)
        return self._connection_cache[connection]

    @property
    def connected(self):
        """True if any peers are connected to the adapter."""
        return self._adapter.connected

    @property
    def connections(self):
        """A tuple of active `BLEConnection` objects."""
        connections = self._adapter.connections
        wrapped_connections = [None] * len(connections)
        for i, connection in enumerate(self._adapter.connections):
            if connection not in self._connection_cache:
                self._connection_cache[connection] = BLEConnection(connection)
            wrapped_connections[i] = self._connection_cache[connection]

        return tuple(wrapped_connections)
