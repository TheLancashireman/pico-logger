# Pico logger

This is the firmware for a data logger using a Raspberry Pico-W.

The design uses various local sensors as well as remote sensors communicating over serial
lines, RF etc. to gather information. The data will be stored locally and sent to
a remote server.

Possible sensors:

* Temperature
* Humidity
* Wind speed
* Rainfall
* Radiation
* ... depending on what I can find.

## Hardware

The base station uses a Raspberry Pi Pico-W board.

The remote sensors will use various AVR devices - mostly ATtiny. The firmware for
these can be found in separate repositories.

## Design (short version)

* On-board LED is used as an alive indicator. Blinks for 20 ms every 10s normally - extended during network access.
* USB is the console - used for communicating with PC.
* One UART is used for receiving messages from the serial remote sensors.
* Wifi for connecting to the internet:
** NTP time synchronisation
** Post data to a server using an https GET request

One of the challenges is that the internet communication (especially the https GET request)
takes a *long* time. For http, it takes up to 1 second; https can take up to 10 seconds.
During that time nothing else happens. There's an asynchronous version of urequests, but
in the source code there's a warning that setting up the SSL blocks for a long time,
so the async version won't be much help.

For the initial version, everything runs on core 0 and the several seconds of inactivity
during server posts will have to be accepted. Some data might be lost, but it probably isn't
important.

Some experiments using both cores have been performed; see notes at end of this page.

## CAVEAT: This project is in the early development stages.
If you're looking for a ready-to-run project please look elsewhere.

## License

GPL v3 or later.  See the LICENSE file

## Experimental notes

These dual-core experiments were performed in small test programs.

First attempt: do the server posts in a thread on core 1:
* Connect to WLAN on core 0 at startup
* Start a thread on core 1 from the timing loop on core 0 whenever it's time to send. URL calculated on
core 0 and passed as a parameter.
* Result: thread starts and prints URL, but network request times out.

Second attempt: do all networking in threads on core 1:
* Connect to WLAN in core 1 thread fails. Didn't get as far as sending to server

Third attempt: do all networking on core 0 and sensor monitoring on core 1
* Seems to work with dummy sensor code
* Next step: find out if other Pico hardware can be used from core 1:
** ADC - seems to work
** SPI
** UART
Unsure if mutual exclusion is needed while updating variables (core 1) and reading variables (core 0).
Not even sure if the micropython threads are truly concurrent. Information from the internet is
conflicting.
