"""
Demonstration of a Bluefruit BLE Central. Connects to the first BLE UART peripheral it finds.
Sends Bluefruit ColorPackets, read from three potentiometers, to the peripheral.
"""

import time

import board
from analogio import AnalogIn
import adafruit_ble
from adafruit_ble import SmartAdapter
from adafruit_ble.advertising.standard import ProvideServiceAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.color_packet import ColorPacket

def scale(value):
    """Scale an value from 0-65535 (AnalogIn range) to 0-255 (RGB range)"""
    return int(value / 65535 * 255)

adapter = SmartAdapter()
adafruit_ble.recognize_services(UARTService)

a3 = AnalogIn(board.A3)
a4 = AnalogIn(board.A4)
a5 = AnalogIn(board.A5)

uart_connection = None
# See if any existing connections are providing UARTService.
if adapter.connected:
    for conn in adapter.connections:
        if hasattr(conn, "uart"):
            uart_connection = conn
        break

while True:
    if not uart_connection:
        print("Scanning...")
        for adv in adapter.start_scan((ProvideServiceAdvertisement,), timeout=5):
            if UARTService in adv.services:
                print("found a UARTService advertisement")
                uart_connection = adapter.connect(adv)
                break
        # Stop scanning whether or not we are connected.
        adapter.stop_scan()

    while uart_connection and uart_connection.connected:
        r = scale(a3.value)
        g = scale(a4.value)
        b = scale(a5.value)

        color = (r, g, b)
        print(color)
        color_packet = ColorPacket(color)
        try:
            uart_connection.uart.write(color_packet.to_bytes())
        except OSError:
            try:
                uart_connection.disconnect()
            except:
                pass
            uart_connection = None
        time.sleep(0.3)
