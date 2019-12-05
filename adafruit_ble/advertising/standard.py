# The MIT License (MIT)
#
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
:py:mod:`~adafruit_ble.advertising.standard`
====================================================

This module provides BLE standard defined advertisements. The Advertisements are single purpose
even though multiple purposes may actually be present in a single packet.

"""

import struct

from . import Advertisement, AdvertisingDataField, encode_data, decode_data, to_hex, compute_length
from ..uuid import StandardUUID, VendorUUID

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class BoundServiceList:
    """Sequence-like object of Service UUID objects. It stores both standard and vendor UUIDs."""
    def __init__(self, advertisement, *, standard_services, vendor_services):
        self._advertisement = advertisement
        self._standard_service_fields = standard_services
        self._vendor_service_fields = vendor_services
        self._standard_services = []
        self._vendor_services = []
        for adt in standard_services:
            if adt in self._advertisement.data_dict:
                data = self._advertisement.data_dict[adt]
                for i in range(len(data) // 2):
                    uuid = StandardUUID(data[2*i:2*(i+1)])
                    self._standard_services.append(uuid)
        for adt in vendor_services:
            if adt in self._advertisement.data_dict:
                data = self._advertisement.data_dict[adt]
                for i in range(len(data) // 16):
                    uuid = VendorUUID(data[16*i:16*(i+1)])
                    self._vendor_services.append(uuid)

    def __contains__(self, key):
        uuid = key
        if hasattr(key, "uuid"):
            uuid = key.uuid
        return uuid in self._vendor_services or uuid in self._standard_services

    def _update(self, adt, uuids):
        if not uuids:
            # uuids is empty
            del self._advertisement.data_dict[adt]
        uuid_length = uuids[0].size // 8
        b = bytearray(len(uuids) * uuid_length)
        i = 0
        for uuid in uuids:
            uuid.pack_into(b, i)
            i += uuid_length
        self._advertisement.data_dict[adt] = b

    def __iter__(self):
        all_services = list(self._standard_services)
        all_services.extend(self._vendor_services)
        return iter(all_services)

    # TODO: Differentiate between complete and incomplete lists.
    def append(self, service):
        """Append a service to the list."""
        if isinstance(service.uuid, StandardUUID) and service not in self._standard_services:
            self._standard_services.append(service.uuid)
            self._update(self._standard_service_fields[0], self._standard_services)
        elif isinstance(service.uuid, VendorUUID) and service not in self._vendor_services:
            self._vendor_services.append(service.uuid)
            self._update(self._vendor_service_fields[0], self._vendor_services)

    # TODO: Differentiate between complete and incomplete lists.
    def extend(self, services):
        """Appends all services in the iterable to the list."""
        standard = False
        vendor = False
        for service in services:
            if (isinstance(service.uuid, StandardUUID) and
                    service.uuid not in self._standard_services):
                self._standard_services.append(service.uuid)
                standard = True
            elif isinstance(service.uuid, VendorUUID) and service.uuid not in self._vendor_services:
                self._vendor_services.append(service.uuid)
                vendor = True

        if standard:
            self._update(self._standard_service_fields[0], self._standard_services)
        if vendor:
            self._update(self._vendor_service_fields[0], self._vendor_services)

    def __str__(self):
        data = []
        for service_uuid in self._standard_services:
            data.append(str(service_uuid))
        for service_uuid in self._vendor_services:
            data.append(str(service_uuid))
        return " ".join(data)

class ServiceList(AdvertisingDataField):
    """Descriptor for a list of Service UUIDs that lazily binds a corresponding BoundServiceList."""
    def __init__(self, *, standard_services, vendor_services):
        self.standard_services = standard_services
        self.vendor_services = vendor_services

    def _present(self, obj):
        for adt in self.standard_services:
            if adt in obj.data_dict:
                return True
        for adt in self.vendor_services:
            if adt in obj.data_dict:
                return True
        return False

    def __get__(self, obj, cls):
        if not self._present(obj) and not obj.mutable:
            return None
        if not hasattr(obj, "adv_service_lists"):
            obj.adv_service_lists = {}
        first_adt = self.standard_services[0]
        if first_adt not in obj.adv_service_lists:
            obj.adv_service_lists[first_adt] = BoundServiceList(obj, **self.__dict__)
        return obj.adv_service_lists[first_adt]

class ProvideServicesAdvertisement(Advertisement):
    """Advertise what services that the device makes available upon connection."""
    # This is four prefixes, one for each ADT that can carry service UUIDs.
    prefix = b"\x01\x02\x01\x03\x01\x06\x01\x07"
    services = ServiceList(standard_services=[0x02, 0x03], vendor_services=[0x06, 0x07])
    """List of services the device can provide."""

    def __init__(self, *services):
        super().__init__()
        if services:
            self.services.extend(services)
        self.connectable = True

    @classmethod
    def matches(cls, entry):
        return entry.matches(cls.prefix, all=False)

class SolicitServicesAdvertisement(Advertisement):
    """Advertise what services the device would like to use over a connection."""
    # This is two prefixes, one for each ADT that can carry solicited service UUIDs.
    prefix = b"\x01\x14\x01\x15"

    solicited_services = ServiceList(standard_services=[0x14], vendor_services=[0x15])
    """List of services the device would like to use."""

    def __init__(self, *services):
        super().__init__()
        self.solicited_services.extend(services)
        self.connectable = True


class ManufacturerData:
    """Encapsulates manufacturer specific keyed data bytes. The manufacturer is identified by the
       company_id and the data is structured like an advertisement with a configurable key
       format."""
    def __init__(self, obj, *, advertising_data_type=0xff, company_id, key_encoding="B"):
        self._obj = obj
        self._company_id = company_id
        self._adt = advertising_data_type

        self.data = {}
        self.company_id = company_id
        encoded_company = struct.pack('<H', company_id)
        if 0xff in obj.data_dict:
            existing_data = obj.data_dict[0xff]
            if isinstance(existing_data, list):
                for existing in existing_data:
                    if existing.startswith(encoded_company):
                        existing_data = existing
                existing_data = None
            self.data = decode_data(existing_data[2:], key_encoding=key_encoding)
        self._key_encoding = key_encoding

    def __len__(self):
        return 2 + compute_length(self.data, key_encoding=self._key_encoding)

    def __bytes__(self):
        return (struct.pack('<H', self.company_id) +
                encode_data(self.data, key_encoding=self._key_encoding))

    def __str__(self):
        hex_data = to_hex(encode_data(self.data, key_encoding=self._key_encoding))
        return "<ManufacturerData company_id={:04x} data={} >".format(self.company_id, hex_data)

class ManufacturerDataField:
    """A single piece of data within the manufacturer specific data."""
    def __init__(self, key, key_format):
        self._key = key
        self._format = key_format

    def __get__(self, obj, cls):
        return struct.unpack_from(self._format, obj.manufacturer_data.data[self._key])[0]

    def __set__(self, obj, value):
        if not obj.mutable:
            raise AttributeError()
        obj.manufacturer_data.data[self._key] = struct.pack(self._format, value)

# TODO: Handle service data.

# SERVICE_DATA_128BIT_UUID = 0x21
# """Service data with 128 bit UUID."""

# SERVICE_DATA_16_BIT_UUID = 0x16
# """Service data with 16 bit UUID."""
