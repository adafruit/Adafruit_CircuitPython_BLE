# CircuitPython NeoPixel Color Picker Example

import board
import neopixel
from adafruit_ble.uart_server import UARTServer
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

uart_server = UARTServer()

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)

while True:
    # Advertise when not connected.
    uart_server.start_advertising()
    while not uart_server.connected:
        pass

    while uart_server.connected:
        try:
            packet = Packet.from_stream(uart_server)
        except (ValueError, OSError):
            pass
        if isinstance(packet, ColorPacket):
            print(packet.color)
            pixels.fill(packet.color)
