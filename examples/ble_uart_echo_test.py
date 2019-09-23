import adafruit_ble

from adafruit_ble import SmartAdapter
from adafruit_ble.advertising.standard import ProvideServiceAdvertisement
from adafruit_ble.services.nordic import UARTService

# This should work.

adapter = SmartAdapter()
uart = UARTService()
advertisement = ProvideServiceAdvertisement(uart)

while True:
    adapter.start_advertising(advertisement)
    while not adapter.connected:
        pass
    while adapter.connected:
        # Returns b'' if nothing was read.
        one_byte = uart.read(1)
        if one_byte:
            print(one_byte)
            uart.write(one_byte)
