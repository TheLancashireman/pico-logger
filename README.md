# Weather station

This is the firmware for a weather station. The design uses various remote sensors communicating
over serial lines, RF etc. to gather information.

The plan is to log the data to flash memory (SD card, etc.) and dump it to a PC for offline
analysis.

Possible sensors:

* Temperature
* Humidity
* Wind speed
* Rainfall
* Radiation
* ... depending on what I can find.

## Hardware

The base station uses a Raspberry Pi Pico-W board.

The remote sensors will use various AVR devices - mostly ATtiny.

The remote sensors are in separate repositories.

## Additional software

## Design (short version)

* On-board LED is used as an alive indicator. Blinks for 20 ms every 2s.
* USB is the console - used for communicating with PC.
* Uart1 is used for receiving messages from the serial remote sensors.

## CAVEAT: This project is under development. If you're looking for a ready-to-run project please look elsewhere.

## License

GPL v3 or later.  See the LICENSE file
