# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""

This module provides the top level Service definition.

"""

import _bleio

from ..characteristics import Characteristic, ComplexCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class Service:
    """Top level Service class that handles the hard work of binding to a local or remote service.

    Providers of a local service should instantiate their Service with service=None, the default.
    The local Service's characteristics will be lazily made available to clients as they are used
    locally. In other words, a characteristic won't be available to remote clients until it has
    been read or written locally.

    To use a remote Service, get the item with the key of the Service type on the
    `BLEConnection`. For example, ``connection[UartService]`` will return the UartService
    instance for the connection's peer.
    """

    def __init__(self, *, service=None, secondary=False, **initial_values):
        if service is None:
            # pylint: disable=no-member
            self.bleio_service = _bleio.Service(
                self.uuid.bleio_uuid, secondary=secondary
            )
        elif not service.remote:
            raise ValueError("Can only create services with a remote service or None")
        else:
            self.bleio_service = service

        # This internal dictionary is manipulated by the Characteristic descriptors to store their
        # per-Service state. It is NOT managed by the Service itself. It is an attribute of the
        # Service so that the lifetime of the objects is the same as the Service.
        self.bleio_characteristics = {}

        # Set the field name on all of the characteristic objects so they can replace themselves if
        # they choose.
        # TODO: Replace this with __set_name__ support.
        for class_attr in dir(self.__class__):
            if class_attr.startswith("__"):
                continue
            value = getattr(self.__class__, class_attr)
            if not isinstance(value, Characteristic) and not isinstance(
                value, ComplexCharacteristic
            ):
                continue

            value.field_name = class_attr

            # Get or set every attribute to ensure that they are all bound up front. We could lazily
            # init them but the Nordic Soft Device requires characteristics be added immediately
            # after the Service. In other words, only characteristics for the most recently added
            # service can be added.
            if not self.remote:
                if class_attr in initial_values:
                    setattr(self, class_attr, initial_values[class_attr])
                else:
                    getattr(self, class_attr)

    @property
    def remote(self):
        """True if the service is provided by a peer and accessed remotely."""
        return self.bleio_service.remote
