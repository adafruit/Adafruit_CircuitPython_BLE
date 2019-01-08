from adafruit_ble.uart import UARTService

# Starts advertising automatically. That may change in later versions.
uart = UARTService()

while True:
    # Returns one if nothing was read.
    one_byte = uart.read()
    if one_byte:
        uart.write(bytes([one_byte]))
