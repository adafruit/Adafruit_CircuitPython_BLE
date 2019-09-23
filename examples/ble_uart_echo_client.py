import time

import adafruit_ble

from adafruit_ble import SmartAdapter
from adafruit_ble.advertising.standard import ProvideServiceAdvertisement
from adafruit_ble.services.nordic import UARTService

# This should work.

adapter = SmartAdapter()

adafruit_ble.recognize_services(UARTService)

connection = None
if adapter.connected:
    connection = adapter.connections[0]

while True:
    print(connection, connection.connected if connection is not None else False)
    while connection is not None and connection.connected:
        print("echo")
        connection.uart.write(b"echo")
        # Returns b'' if nothing was read.
        one_byte = connection.uart.read(4)
        if one_byte:
            print(one_byte)
        print()
        time.sleep(1)

    print("disconnected, scanning")
    for entry in adapter.start_scan((ProvideServiceAdvertisement,), timeout=1):
        if UARTService in entry.services:
            connection = adapter.connect(entry)
            break

    adapter.stop_scan()
