# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""

This module provides core BLE characteristic classes that are used within Services.

"""

import struct
import _bleio

from ..attributes import Attribute

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class Characteristic:
    """
    Top level Characteristic class that does basic binding.

    :param UUID uuid: The uuid of the characteristic
    :param int properties: The properties of the characteristic,
       specified as a bitmask of these values bitwise-or'd together:
       `BROADCAST`, `INDICATE`, `NOTIFY`, `READ`, `WRITE`, `WRITE_NO_RESPONSE`.
    :param int read_perm: Specifies whether the characteristic can be read by a client,
       and if so, which security mode is required.
       Must be one of the integer values `Attribute.NO_ACCESS`, `Attribute.OPEN`,
       `Attribute.ENCRYPT_NO_MITM`, `Attribute.ENCRYPT_WITH_MITM`,
       `Attribute.LESC_ENCRYPT_WITH_MITM`,
       `Attribute.SIGNED_NO_MITM`, or `Attribute.SIGNED_WITH_MITM`.
    :param int write_perm: Specifies whether the characteristic can be written by a client,
       and if so, which security mode is required. Values allowed are the same as ``read_perm``.
    :param int max_length: Maximum length in bytes of the characteristic value. The maximum allowed
       by the BLE specification is 512. On nRF, if ``fixed_length`` is ``True``, the maximum
       is 510. The default value is 20, which is the maximum
       number of data bytes that fit in a single BLE 4.x ATT packet.
    :param bool fixed_length: True if the characteristic value is of fixed length.
    :param buf initial_value: The initial value for this characteristic. If not given, will be
       filled with zeros.

    .. data:: BROADCAST

       property: allowed in advertising packets

    .. data:: INDICATE

         property: server will indicate to the client when the value is set and wait for a response

    .. data:: NOTIFY

       property: server will notify the client when the value is set

    .. data:: READ

       property: clients may read this characteristic

    .. data:: WRITE

       property: clients may write this characteristic; a response will be sent back

    .. data:: WRITE_NO_RESPONSE

       property: clients may write this characteristic; no response will be sent back"""

    BROADCAST = _bleio.Characteristic.BROADCAST
    INDICATE = _bleio.Characteristic.INDICATE
    NOTIFY = _bleio.Characteristic.NOTIFY
    READ = _bleio.Characteristic.READ
    WRITE = _bleio.Characteristic.WRITE
    WRITE_NO_RESPONSE = _bleio.Characteristic.WRITE_NO_RESPONSE

    def __init__(
        self,
        *,
        uuid=None,
        properties=0,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        max_length=None,
        fixed_length=False,
        initial_value=None
    ):
        self.field_name = None  # Set by Service during basic binding

        if uuid:
            self.uuid = uuid
        self.properties = properties
        self.read_perm = read_perm
        self.write_perm = write_perm
        self.max_length = max_length
        self.fixed_length = fixed_length
        self.initial_value = initial_value

    def _ensure_bound(self, service, initial_value=None):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
        if self.field_name in service.bleio_characteristics:
            return
        if service.remote:
            for characteristic in service.bleio_service.characteristics:
                if characteristic.uuid == self.uuid.bleio_uuid:
                    bleio_characteristic = characteristic
                    break
            else:
                raise AttributeError("Characteristic not available on remote service")
        else:
            bleio_characteristic = self.__bind_locally(service, initial_value)

        service.bleio_characteristics[self.field_name] = bleio_characteristic

    def __bind_locally(self, service, initial_value):
        if initial_value is None:
            initial_value = self.initial_value
        if initial_value is None and self.max_length:
            initial_value = bytes(self.max_length)
        max_length = self.max_length
        if max_length is None and initial_value is None:
            max_length = 0
            initial_value = b""
        elif max_length is None:
            max_length = len(initial_value)
        return _bleio.Characteristic.add_to_service(
            service.bleio_service,
            self.uuid.bleio_uuid,
            initial_value=initial_value,
            max_length=max_length,
            fixed_length=self.fixed_length,
            properties=self.properties,
            read_perm=self.read_perm,
            write_perm=self.write_perm,
        )

    def __get__(self, service, cls=None):
        # CircuitPython doesn't invoke descriptor protocol on obj's class,
        # but CPython does. In the CPython case, pretend that it doesn't.
        if service is None:
            return self
        self._ensure_bound(service)
        bleio_characteristic = service.bleio_characteristics[self.field_name]
        return bleio_characteristic.value

    def __set__(self, service, value):
        self._ensure_bound(service, value)
        if value is None:
            value = b""
        bleio_characteristic = service.bleio_characteristics[self.field_name]
        bleio_characteristic.value = value


class ComplexCharacteristic:
    """
    Characteristic class that does complex binding where the subclass returns a full object for
    interacting with the characteristic data. The Characteristic itself will be shadowed once it
    has been bound to the corresponding instance attribute.
    """

    def __init__(
        self,
        *,
        uuid=None,
        properties=0,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        max_length=20,
        fixed_length=False,
        initial_value=None
    ):
        self.field_name = None  # Set by Service during basic binding

        if uuid:
            self.uuid = uuid
        self.properties = properties
        self.read_perm = read_perm
        self.write_perm = write_perm
        self.max_length = max_length
        self.fixed_length = fixed_length
        self.initial_value = initial_value

    def bind(self, service):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
        if service.remote:
            for characteristic in service.bleio_service.characteristics:
                if characteristic.uuid == self.uuid.bleio_uuid:
                    return characteristic
            raise AttributeError("Characteristic not available on remote service")
        return _bleio.Characteristic.add_to_service(
            service.bleio_service,
            self.uuid.bleio_uuid,
            initial_value=self.initial_value,
            max_length=self.max_length,
            properties=self.properties,
            read_perm=self.read_perm,
            write_perm=self.write_perm,
        )

    def __get__(self, service, cls=None):
        if service is None:
            return self
        bound_object = self.bind(service)
        setattr(service, self.field_name, bound_object)
        return bound_object


class StructCharacteristic(Characteristic):
    """
    Data descriptor for a structure with a fixed format.

    :param struct_format: a `struct` format string describing how to pack multiple values
      into the characteristic bytestring
    :param UUID uuid: The uuid of the characteristic
    :param int properties: see `Characteristic`
    :param int read_perm: see `Characteristic`
    :param int write_perm: see `Characteristic`
    :param buf initial_value: see `Characteristic`
    """

    def __init__(
        self,
        struct_format,
        *,
        uuid=None,
        properties=0,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        initial_value=None
    ):
        self._struct_format = struct_format
        self._expected_size = struct.calcsize(struct_format)
        if initial_value is not None:
            initial_value = struct.pack(self._struct_format, *initial_value)
        super().__init__(
            uuid=uuid,
            initial_value=initial_value,
            max_length=self._expected_size,
            fixed_length=True,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
        )

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        raw_data = super().__get__(obj, cls)
        if len(raw_data) < self._expected_size:
            return None
        return struct.unpack(self._struct_format, raw_data)

    def __set__(self, obj, value):
        encoded = struct.pack(self._struct_format, *value)
        super().__set__(obj, encoded)
