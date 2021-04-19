# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
:py:mod:`~adafruit_ble.advertising.standard`
====================================================

This module provides BLE standard defined advertisements. The Advertisements are single purpose
even though multiple purposes may actually be present in a single packet.

"""

import struct
from collections import OrderedDict, namedtuple

from . import (
    Advertisement,
    AdvertisingDataField,
    encode_data,
    decode_data,
    to_hex,
    compute_length,
)
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
                    uuid = StandardUUID(data[2 * i : 2 * (i + 1)])
                    self._standard_services.append(uuid)
        for adt in vendor_services:
            if adt in self._advertisement.data_dict:
                data = self._advertisement.data_dict[adt]
                for i in range(len(data) // 16):
                    uuid = VendorUUID(data[16 * i : 16 * (i + 1)])
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
        if (
            isinstance(service.uuid, StandardUUID)
            and service not in self._standard_services
        ):
            self._standard_services.append(service.uuid)
            self._update(self._standard_service_fields[0], self._standard_services)
        elif (
            isinstance(service.uuid, VendorUUID)
            and service not in self._vendor_services
        ):
            self._vendor_services.append(service.uuid)
            self._update(self._vendor_service_fields[0], self._vendor_services)

    # TODO: Differentiate between complete and incomplete lists.
    def extend(self, services):
        """Appends all services in the iterable to the list."""
        standard = False
        vendor = False
        for service in services:
            if (
                isinstance(service.uuid, StandardUUID)
                and service.uuid not in self._standard_services
            ):
                self._standard_services.append(service.uuid)
                standard = True
            elif (
                isinstance(service.uuid, VendorUUID)
                and service.uuid not in self._vendor_services
            ):
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
        return "<BoundServiceList: {}>".format(", ".join(data))


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
        if obj is None:
            return self
        if not self._present(obj) and not obj.mutable:
            return ()
        if not hasattr(obj, "adv_service_lists"):
            obj.adv_service_lists = {}
        first_adt = self.standard_services[0]
        if first_adt not in obj.adv_service_lists:
            obj.adv_service_lists[first_adt] = BoundServiceList(obj, **self.__dict__)
        return obj.adv_service_lists[first_adt]


class ProvideServicesAdvertisement(Advertisement):
    """Advertise what services that the device makes available upon connection."""

    # Prefixes that match each ADT that can carry service UUIDs.
    match_prefixes = (b"\x02", b"\x03", b"\x06", b"\x07")
    services = ServiceList(standard_services=[0x02, 0x03], vendor_services=[0x06, 0x07])
    """List of services the device can provide."""

    def __init__(self, *services, entry=None):
        super().__init__(entry=entry)
        if entry:
            if services:
                raise ValueError("Supply services or entry, not both")
            # Attributes are supplied by entry.
            return
        if services:
            self.services.extend(services)
        self.connectable = True
        self.flags.general_discovery = True
        self.flags.le_only = True

    @classmethod
    def matches(cls, entry):
        """Only one kind of service list need be present in a ProvideServicesAdvertisement,
        so override the default behavior and match any prefix, not all.
        """
        return cls.matches_prefixes(entry, all_=False)


class SolicitServicesAdvertisement(Advertisement):
    """Advertise what services the device would like to use over a connection."""

    # Prefixes that match each ADT that can carry solicited service UUIDs.
    match_prefixes = (b"\x14", b"\x15")

    solicited_services = ServiceList(standard_services=[0x14], vendor_services=[0x15])
    """List of services the device would like to use."""

    def __init__(self, *services, entry=None):
        super().__init__(entry=entry)
        if entry:
            if services:
                raise ValueError("Supply services or entry, not both")
            # Attributes are supplied by entry.
            return
        self.solicited_services.extend(services)
        self.connectable = True
        self.flags.general_discovery = True
        self.flags.le_only = True


class ManufacturerData(AdvertisingDataField):
    """Encapsulates manufacturer specific keyed data bytes. The manufacturer is identified by the
    company_id and the data is structured like an advertisement with a configurable key
    format. The order of the serialized data is determined by the order that the
    `ManufacturerDataField` attributes are set in - this can be useful for
    `match_prefixes` in an `Advertisement` sub-class."""

    def __init__(
        self, obj, *, advertising_data_type=0xFF, company_id, key_encoding="B"
    ):
        self._obj = obj
        self._company_id = company_id
        self._adt = advertising_data_type

        self.data = OrderedDict()  # makes field order match order they are set in
        self.company_id = company_id
        encoded_company = struct.pack("<H", company_id)
        if 0xFF in obj.data_dict:
            existing_data = obj.data_dict[0xFF]
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
        return struct.pack("<H", self.company_id) + encode_data(
            self.data, key_encoding=self._key_encoding
        )

    def __str__(self):
        hex_data = to_hex(encode_data(self.data, key_encoding=self._key_encoding))
        return "<ManufacturerData company_id={:04x} data={} >".format(
            self.company_id, hex_data
        )


class ManufacturerDataField:
    """A single piece of data within the manufacturer specific data. The format can be repeated."""

    def __init__(self, key, value_format, field_names=None):
        self._key = key
        self._format = value_format
        # TODO: Support format strings that use numbers to repeat a given type. For now, we strip
        # numbers because Radio specifies string length with it.
        self.element_count = len(value_format.strip("><!=@0123456789").replace("x", ""))
        if self.element_count > 1 and (
            not field_names or len(field_names) != self.element_count
        ):
            raise ValueError(
                "Provide field_names when multiple values are in the format"
            )
        self._entry_length = struct.calcsize(value_format)
        self.field_names = field_names
        if field_names:
            # Mostly, this is to raise a ValueError if field_names has invalid entries
            self.mdf_tuple = namedtuple("mdf_tuple", self.field_names)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self._key not in obj.manufacturer_data.data:
            return None
        packed = obj.manufacturer_data.data[self._key]
        if self._entry_length == len(packed):
            unpacked = struct.unpack_from(self._format, packed)
            if self.element_count == 1:
                unpacked = unpacked[0]
            if self.field_names and len(self.field_names) == len(unpacked):
                # If we have field names, we should already have a namedtuple type to use
                # Unless the element count is off, which... werid.
                return self.mdf_tuple(*unpacked)
            return unpacked
        if len(packed) % self._entry_length != 0:
            raise RuntimeError("Invalid data length")
        entry_count = len(packed) // self._entry_length
        unpacked = [None] * entry_count
        for i in range(entry_count):
            offset = i * self._entry_length
            unpacked[i] = struct.unpack_from(self._format, packed, offset=offset)
            if self.element_count == 1:
                unpacked[i] = unpacked[i][0]
        return tuple(unpacked)

    def __set__(self, obj, value):
        if not obj.mutable:
            raise AttributeError()
        if isinstance(value, tuple) and (
            self.element_count == 1 or isinstance(value[0], tuple)
        ):
            packed = bytearray(self._entry_length * len(value))
            for i, entry in enumerate(value):
                offset = i * self._entry_length
                if self.element_count > 1:
                    struct.pack_into(self._format, packed, offset, *entry)
                else:
                    struct.pack_into(self._format, packed, offset, entry)
            obj.manufacturer_data.data[self._key] = bytes(packed)
        elif self.element_count == 1:
            obj.manufacturer_data.data[self._key] = struct.pack(self._format, value)
        else:
            obj.manufacturer_data.data[self._key] = struct.pack(self._format, *value)


class ServiceData(AdvertisingDataField):
    """Encapsulates service data. It is read as a memoryview which can be manipulated or set as a
    bytearray to change the size."""

    def __init__(self, service):
        if isinstance(service.uuid, StandardUUID):
            self._adt = 0x16
        elif isinstance(service.uuid, VendorUUID):
            self._adt = 0x21
        self._prefix = bytes(service.uuid)

    def __get__(
        self, obj, cls
    ):  # pylint: disable=too-many-return-statements,too-many-branches
        if obj is None:
            return self
        # If not present at all and mutable, then we init it, otherwise None.
        if self._adt not in obj.data_dict:
            if obj.mutable:
                obj.data_dict[self._adt] = bytearray(self._prefix)
            else:
                return None

        all_service_data = obj.data_dict[self._adt]
        # Handle a list of existing data. This doesn't support multiple service data ADTs for the
        # same service.
        if isinstance(all_service_data, list):
            for i, service_data in enumerate(all_service_data):
                if service_data.startswith(self._prefix):
                    if not isinstance(service_data, bytearray):
                        service_data = bytearray(service_data)
                        all_service_data[i] = service_data
                    return memoryview(service_data)[len(self._prefix) :]
            if obj.mutable:
                service_data = bytearray(self._prefix)
                all_service_data.append(service_data)
                return memoryview(service_data)[len(self._prefix) :]
        # Existing data is a single set of bytes.
        elif isinstance(all_service_data, (bytes, bytearray)):
            service_data = all_service_data
            if not bytes(service_data).startswith(self._prefix):
                if not obj.mutable:
                    return None
                # Upgrade the value to a list.
                service_data = bytearray(self._prefix)
                obj.data_dict[self._adt] = [service_data, service_data]
            if not isinstance(service_data, bytearray):
                service_data = bytearray(service_data)
                obj.data_dict[self._adt] = service_data
            return memoryview(service_data)[len(self._prefix) :]

        return None

    def __set__(self, obj, value):
        if not obj.mutable:
            raise RuntimeError("Advertisement immutable")
        if not isinstance(value, bytearray):
            raise TypeError("Value must be bytearray")
        full_value = bytearray(self._prefix) + value
        if self._adt not in obj.data_dict:
            obj.data_dict[self._adt] = full_value
            return

        all_service_data = obj.data_dict[self._adt]
        if isinstance(all_service_data, list):
            for i, service_data in enumerate(all_service_data):
                if service_data.startswith(self._prefix):
                    all_service_data[i] = full_value
                    return
            all_service_data.append(full_value)
        elif isinstance(all_service_data, (bytes, bytearray)):
            obj.data_dict[self._adt] = full_value
