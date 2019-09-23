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
:py:mod:`~adafruit_ble.characteristics.core`
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

    def bind(self, obj, *, initial_value=None):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
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
            obj,
            self.uuid._uuid, # pylint: disable=protected-access
            initial_value=initial_value,
            max_length=max_length,
            **self.kwargs
        )

    def write_raw_data(self, bound_characteristic, data):
        """Writes the data out to the bound characteristic."""
        # pylint: disable=no-self-use
        bound_characteristic.value = data

    def read_raw_data(self, bound_characteristic):
        """Reads data out of the bound characteristic."""
        # pylint: disable=no-self-use
        return bound_characteristic.value

class ComplexCharacteristic(Characteristic):
    """Characteristic class that does complex binding where the subclass returns a full object for
       interacting with the characteristic data. The Characteristic itself will be shadowed once it
       has been bound to the corresponding instance attribute."""

class BytesCharacteristic(Characteristic):
    """Data descriptor for a variable length byte array."""
    def __get__(self, obj, cls=None):
        if not hasattr(obj, "_bound_characteristics"):
            return self.initial_value
        bound_characteristic = obj._bound_characteristics[self.field_name]
        raw_data = self.read_raw_data(bound_characteristic)
        return raw_data

    def __set__(self, obj, value):
        if not hasattr(obj, "_bound_characteristics"):
            self.initial_value = value
            if "fixed_length" in self.kwargs and self.kwargs["fixed_length"]:
                self.kwargs["max_length"] = len(value)
            return
        bound_characteristic = obj._bound_characteristics[self.field_name]
        self.write_raw_data(bound_characteristic, value)

class StructCharacteristic(Characteristic):
    """Data descriptor for a structure with a fixed format."""
    def __init__(self, struct_format, **kwargs):
        self._struct_format = struct_format
        self._expected_size = struct.calcsize(struct_format)
        if "initial_value" in kwargs:
            kwargs["initial_value"] = struct.pack(self._struct_format, *kwargs["initial_value"])
        super().__init__(**kwargs, max_length=self._expected_size, fixed_length=True)

    def __get__(self, obj, cls=None):
        bound_characteristic = obj._bound_characteristics[self.field_name]
        raw_data = self.read_raw_data(bound_characteristic)
        if len(raw_data) < self._expected_size:
            print(raw_data)
            return None
        return struct.unpack(self._struct_format, raw_data)

    def __set__(self, obj, value):
        bound_characteristic = obj._bound_characteristics[self.field_name]
        encoded = struct.pack(self._struct_format, *value)
        self.write_raw_data(bound_characteristic, encoded)
