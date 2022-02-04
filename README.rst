Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ble/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/ble/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_ble/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_ble/actions
    :alt: Build Status

This module provides higher-level BLE (Bluetooth Low Energy) functionality,
building on the native `_bleio` module.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

Warning: Linux support is **very** limited. See `Adafruit Blinka _bleio
<https://github.com/adafruit/Adafruit_Blinka_bleio>`_ for details.

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-ble/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-ble

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-ble

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-ble

Usage Example
=============

.. code-block:: python

    from adafruit_ble import BLERadio

    radio = BLERadio()
    print("scanning")
    found = set()
    for entry in radio.start_scan(timeout=60, minimum_rssi=-80):
        addr = entry.address
        if addr not in found:
            print(entry)
        found.add(addr)

    print("scan done")


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/ble/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_ble/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
