# CircuitPython Bluefruit LE Connect Plotter Example

import board
import analogio
import adafruit_thermistor
from adafruit_ble.uart_server import UARTServer

uart_server = UARTServer()

thermistor = adafruit_thermistor.Thermistor(board.TEMPERATURE, 10000, 10000, 25, 3950)
light = analogio.AnalogIn(board.LIGHT)


def scale(value):
    """Scale the light sensor values from 0-65535 (AnalogIn range)
    to 0-50 (arbitrarily chosen to plot well with temperature)"""
    return value / 65535 * 50


while True:
    # Advertise when not connected.
    uart_server.start_advertising()
    while not uart_server.connected:
        pass

    while uart_server.connected:
        print(scale(light.value), thermistor.temperature)
        uart_server.write('{},{}\n'.format(scale(light.value), thermistor.temperature))
