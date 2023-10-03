#!/bin/sh
#
# This script is used for development without having to maintain and update files on the
# pico's internal filesystem.
# Concatenate all parts together and upload to the pico.

cat	dhConfig.py    Blank.txt \
	PicoLogger.py  Blank.txt \
	main.py        Blank.txt | egrep -v '^import|^from' > tmprun1.py

cat AllImports.txt Blank.txt tmprun1.py > tmprun.py

mpremote run tmprun.py
