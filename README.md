# Pico logger

This repository contains the parts of a data logger suite.

The data logger itself is based on a Raspberry Pico running Micropython. Data is gathered
from various sources - local sensors, asynchronous serial input from remote sensors, RF etc.
The data will be stored locally and sent over an internet connection to a remote server.
For internet use, a Pico-W is needed.

Subdirectories:

* logger/ - the Pico/Pico-W firmware
* server/ - the server-side scripts
* host/ - download and offline storage on a host PC (to do)

See the README.md files in the individual subdirectories for further details.

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

## CAVEAT: This project is in the early development stages.
If you're looking for a ready-to-run project please look elsewhere.

## License

GPL v3 or later.  See the LICENSE file
