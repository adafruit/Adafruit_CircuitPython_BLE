# SPDX-FileCopyrightText: 2019 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
:py:mod:`~adafruit_ble.services.standard.hid`
=======================================================

BLE Human Interface Device (HID)

* Author(s): Dan Halbert for Adafruit Industries

"""
import struct

from micropython import const
import _bleio

from adafruit_ble.characteristics import Attribute
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.int import Uint8Characteristic
from adafruit_ble.uuid import StandardUUID

from .. import Service

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

_HID_SERVICE_UUID_NUM = const(0x1812)
_REPORT_UUID_NUM = const(0x2A4D)
_REPORT_MAP_UUID_NUM = const(0x2A4B)
_HID_INFORMATION_UUID_NUM = const(0x2A4A)
_HID_CONTROL_POINT_UUID_NUM = const(0x2A4C)
_REPORT_REF_DESCR_UUID_NUM = const(0x2908)
_REPORT_REF_DESCR_UUID = _bleio.UUID(_REPORT_REF_DESCR_UUID_NUM)
_PROTOCOL_MODE_UUID_NUM = const(0x2A4E)

_APPEARANCE_HID_KEYBOARD = const(961)
_APPEARANCE_HID_MOUSE = const(962)
_APPEARANCE_HID_JOYSTICK = const(963)
_APPEARANCE_HID_GAMEPAD = const(964)

# pylint: disable=line-too-long
DEFAULT_HID_DESCRIPTOR = (
    b"\x05\x01"  # Usage Page (Generic Desktop Ctrls)
    b"\x09\x06"  # Usage (Keyboard)
    b"\xA1\x01"  # Collection (Application)
    b"\x85\x01"  #   Report ID (1)
    b"\x05\x07"  #   Usage Page (Kbrd/Keypad)
    b"\x19\xE0"  #   Usage Minimum (\xE0)
    b"\x29\xE7"  #   Usage Maximum (\xE7)
    b"\x15\x00"  #   Logical Minimum (0)
    b"\x25\x01"  #   Logical Maximum (1)
    b"\x75\x01"  #   Report Size (1)
    b"\x95\x08"  #   Report Count (8)
    b"\x81\x02"  #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b"\x81\x01"  #   Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b"\x19\x00"  #   Usage Minimum (\x00)
    b"\x29\x89"  #   Usage Maximum (\x89)
    b"\x15\x00"  #   Logical Minimum (0)
    b"\x25\x89"  #   Logical Maximum (137)
    b"\x75\x08"  #   Report Size (8)
    b"\x95\x06"  #   Report Count (6)
    b"\x81\x00"  #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b"\x05\x08"  #   Usage Page (LEDs)
    b"\x19\x01"  #   Usage Minimum (Num Lock)
    b"\x29\x05"  #   Usage Maximum (Kana)
    b"\x15\x00"  #   Logical Minimum (0)
    b"\x25\x01"  #   Logical Maximum (1)
    b"\x75\x01"  #   Report Size (1)
    b"\x95\x05"  #   Report Count (5)
    b"\x91\x02"  #   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
    b"\x95\x03"  #   Report Count (3)
    b"\x91\x01"  #   Output (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
    b"\xC0"  # End Collection
    b"\x05\x01"  # Usage Page (Generic Desktop Ctrls)
    b"\x09\x02"  # Usage (Mouse)
    b"\xA1\x01"  # Collection (Application)
    b"\x09\x01"  #   Usage (Pointer)
    b"\xA1\x00"  #   Collection (Physical)
    b"\x85\x02"  #     Report ID (2)
    b"\x05\x09"  #     Usage Page (Button)
    b"\x19\x01"  #     Usage Minimum (\x01)
    b"\x29\x05"  #     Usage Maximum (\x05)
    b"\x15\x00"  #     Logical Minimum (0)
    b"\x25\x01"  #     Logical Maximum (1)
    b"\x95\x05"  #     Report Count (5)
    b"\x75\x01"  #     Report Size (1)
    b"\x81\x02"  #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b"\x95\x01"  #     Report Count (1)
    b"\x75\x03"  #     Report Size (3)
    b"\x81\x01"  #     Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b"\x05\x01"  #     Usage Page (Generic Desktop Ctrls)
    b"\x09\x30"  #     Usage (X)
    b"\x09\x31"  #     Usage (Y)
    b"\x15\x81"  #     Logical Minimum (-127)
    b"\x25\x7F"  #     Logical Maximum (127)
    b"\x75\x08"  #     Report Size (8)
    b"\x95\x02"  #     Report Count (2)
    b"\x81\x06"  #     Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)
    b"\x09\x38"  #     Usage (Wheel)
    b"\x15\x81"  #     Logical Minimum (-127)
    b"\x25\x7F"  #     Logical Maximum (127)
    b"\x75\x08"  #     Report Size (8)
    b"\x95\x01"  #     Report Count (1)
    b"\x81\x06"  #     Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)
    b"\xC0"  #   End Collection
    b"\xC0"  # End Collection
    b"\x05\x0C"  # Usage Page (Consumer)
    b"\x09\x01"  # Usage (Consumer Control)
    b"\xA1\x01"  # Collection (Application)
    b"\x85\x03"  #   Report ID (3)
    b"\x75\x10"  #   Report Size (16)
    b"\x95\x01"  #   Report Count (1)
    b"\x15\x01"  #   Logical Minimum (1)
    b"\x26\x8C\x02"  #   Logical Maximum (652)
    b"\x19\x01"  #   Usage Minimum (Consumer Control)
    b"\x2A\x8C\x02"  #   Usage Maximum (AC Send)
    b"\x81\x00"  #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b"\xC0"  # End Collection
    # b'\x05\x01'        # Usage Page (Generic Desktop Ctrls)
    # b'\x09\x05'        # Usage (Game Pad)
    # b'\xA1\x01'        # Collection (Application)
    # b'\x85\x05'        #   Report ID (5)
    # b'\x05\x09'        #   Usage Page (Button)
    # b'\x19\x01'        #   Usage Minimum (\x01)
    # b'\x29\x10'        #   Usage Maximum (\x10)
    # b'\x15\x00'        #   Logical Minimum (0)
    # b'\x25\x01'        #   Logical Maximum (1)
    # b'\x75\x01'        #   Report Size (1)
    # b'\x95\x10'        #   Report Count (16)
    # b'\x81\x02'        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    # b'\x05\x01'        #   Usage Page (Generic Desktop Ctrls)
    # b'\x15\x81'        #   Logical Minimum (-127)
    # b'\x25\x7F'        #   Logical Maximum (127)
    # b'\x09\x30'        #   Usage (X)
    # b'\x09\x31'        #   Usage (Y)
    # b'\x09\x32'        #   Usage (Z)
    # b'\x09\x35'        #   Usage (Rz)
    # b'\x75\x08'        #   Report Size (8)
    # b'\x95\x04'        #   Report Count (4)
    # b'\x81\x02'        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    # b'\xC0'            # End Collection
)
"""Default HID descriptor: provides mouse, keyboard, and consumer control devices."""
# pylint: enable=line-too-long


# Boot keyboard and mouse not currently supported.
_BOOT_KEYBOARD_INPUT_REPORT_UUID_NUM = const(0x2A22)
_BOOT_KEYBOARD_OUTPUT_REPORT_UUID_NUM = const(0x2A32)
_BOOT_MOUSE_INPUT_REPORT_UUID_NUM = const(0x2A33)

# Output reports not currently implemented (e.g. LEDs on keyboard)
_REPORT_TYPE_INPUT = const(1)
_REPORT_TYPE_OUTPUT = const(2)

# Boot Protocol mode not currently implemented
_PROTOCOL_MODE_BOOT = b"\x00"
_PROTOCOL_MODE_REPORT = b"\x01"


class ReportIn:
    """A single HID report that transmits HID data into a client."""

    uuid = StandardUUID(_REPORT_UUID_NUM)

    def __init__(self, service, report_id, usage_page, usage, *, max_length):
        self._characteristic = _bleio.Characteristic.add_to_service(
            service.bleio_service,
            self.uuid.bleio_uuid,
            properties=Characteristic.READ | Characteristic.NOTIFY,
            read_perm=Attribute.ENCRYPT_NO_MITM,
            write_perm=Attribute.NO_ACCESS,
            max_length=max_length,
            fixed_length=True,
        )
        self._report_id = report_id
        self.usage_page = usage_page
        self.usage = usage

        _bleio.Descriptor.add_to_characteristic(
            self._characteristic,
            _REPORT_REF_DESCR_UUID,
            read_perm=Attribute.ENCRYPT_NO_MITM,
            write_perm=Attribute.NO_ACCESS,
            initial_value=struct.pack("<BB", self._report_id, _REPORT_TYPE_INPUT),
        )

    def send_report(self, report):
        """Send a report to the peers"""
        self._characteristic.value = report


class ReportOut:
    """A single HID report that receives HID data from a client."""

    # pylint: disable=too-few-public-methods
    uuid = StandardUUID(_REPORT_UUID_NUM)

    def __init__(self, service, report_id, usage_page, usage, *, max_length):
        self._characteristic = _bleio.Characteristic.add_to_service(
            service.bleio_service,
            self.uuid.bleio_uuid,
            max_length=max_length,
            fixed_length=True,
            properties=(
                Characteristic.READ
                | Characteristic.WRITE
                | Characteristic.WRITE_NO_RESPONSE
            ),
            read_perm=Attribute.ENCRYPT_NO_MITM,
            write_perm=Attribute.ENCRYPT_NO_MITM,
        )
        self._report_id = report_id
        self.usage_page = usage_page
        self.usage = usage

        _bleio.Descriptor.add_to_characteristic(
            self._characteristic,
            _REPORT_REF_DESCR_UUID,
            read_perm=Attribute.ENCRYPT_NO_MITM,
            write_perm=Attribute.NO_ACCESS,
            initial_value=struct.pack("<BB", self._report_id, _REPORT_TYPE_OUTPUT),
        )

    @property
    def report(self):
        """The HID OUT report"""
        return self._characteristic.value


_ITEM_TYPE_MAIN = const(0)
_ITEM_TYPE_GLOBAL = const(1)
_ITEM_TYPE_LOCAL = const(2)

_MAIN_ITEM_TAG_START_COLLECTION = const(0b1010)
_MAIN_ITEM_TAG_END_COLLECTION = const(0b1100)
_MAIN_ITEM_TAG_INPUT = const(0b1000)
_MAIN_ITEM_TAG_OUTPUT = const(0b1001)
_MAIN_ITEM_TAG_FEATURE = const(0b1011)


class HIDService(Service):
    """
    Provide devices for HID over BLE.

    :param str hid_descriptor: USB HID descriptor that describes the structure of the reports. Known
        as the report map in BLE HID.

    Example::

        from adafruit_ble.hid_server import HIDServer

        hid = HIDServer()
    """

    uuid = StandardUUID(0x1812)

    boot_keyboard_in = Characteristic(
        uuid=StandardUUID(0x2A22),
        properties=(Characteristic.READ | Characteristic.NOTIFY),
        read_perm=Attribute.ENCRYPT_NO_MITM,
        write_perm=Attribute.NO_ACCESS,
        max_length=8,
        fixed_length=True,
    )

    boot_keyboard_out = Characteristic(
        uuid=StandardUUID(0x2A32),
        properties=(
            Characteristic.READ
            | Characteristic.WRITE
            | Characteristic.WRITE_NO_RESPONSE
        ),
        read_perm=Attribute.ENCRYPT_NO_MITM,
        write_perm=Attribute.ENCRYPT_NO_MITM,
        max_length=1,
        fixed_length=True,
    )

    protocol_mode = Uint8Characteristic(
        uuid=StandardUUID(0x2A4E),
        properties=(Characteristic.READ | Characteristic.WRITE_NO_RESPONSE),
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        initial_value=1,
        max_value=1,
    )
    """Protocol mode: boot (0) or report (1)"""

    # bcdHID (version), bCountryCode (0 not localized), Flags: RemoteWake, NormallyConnectable
    # bcd1.1, country = 0, flag = normal connect
    # TODO: Make this a struct.
    hid_information = Characteristic(
        uuid=StandardUUID(0x2A4A),
        properties=Characteristic.READ,
        read_perm=Attribute.ENCRYPT_NO_MITM,
        write_perm=Attribute.NO_ACCESS,
        initial_value=b"\x01\x01\x00\x02",
    )
    """Hid information including version, country code and flags."""

    report_map = Characteristic(
        uuid=StandardUUID(0x2A4B),
        properties=Characteristic.READ,
        read_perm=Attribute.ENCRYPT_NO_MITM,
        write_perm=Attribute.NO_ACCESS,
        fixed_length=True,
    )
    """This is the USB HID descriptor (not to be confused with a BLE Descriptor). It describes
       which report characteristic are what."""

    suspended = Uint8Characteristic(
        uuid=StandardUUID(0x2A4C),
        properties=Characteristic.WRITE_NO_RESPONSE,
        read_perm=Attribute.NO_ACCESS,
        write_perm=Attribute.ENCRYPT_NO_MITM,
        max_value=1,
    )
    """Controls whether the device should be suspended (0) or not (1)."""

    def __init__(self, hid_descriptor=DEFAULT_HID_DESCRIPTOR, service=None):
        super().__init__(report_map=hid_descriptor)
        if service:
            # TODO: Add support for connecting to a remote hid server.
            pass
        self._init_devices()

    def _init_devices(self):
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self.devices = []
        hid_descriptor = self.report_map

        global_table = [None] * 10
        local_table = [None] * 3
        collections = []
        top_level_collections = []

        i = 0
        while i < len(hid_descriptor):
            b = hid_descriptor[i]
            tag = (b & 0xF0) >> 4
            _type = (b & 0b1100) >> 2
            size = b & 0b11
            size = 4 if size == 3 else size
            i += 1
            data = hid_descriptor[i : i + size]
            if _type == _ITEM_TYPE_GLOBAL:
                global_table[tag] = data
            elif _type == _ITEM_TYPE_MAIN:
                if tag == _MAIN_ITEM_TAG_START_COLLECTION:
                    collections.append(
                        {
                            "type": data,
                            "locals": list(local_table),
                            "globals": list(global_table),
                            "mains": [],
                        }
                    )
                elif tag == _MAIN_ITEM_TAG_END_COLLECTION:
                    collection = collections.pop()
                    # This is a top level collection if the collections list is now empty.
                    if not collections:
                        top_level_collections.append(collection)
                    else:
                        collections[-1]["mains"].append(collection)
                elif tag == _MAIN_ITEM_TAG_INPUT:
                    collections[-1]["mains"].append(
                        {
                            "tag": "input",
                            "locals": list(local_table),
                            "globals": list(global_table),
                        }
                    )
                elif tag == _MAIN_ITEM_TAG_OUTPUT:
                    collections[-1]["mains"].append(
                        {
                            "tag": "output",
                            "locals": list(local_table),
                            "globals": list(global_table),
                        }
                    )
                else:
                    raise RuntimeError("Unsupported main item in HID descriptor")
                local_table = [None] * 3
            else:
                local_table[tag] = data

            i += size

        def get_report_info(collection, reports):
            """ Gets info about hid reports """
            for main in collection["mains"]:
                if "type" in main:
                    get_report_info(main, reports)
                else:
                    report_size, report_id, report_count = [
                        x[0] for x in main["globals"][7:10]
                    ]
                    if report_id not in reports:
                        reports[report_id] = {"input_size": 0, "output_size": 0}
                    if main["tag"] == "input":
                        reports[report_id]["input_size"] += report_size * report_count
                    elif main["tag"] == "output":
                        reports[report_id]["output_size"] += report_size * report_count

        for collection in top_level_collections:
            if collection["type"][0] != 1:
                raise NotImplementedError(
                    "Only Application top level collections supported."
                )
            usage_page = collection["globals"][0][0]
            usage = collection["locals"][0][0]
            reports = {}
            get_report_info(collection, reports)
            if len(reports) > 1:
                raise NotImplementedError(
                    "Only one report id per Application collection supported"
                )

            report_id, report = list(reports.items())[0]
            output_size = report["output_size"]
            if output_size > 0:
                self.devices.append(
                    ReportOut(
                        self, report_id, usage_page, usage, max_length=output_size // 8
                    )
                )

            input_size = reports[report_id]["input_size"]
            if input_size > 0:
                self.devices.append(
                    ReportIn(
                        self, report_id, usage_page, usage, max_length=input_size // 8
                    )
                )
