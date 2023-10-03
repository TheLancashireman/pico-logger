#!/bin/sh
#
# This script is used for development to avoid having to maintain and update files on the
# pico's internal filesystem.
# It concatenates all parts together and upload to the pico.

# First concatenate all the python files (with blank lines between them) and remove all imports.
#
cat	Config.py      Blank.txt \
	Network.py     Blank.txt \
	Sensors.py     Blank.txt \
	PicoLogger.py  Blank.txt \
	main.py        Blank.txt | egrep -v '^import|^from' > tmprun1.py

# Prepend global imports
#
cat AllImports.txt Blank.txt tmprun1.py > tmprun.py
rm tmprun1.py

# Run the resulting program
#
mpremote run tmprun.py
