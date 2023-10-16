#!/bin/sh
#
# This Make copies all the necessary files to the Pico's internal filesystem.
#
# It uses a mirror to determine which files to copy

MIRRORS += mirror/Config.py
MIRRORS += mirror/Network.py
MIRRORS += mirror/Sensors.py
MIRRORS += mirror/PicoLogger.py
MIRRORS += mirror/main.py

.PHONY:	default test install

default:
	@echo "make test     : combines python files and sends to Pico on stdin"
	@echo "make install  : installs/updates python files on Pico internal filesystem"

test:
	./run.sh

install:	$(MIRRORS)
	mpremote ls :

mirror/%:	%
	mpremote cp $* :
	mkdir -p mirror
	touch $@

