# SPDX-FileCopyrightText: 2018 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Advertising is the first phase of BLE where devices can broadcast
"""

from __future__ import annotations

import struct

try:
    from typing import (
        TYPE_CHECKING,
        Any,
        Dict,
        List,
        Optional,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    from typing_extensions import Literal

    if TYPE_CHECKING:
        from _bleio import Address, ScanEntry

        LazyObjectField_GivenClass = TypeVar(  # pylint: disable=invalid-name
            "LazyObjectField_GivenClass"
        )

        DataDict = Dict[int, Union[bytes, List[bytes]]]

except ImportError:
    pass


def to_hex(seq: bytes) -> str:
    """Pretty prints a byte sequence as hex values."""
    return " ".join("{:02x}".format(v) for v in seq)


def to_bytes_literal(seq: bytes) -> str:
    """Prints a byte sequence as a Python bytes literal that only uses hex encoding."""
    return 'b"' + "".join("\\x{:02x}".format(v) for v in seq) + '"'


def decode_data(data: bytes, *, key_encoding: str = "B") -> DataDict:
    """Helper which decodes length encoded structures into a dictionary with the given key
    encoding."""
    i = 0
    data_dict: DataDict = {}
    key_size = struct.calcsize(key_encoding)
    while i < len(data):
        item_length = data[i]
        i += 1
        if item_length == 0:
            break
        key = struct.unpack_from(key_encoding, data, i)[0]
        value = data[i + key_size : i + item_length]
        if key in data_dict:
            cur_value = data_dict[key]
            if isinstance(cur_value, list):
                cur_value.append(value)
            else:
                data_dict[key] = [cur_value, value]
        else:
            data_dict[key] = value
        i += item_length
    return data_dict


def compute_length(data_dict: DataDict, *, key_encoding: str = "B") -> int:
    """Computes the length of the encoded data dictionary."""
    value_size = 0
    for value in data_dict.values():
        if isinstance(value, list):
            for subv in value:
                value_size += len(subv)
        else:
            value_size += len(value)
    return len(data_dict) + len(data_dict) * struct.calcsize(key_encoding) + value_size


def encode_data(data_dict: DataDict, *, key_encoding: str = "B") -> bytes:
    """Helper which encodes dictionaries into length encoded structures with the given key
    encoding."""
    length = compute_length(data_dict, key_encoding=key_encoding)
    data = bytearray(length)
    key_size = struct.calcsize(key_encoding)
    i = 0
    for key, value in data_dict.items():
        if isinstance(value, list):
            value = b"".join(value)
        item_length = key_size + len(value)
        struct.pack_into("B", data, i, item_length)
        struct.pack_into(key_encoding, data, i + 1, key)
        data[i + 1 + key_size : i + 1 + item_length] = bytes(value)
        i += 1 + item_length
    return bytes(data)


# pylint: disable=too-few-public-methods
class AdvertisingDataField:
    """Top level class for any descriptor classes that live in Advertisement or its subclasses."""


class AdvertisingFlag:
    """A single bit flag within an AdvertisingFlags object."""

    def __init__(self, bit_position: int) -> None:
        self._bitmask = 1 << bit_position

    def __get__(
        self, obj: Optional["AdvertisingFlags"], cls: Type["AdvertisingFlags"]
    ) -> Union[bool, "AdvertisingFlag"]:
        if obj is None:
            return self
        return (obj.flags & self._bitmask) != 0

    def __set__(self, obj: "AdvertisingFlags", value: bool) -> None:
        if value:
            obj.flags |= self._bitmask
        else:
            obj.flags &= ~self._bitmask


class AdvertisingFlags(AdvertisingDataField):
    """Standard advertising flags"""

    limited_discovery = AdvertisingFlag(0)
    """Discoverable only for a limited time period."""
    general_discovery = AdvertisingFlag(1)
    """Will advertise until discovered."""
    le_only = AdvertisingFlag(2)
    """BR/EDR not supported."""
    # BR/EDR flags not included here, since we don't support BR/EDR.

    def __init__(
        self, advertisement: "Advertisement", advertising_data_type: int
    ) -> None:
        self._advertisement = advertisement
        self._adt = advertising_data_type
        self.flags = 0
        if self._adt in self._advertisement.data_dict:
            value = self._advertisement.data_dict[self._adt]
            if isinstance(value, list):
                raise RuntimeError
            self.flags = value[0]

    def __len__(self) -> Literal[1]:
        return 1

    def __bytes__(self) -> bytes:
        return bytes([self.flags])

    def __str__(self) -> str:
        parts = []
        for attr in dir(self.__class__):
            attribute_instance = getattr(self.__class__, attr)
            if issubclass(attribute_instance.__class__, AdvertisingFlag):
                if getattr(self, attr):
                    parts.append(attr)
        return "<AdvertisingFlags {} >".format(" ".join(parts))


class String(AdvertisingDataField):
    """UTF-8 encoded string in an Advertisement.

    Not null terminated once encoded because length is always transmitted."""

    def __init__(self, *, advertising_data_type: int) -> None:
        self._adt = advertising_data_type

    def __get__(
        self, obj: Optional["Advertisement"], cls: Type["Advertisement"]
    ) -> Optional[Union[str, "String"]]:
        if obj is None:
            return self
        if self._adt not in obj.data_dict:
            return None
        value = obj.data_dict[self._adt]
        if isinstance(value, list):
            raise RuntimeError
        return str(value, "utf-8")

    def __set__(self, obj: "Advertisement", value: str) -> None:
        obj.data_dict[self._adt] = value.encode("utf-8")


class Struct(AdvertisingDataField):
    """`struct` encoded data in an Advertisement."""

    def __init__(self, struct_format: str, *, advertising_data_type: int) -> None:
        self._format = struct_format
        self._adt = advertising_data_type

    def __get__(
        self, obj: Optional["Advertisement"], cls: Type["Advertisement"]
    ) -> Optional[Union[Any, "Struct"]]:
        if obj is None:
            return self
        if self._adt not in obj.data_dict:
            return None
        value = obj.data_dict[self._adt]
        if isinstance(value, list):
            raise RuntimeError
        return struct.unpack(self._format, value)[0]

    def __set__(self, obj: "Advertisement", value: Any) -> None:
        obj.data_dict[self._adt] = struct.pack(self._format, value)


class LazyObjectField(AdvertisingDataField):
    """Non-data descriptor useful for lazily binding a complex object to an advertisement object."""

    def __init__(
        self, cls: Any, attribute_name: str, *, advertising_data_type: int, **kwargs
    ) -> None:
        self._cls = cls
        self._attribute_name = attribute_name
        self._adt = advertising_data_type
        self._kwargs = kwargs

    def __get__(
        self, obj: Optional["Advertisement"], cls: Type["Advertisement"]
    ) -> Any:
        if obj is None:
            return self
        # Return None if our object is immutable and the data is not present.
        if not obj.mutable and self._adt not in obj.data_dict:
            return None
        # Instantiate the object.
        bound_obj = self._cls(obj, advertising_data_type=self._adt, **self._kwargs)
        setattr(obj, self._attribute_name, bound_obj)
        obj.data_dict[self._adt] = bound_obj
        return bound_obj

    @property
    def advertising_data_type(self) -> int:
        """Return the data type value used to indicate this field."""
        return self._adt

    # TODO: Add __set_name__ support to CircuitPython so that we automatically tell the descriptor
    # instance the attribute name it has and the class it is on.


class Advertisement:
    """Core Advertisement type.

    The class attribute ``match_prefixes``, if not ``None``, is a tuple of
    bytestring prefixes to match against the multiple data structures in the advertisement.
    """

    match_prefixes: Optional[Tuple[bytes, ...]] = ()
    """For Advertisement, :py:attr:`~adafruit_ble.advertising.Advertisement.match_prefixes`
    will always return ``True``. Subclasses may override this value."""
    # cached bytes of merged prefixes.
    _prefix_bytes = None

    flags = LazyObjectField(AdvertisingFlags, "flags", advertising_data_type=0x01)
    short_name = String(advertising_data_type=0x08)
    """Short local device name (shortened to fit)."""
    complete_name = String(advertising_data_type=0x09)
    """Complete local device name."""
    tx_power = Struct("<b", advertising_data_type=0x0A)
    """Transmit power level"""
    # DEVICE_ID = 0x10
    # """Device identifier."""
    # SLAVE_CONN_INTERVAL_RANGE = 0x12
    # """Slave connection interval range."""
    # PUBLIC_TARGET_ADDRESS = 0x17
    # """Public target address."""
    # RANDOM_TARGET_ADDRESS = 0x18
    # """Random target address (chosen randomly)."""
    # APPEARANCE = 0x19
    appearance = Struct("<H", advertising_data_type=0x19)
    """Appearance."""
    # DEVICE_ADDRESS = 0x1B
    # """LE Bluetooth device address."""
    # ROLE = 0x1C
    # """LE Role."""
    #
    # MAX_LEGACY_DATA_SIZE = 31
    # """Data size in a regular BLE packet."""

    def __init__(self, *, entry: Optional[ScanEntry] = None) -> None:
        """Create an empty advertising packet or one from a ScanEntry."""
        if entry:
            self.data_dict = decode_data(entry.advertisement_bytes)
            self.address = entry.address
            self._rssi = entry.rssi  # pylint: disable=protected-access
            self.connectable = entry.connectable
            self.scan_response = entry.scan_response
            self.mutable = False
        else:
            self.data_dict = {}
            self.address = None
            self._rssi = None
            self.connectable = False
            self.mutable = True
            self.scan_response = False

    @property
    def rssi(self) -> Optional[int]:
        """Signal strength of the scanned advertisement. Only available on Advertisements returned
        from `BLERadio.start_scan()`. (read-only)"""
        return self._rssi

    @classmethod
    def get_prefix_bytes(cls) -> bytes:
        """Return a merged version of match_prefixes as a single bytes object,
        with length headers.
        """
        # Check for deprecated `prefix` class attribute.
        prefix_bytes: Optional[bytes] = getattr(cls, "prefix", None)

        # Do merge once and memoize it.
        cls._prefix_bytes = (
            (
                b""
                if cls.match_prefixes is None
                else b"".join(
                    len(prefix).to_bytes(1, "little") + prefix
                    for prefix in cls.match_prefixes
                )
            )
            if prefix_bytes is None
            else prefix_bytes
        )

        return cls._prefix_bytes

    @classmethod
    def matches(cls, entry: ScanEntry) -> bool:
        """Returns ``True`` if the given `_bleio.ScanEntry` advertisement fields
        matches all of the given prefixes in the `match_prefixes` tuple attribute.
        Subclasses may override this to match any instead of all.
        """
        return cls.matches_prefixes(entry, all_=True)

    @classmethod
    def matches_prefixes(cls, entry: ScanEntry, *, all_: bool) -> bool:
        """Returns ``True`` if the given `_bleio.ScanEntry` advertisement fields
        match any or all of the given prefixes in the `match_prefixes` tuple attribute.
        If ``all_`` is ``True``, all the prefixes must match. If ``all_`` is ``False``,
        returns ``True`` if at least one of the prefixes match.
        """
        # Returns True if cls.get_prefix_bytes() is empty.
        return entry.matches(cls.get_prefix_bytes(), match_all=all_)

    def __bytes__(self) -> bytes:
        """The raw packet bytes."""
        return encode_data(self.data_dict)

    def __eq__(self, other) -> bool:
        if isinstance(other, Advertisement):
            return self.data_dict == other.data_dict
        return False

    def __str__(self) -> str:
        parts = []
        for attr in dir(self.__class__):
            attribute_instance = getattr(self.__class__, attr)
            if issubclass(attribute_instance.__class__, AdvertisingDataField):
                if (
                    issubclass(attribute_instance.__class__, LazyObjectField)
                    and not attribute_instance.advertising_data_type in self.data_dict
                ):
                    # Skip uninstantiated lazy objects; if we get
                    # their value, they will be be instantiated.
                    continue
                value = getattr(self, attr)
                if value is not None:
                    parts.append("{}={}".format(attr, str(value)))
        return "<{} {} >".format(self.__class__.__name__, " ".join(parts))

    def __len__(self) -> int:
        return compute_length(self.data_dict)

    def __repr__(self) -> str:
        return "Advertisement(data={})".format(
            to_bytes_literal(encode_data(self.data_dict))
        )
