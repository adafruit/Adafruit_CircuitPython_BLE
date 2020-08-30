# The MIT License (MIT)
#
# Copyright (c) 2020 Dan Halbert for Adafruit Industries
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
Sets up an on-board HCI BLE adapter.
"""

import time

import board
import busio
import digitalio
import _bleio


def create_adapter_esp32_hci(
    *,
    esp_reset=board.ESP_RESET,
    esp_gpio0=board.ESP_GPIO0,
    esp_busy=board.ESP_BUSY,
    esp_cs=board.ESP_CS,
    esp_tx=board.ESP_TX,
    esp_rx=board.ESP_RX,
    reset_high=False,
    debug=False
):
    """Do ESP32-specific HCI adapter initialization."""

    reset = digitalio.DigitalInOut(esp_reset)
    reset.switch_to_output(not reset_high)

    gpio0_and_rts = digitalio.DigitalInOut(esp_gpio0)
    cts = digitalio.DigitalInOut(esp_busy)
    chip_select = digitalio.DigitalInOut(esp_cs)

    uart = busio.UART(
        esp_tx, esp_rx, baudrate=115200, timeout=0, receiver_buffer_size=512
    )

    # Boot ESP32 from SPI flash.
    gpio0_and_rts.switch_to_output(True)

    # Choose Bluetooth mode.
    chip_select.switch_to_output(False)

    # Start reset
    reset.value = reset_high
    time.sleep(0.1)

    # Release reset and wait for startup and startup message.
    reset.value = not reset_high
    time.sleep(1.0)

    startup_message = b""
    while uart.in_waiting:  # pylint: disable=no-member
        more = uart.read()
        if more:
            startup_message += more

    if not startup_message:
        raise _bleio.BluetoothError(
            "HCI adapter did not respond with a startup message"
        )

    if debug:
        try:
            print(startup_message.decode("utf-8"))
        except UnicodeError:
            raise _bleio.BluetoothError("Garbled HCI startup message") from UnicodeError

    # pylint: disable=no-member
    # pylint: disable=unexpected-keyword-arg
    return _bleio.Adapter(uart=uart, rts=gpio0_and_rts, cts=cts)


def create_adapter(debug=False):
    """Determine whether an on-board HCI adapter is available, and initialize it.
    Currently only ESP32 co-processors are supported.
    """
    # See if all the pins we need for an ESP32 HCI adapter are available.
    if all(
        pin in dir(board)
        for pin in ("ESP_RESET", "ESP_GPIO0", "ESP_BUSY", "ESP_CS", "ESP_TX", "ESP_RX")
    ):
        return create_adapter_esp32_hci(
            esp_reset=board.ESP_RESET,
            esp_gpio0=board.ESP_GPIO0,
            esp_busy=board.ESP_BUSY,
            esp_cs=board.ESP_CS,
            esp_tx=board.ESP_TX,
            esp_rx=board.ESP_RX,
            reset_high=False,
            debug=debug,
        )

    raise _bleio.BluetoothError("ESP32 HCI adapter pins not available")
