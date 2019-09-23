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
:py:mod:`~adafruit_ble.services.core`
====================================================

This module provides the top level Service definition.

"""

import _bleio

from ..characteristics.core import Characteristic, ComplexCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class Service:
    """Top level Service class that handles the hard work of binding to a local or remote service.

       Providers of a local service should instantiate their Service with service=None, the default.

       To use a remote Service, read the corresponding attribute on the `SmartConnection`. The
       attribute names match the Service's ``default_field_name``.
    """
    def __init__(self, *, service=None, secondary=False, **initial_values):
        if service is None:
            # pylint: disable=no-member
            self._service = _bleio.Service(self.uuid._uuid, secondary=secondary)
        elif not service.remote:
            raise ValueError("Can only create services with a remote service or None")
        else:
            self._service = service

        if self._service.remote:
            self.__init_remote()
        else:
            self.__init_local(initial_values)

    def __init_local(self, initial_values):
        self._bound_characteristics = {}
        for class_attr in dir(self.__class__):
            if class_attr.startswith("__"):
                continue
            value = getattr(self.__class__, class_attr)
            if isinstance(value, ComplexCharacteristic):
                setattr(self, class_attr, value.bind(self._service))
            elif isinstance(value, Characteristic):
                initial_value = initial_values.get(class_attr, None)
                self._bound_characteristics[class_attr] = value.bind(self._service,
                                                                     initial_value=initial_value)
                value.field_name = class_attr

    def __init_remote(self):
        remote_service = self._service
        uuid_to_bc = {}
        for characteristic in remote_service.characteristics:
            uuid_to_bc[characteristic.uuid] = characteristic

        self._bound_characteristics = {}
        for class_attr in dir(self.__class__):
            if class_attr.startswith("__"):
                continue
            value = getattr(self.__class__, class_attr)
            if not isinstance(value, Characteristic):
                continue
            uuid = value.uuid._uuid # pylint: disable=protected-access
            if isinstance(value, ComplexCharacteristic):
                setattr(self, class_attr, value.bind(uuid_to_bc[uuid]))
            elif isinstance(value, Characteristic):
                if uuid in uuid_to_bc:
                    self._bound_characteristics[class_attr] = uuid_to_bc[uuid]
                    value.field_name = class_attr
        return self
