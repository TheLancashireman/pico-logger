#!/usr/bin/python3
#
# (c) David Haworth
#
# This file is part of pico-logger.
#
# pico-logger is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pico-logger is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pico-logger.  If not, see <http://www.gnu.org/licenses/>.

# Example configuration file for wlog etc.
# Copy this file to a subdirectory called py. Rename it to Config.py.
# Add access protection to py/ using .htaccess
# Edit the file to suit.

class Config():
	title = 'Weather report'
	# Username/password pairs
	passwords = {
		'me':	'1234',
		'you':	'9876'
	}
	sensornames = {
		'T00':		'Outdoors',
		'T01':		'Indoors'
	}
