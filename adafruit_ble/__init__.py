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

import _bleio
import board

from .services.core import Service
from .advertising import Advertisement

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

# These are internal data structures used throughout the library to recognize certain Services and
# Advertisements.
# pylint: disable=invalid-name
all_services_by_name = {}
all_services_by_uuid = {}
known_advertisements = set()
# pylint: enable=invalid-name

def recognize_services(*service_classes):
    """Instruct the adafruit_ble library to recognize the given Services.

       This will cause the Service related advertisements to show the corresponding class.
       `SmartConnection` will automatically have attributes for any recognized service available
       from the peer."""
    for service_class in service_classes:
        if not issubclass(service_class, Service):
            raise ValueError("Can only detect subclasses of Service")
        all_services_by_name[service_class.default_field_name] = service_class
        all_services_by_uuid[service_class.uuid] = service_class

def recognize_advertisement(*advertisements):
    """Instruct the adafruit_ble library to recognize the given `Advertisement` types.

       When an advertisement is recognized by the `SmartAdapter`, it will be returned from the
       start_scan iterator instead of a generic `Advertisement`."""
    known_advertisements.add(*advertisements)

class SmartConnection:
    """This represents a connection to a peer BLE device.

       Its smarts come from its ability to recognize Services available on the peer and make them
       available as attributes on the Connection. Use `recognize_services` to register all services
       of interest. All subsequent Connections will then recognize the service.

       ``dir(connection)`` will show all attributes including recognized Services.
       """
    def __init__(self, connection):
        self._connection = connection

    def __dir__(self):
        discovered = []
        results = self._connection.discover_remote_services()
        for service in results:
            uuid = service.uuid
            if uuid in all_services_by_uuid:
                service = all_services_by_uuid[uuid]
                discovered.append(service.default_field_name)
        super_dir = dir(super())
        super_dir.extend(discovered)
        return super_dir

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name in all_services_by_name:
            service = all_services_by_name[name]
            uuid = service.uuid._uuid
            results = self._connection.discover_remote_services((uuid,))
            if results:
                remote_service = service(service=results[0])
                setattr(self, name, remote_service)
                return remote_service
        raise AttributeError()

    @property
    def connected(self):
        """True if the connection to the peer is still active."""
        return self._connection.connected

    def disconnect(self):
        """Disconnect from peer."""
        self._connection.disconnect()

class SmartAdapter:
    """This BLE Adapter class enhances the normal `_bleio.Adapter`.

       It uses the library's `Advertisement` classes and the `SmartConnection` class."""
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
        print(advertisement.connectable)
        self._adapter.start_advertising(bytes(advertisement),
                                        scan_response=scan_response_data,
                                        connectable=advertisement.connectable,
                                        **kwargs)

    def stop_advertising(self):
        """Stops advertising."""
        self._adapter.stop_advertising()

    def start_scan(self, advertisement_types=None, **kwargs):
        """Starts scanning. Returns an iterator of Advertisements that are either recognized or
           in advertisment_types (which will be subsequently recognized.) The iterator will block
           until an advertisement is heard or the scan times out.

           If a list ``advertisement_types`` is given, only Advertisements of that type are produced
           by the returned iterator."""
        prefixes = b""
        if advertisement_types:
            recognize_advertisement(*advertisement_types)
            if len(advertisement_types) == 1:
                prefixes = advertisement_types[0].prefix
        for entry in self._adapter.start_scan(prefixes=prefixes, **kwargs):
            adv_type = Advertisement
            for possible_type in known_advertisements:
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
        """Initiates a `SmartConnection` to the peer that advertised the given advertisement."""
        connection = self._adapter.connect(advertisement.address, timeout=timeout)
        self._connection_cache[connection] = SmartConnection(connection)
        return self._connection_cache[connection]

    @property
    def connected(self):
        """True if any peers are connected to the adapter."""
        return self._adapter.connected

    @property
    def connections(self):
        """A tuple of active `SmartConnection` objects."""
        connections = self._adapter.connections
        smart_connections = [None] * len(connections)
        for i, connection in enumerate(self._adapter.connections):
            if connection not in self._connection_cache:
                self._connection_cache[connection] = SmartConnection(connection)
            smart_connections[i] = self._connection_cache[connection]

        return tuple(smart_connections)
