# SPDX-FileCopyrightText: 2019 Dan Halbert for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""

This module provides higher-level BLE (Bluetooth Low Energy) functionality,
building on the native `_bleio` module.

"""
# pylint: disable=wrong-import-position
import sys

if sys.implementation.name == "circuitpython" and sys.implementation.version[0] <= 4:
    raise ImportError(
        "This release is not compatible with CircuitPython 4.x; use library release 1.x.x"
    )
# pylint: enable=wrong-import-position

import _bleio

from .services import Service
from .advertising import Advertisement

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class BLEConnection:
    """
    Represents a connection to a peer BLE device.
    It acts as a map from a `Service` type to a `Service` instance for the connection.

    :param _bleio.Connection bleio_connection: the native `_bleio.Connection` object to wrap

    """

    def __init__(self, bleio_connection):
        self._bleio_connection = bleio_connection
        # _bleio.Service objects representing services found during discovery.
        self._discovered_bleio_services = {}
        # Service objects that wrap remote services.
        self._constructed_services = {}

    def _discover_remote(self, uuid):
        remote_service = None
        if uuid in self._discovered_bleio_services:
            remote_service = self._discovered_bleio_services[uuid]
        else:
            results = self._bleio_connection.discover_remote_services(
                (uuid.bleio_uuid,)
            )
            if results:
                remote_service = results[0]
                self._discovered_bleio_services[uuid] = remote_service
        return remote_service

    def __contains__(self, key):
        """
        Allows easy testing for a particular Service class or a particular UUID
        associated with this connection.

        Example::

            if UARTService in connection:
                # do something

            if StandardUUID(0x1234) in connection:
                # do something
        """
        uuid = key
        if hasattr(key, "uuid"):
            uuid = key.uuid
        return self._discover_remote(uuid) is not None

    def __getitem__(self, key):
        """Return the Service for the given Service class or uuid, if any."""
        uuid = key
        maybe_service = False
        if hasattr(key, "uuid"):
            uuid = key.uuid
            maybe_service = True

        if uuid in self._constructed_services:
            return self._constructed_services[uuid]

        remote_service = self._discover_remote(uuid)
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
        return self._bleio_connection.connected

    @property
    def paired(self):
        """True if the paired to the peer."""
        return self._bleio_connection.paired

    @property
    def connection_interval(self):
        """Time between transmissions in milliseconds. Will be multiple of 1.25ms. Lower numbers
        increase speed and decrease latency but increase power consumption.

        When setting connection_interval, the peer may reject the new interval and
        `connection_interval` will then remain the same.

        Apple has additional guidelines that dictate should be a multiple of 15ms except if HID
        is available. When HID is available Apple devices may accept 11.25ms intervals."""
        return self._bleio_connection.connection_interval

    @connection_interval.setter
    def connection_interval(self, value):
        self._bleio_connection.connection_interval = value

    def pair(self, *, bond=True):
        """Pair to the peer to increase security of the connection."""
        return self._bleio_connection.pair(bond=bond)

    def disconnect(self):
        """Disconnect from peer."""
        self._bleio_connection.disconnect()


class BLERadio:
    """
    BLERadio provides the interfaces for BLE advertising,
    scanning for advertisements, and connecting to peers. There may be
    multiple connections active at once.

    It uses this library's `Advertisement` classes and the `BLEConnection` class."""

    def __init__(self, adapter=None):
        """If no adapter is supplied, use the built-in `_bleio.adapter`.
        If no built-in adapter is available, raise `RuntimeError`.
        """
        if adapter is None and _bleio.adapter is None:
            raise RuntimeError("No adapter available")
        self._adapter = adapter or _bleio.adapter
        self._current_advertisement = None
        self._connection_cache = {}

    def start_advertising(
        self, advertisement, scan_response=None, interval=0.1, timeout=None
    ):
        """
        Starts advertising the given advertisement.

        :param buf scan_response: scan response data packet bytes.
            If ``None``, a default scan response will be generated that includes
            `BLERadio.name` and `BLERadio.tx_power`.
        :param float interval:  advertising interval, in seconds
        :param int timeout:  advertising timeout in seconds.
            If None, no timeout.

        ``timeout`` is not available in CircuitPython 5.x and must be `None`.
        """
        advertisement_bytes = bytes(advertisement)
        scan_response_bytes = b""
        if not scan_response and len(advertisement_bytes) <= 31:
            scan_response = Advertisement()
            scan_response.complete_name = self.name
            scan_response.tx_power = self.tx_power
        if scan_response:
            scan_response_bytes = bytes(scan_response)

        # pylint: disable=unexpected-keyword-arg
        # Remove after 5.x is no longer supported.
        if (
            sys.implementation.name == "circuitpython"
            and sys.implementation.version[0] <= 5
        ):
            if timeout is not None:
                raise NotImplementedError("timeout not available for CircuitPython 5.x")
            self._adapter.start_advertising(
                advertisement_bytes,
                scan_response=scan_response_bytes,
                connectable=advertisement.connectable,
                interval=interval,
            )
        else:
            self._adapter.start_advertising(
                advertisement_bytes,
                scan_response=scan_response_bytes,
                connectable=advertisement.connectable,
                interval=interval,
                timeout=0 if timeout is None else timeout,
            )

    def stop_advertising(self):
        """Stops advertising."""
        self._adapter.stop_advertising()

    def start_scan(
        self,
        *advertisement_types,
        buffer_size=512,
        extended=False,
        timeout=None,
        interval=0.1,
        window=0.1,
        minimum_rssi=-80,
        active=True
    ):
        """
        Starts scanning. Returns an iterator of advertisement objects of the types given in
        advertisement_types. The iterator will block until an advertisement is heard or the scan
        times out.

        If any ``advertisement_types`` are given, only Advertisements of those types are produced
        by the returned iterator. If none are given then `Advertisement` objects will be
        returned.

        Advertisements and scan responses are filtered and returned separately.

        :param int buffer_size: the maximum number of advertising bytes to buffer.
        :param bool extended: When True, support extended advertising packets.
            Increasing buffer_size is recommended when this is set.
        :param float timeout: the scan timeout in seconds.
            If None, will scan until `stop_scan` is called.
        :param float interval: the interval (in seconds) between the start
            of two consecutive scan windows
            Must be in the range 0.0025 - 40.959375 seconds.
        :param float window: the duration (in seconds) to scan a single BLE channel.
            window must be <= interval.
        :param int minimum_rssi: the minimum rssi of entries to return.
        :param bool active: request and retrieve scan responses for scannable advertisements.
        :return: If any ``advertisement_types`` are given,
            only Advertisements of those types are produced by the returned iterator.
            If none are given then `Advertisement` objects will be returned.
        :rtype: iterable
        """
        if not advertisement_types:
            advertisement_types = (Advertisement,)

        all_prefix_bytes = tuple(adv.get_prefix_bytes() for adv in advertisement_types)

        # If one of the advertisement_types has no prefix restrictions, then
        # no prefixes should be specified at all, so we match everything.
        prefixes = b"" if b"" in all_prefix_bytes else b"".join(all_prefix_bytes)

        for entry in self._adapter.start_scan(
            prefixes=prefixes,
            buffer_size=buffer_size,
            extended=extended,
            timeout=timeout,
            interval=interval,
            window=window,
            minimum_rssi=minimum_rssi,
            active=active,
        ):
            adv_type = Advertisement
            for possible_type in advertisement_types:
                if possible_type.matches(entry) and issubclass(possible_type, adv_type):
                    adv_type = possible_type
            # Double check the adv_type is requested. We may return Advertisement accidentally
            # otherwise.
            if adv_type not in advertisement_types:
                continue
            advertisement = adv_type(entry=entry)
            if advertisement:
                yield advertisement

    def stop_scan(self):
        """Stops any active scan.

        The scan results iterator will return any buffered results and then raise StopIteration
        once empty."""
        self._adapter.stop_scan()

    def connect(self, peer, *, timeout=4.0):
        """
        Initiates a `BLEConnection` to the peer that advertised the given advertisement.

        :param peer: An `Advertisement`, a subclass of `Advertisement` or `_bleio.Address`
        :param float timeout: how long to wait for a connection
        :return: the connection to the peer
        :rtype: BLEConnection
        """
        if not isinstance(peer, _bleio.Address):
            peer = peer.address
        connection = self._adapter.connect(peer, timeout=timeout)
        self._clean_connection_cache()
        self._connection_cache[connection] = BLEConnection(connection)
        return self._connection_cache[connection]

    @property
    def connected(self):
        """True if any peers are connected."""
        return self._adapter.connected

    @property
    def connections(self):
        """A tuple of active `BLEConnection` objects."""
        self._clean_connection_cache()
        connections = self._adapter.connections
        wrapped_connections = [None] * len(connections)
        for i, connection in enumerate(connections):
            if connection not in self._connection_cache:
                self._connection_cache[connection] = BLEConnection(connection)
            wrapped_connections[i] = self._connection_cache[connection]

        return tuple(wrapped_connections)

    @property
    def name(self):
        """The name for this device. Used in advertisements and
        as the Device Name in the Generic Access Service, available to a connected peer.
        """
        return self._adapter.name

    @name.setter
    def name(self, value):
        self._adapter.name = value

    @property
    def tx_power(self):
        """Transmit power, in dBm."""
        return 0

    @tx_power.setter
    def tx_power(self, value):
        raise NotImplementedError("setting tx_power not yet implemented")

    @property
    def address_bytes(self):
        """The device address, as a ``bytes()`` object of length 6."""
        return self._adapter.address.address_bytes

    @property
    def advertising(self):
        """The advertising state"""
        return self._adapter.advertising  # pylint: disable=no-member

    def _clean_connection_cache(self):
        """Remove cached connections that have disconnected."""
        for k, connection in list(self._connection_cache.items()):
            if not connection.connected:
                del self._connection_cache[k]
