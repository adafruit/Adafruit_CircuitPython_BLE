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
:py:mod:`~adafruit_ble.characteristics`
====================================================

This module provides core BLE characteristic classes that are used within Services.

"""

import struct
import _bleio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class Characteristic:
    """Top level Characteristic class that does basic binding."""
    def __init__(self, *, uuid=None, initial_value=None, max_length=None, **kwargs):
        if uuid:
            self.uuid = uuid
        self.kwargs = kwargs
        self.initial_value = initial_value
        self.max_length = max_length
        self.field_name = None # Set by Service during basic binding

    def _ensure_bound(self, service, initial_value=None):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
        if self.field_name in service.bleio_characteristics:
            return
        if service.remote:
            bleio_characteristic = None
            remote_characteristics = service.bleio_service.characteristics
            for characteristic in remote_characteristics:
                if characteristic.uuid == self.uuid.bleio_uuid:
                    bleio_characteristic = characteristic
                    break
            if not bleio_characteristic:
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
            max_length = 20
            initial_value = bytes(max_length)
        if max_length is None:
            max_length = len(initial_value)
        return _bleio.Characteristic.add_to_service(
            service.bleio_service,
            self.uuid.bleio_uuid,
            initial_value=initial_value,
            max_length=max_length,
            **self.kwargs
        )

    def __get__(self, service, cls=None):
        self._ensure_bound(service)
        bleio_characteristic = service.bleio_characteristics[self.field_name]
        raw_data = bleio_characteristic.value
        return raw_data

    def __set__(self, service, value):
        self._ensure_bound(service, value)
        bleio_characteristic = service.bleio_characteristics[self.field_name]
        bleio_characteristic.value = value

class ComplexCharacteristic:
    """Characteristic class that does complex binding where the subclass returns a full object for
       interacting with the characteristic data. The Characteristic itself will be shadowed once it
       has been bound to the corresponding instance attribute."""
    def __init__(self, *, uuid=None, **kwargs):
        if uuid:
            self.uuid = uuid
        self.kwargs = kwargs
        self.field_name = None # Set by Service

    def bind(self, service):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
        if service.remote:
            remote_characteristics = service.bleio_service.characteristics
            for characteristic in remote_characteristics:
                if characteristic.uuid == self.uuid.bleio_uuid:
                    return characteristic
            raise AttributeError("Characteristic not available on remote service")
        return _bleio.Characteristic.add_to_service(
            service.bleio_service,
            self.uuid.bleio_uuid,
            **self.kwargs
        )

    def __get__(self, service, cls=None):
        bound_object = self.bind(service)
        setattr(service, self.field_name, bound_object)
        return bound_object

class StructCharacteristic(Characteristic):
    """Data descriptor for a structure with a fixed format."""
    def __init__(self, struct_format, **kwargs):
        self._struct_format = struct_format
        self._expected_size = struct.calcsize(struct_format)
        if "initial_value" in kwargs:
            kwargs["initial_value"] = struct.pack(self._struct_format, *kwargs["initial_value"])
        super().__init__(**kwargs, max_length=self._expected_size, fixed_length=True)

    def __get__(self, obj, cls=None):
        raw_data = super().__get__(obj, cls)
        if len(raw_data) < self._expected_size:
            return None
        return struct.unpack(self._struct_format, raw_data)

    def __set__(self, obj, value):
        encoded = struct.pack(self._struct_format, *value)
        super().__set__(obj, encoded)
