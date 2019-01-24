from adafruit_ble.uart import UARTServer

uart = UARTServer()
uart.start_advertising()

# Wait for a connection
while not uart.connected:
    pass

# When the client disconnects, the program will exit.
while uart.connected:
    # Returns b'' if nothing was read.
    one_byte = uart.read(1)
    if one_byte:
        uart.write(one_byte)
