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

# This is an example. You need to adapt it for your own environment.
# WARNING: don't upload your adapted version to any public server!

class Config():
	# WiFi credentials
	WLAN_SSID	= 'ExampleSsid'
	WLAN_PASSWD	= 'ExampleWifiPassword'

	# NTP information
	NTP_SERVER	= 'pool.ntp.org'
	NTP_DELTA	= 2208988800		# NTP time 0 is 1900-01-01. This constant adjusts to a unix time 0 of 1970-01-01

	# Logger server
	LOG_SERVER	= 'https://example.com/path/to/wlog.py'
	LOG_ID		= 'user=EXAMPLE&pass=SECRET&from=pico'

	# Max age (in seconds) for sensor values
	SENSOR_AGE	= 300
