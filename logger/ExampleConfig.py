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

# Schedule configuration for tasks
#
# The basic unit of time for the main loop is 20 ms. If the total execution time for the tasks
# in a single iteration exceeds 20 ms, then subsequent loop iterations run late but are shortened
# until the loop is synchronised once more with the 20 ms tick.
#
# Each task has a period and an offset, defined by PER_<task> and OFF_<task>. Activity in a task is
# determined by a decision of the form "if (counter % PER) == OFF:"
#
# The main loop calls all task functions in turn and then sleeps for a computed time (which may be 0). Each
# task function decides, based on its period and offset, whether to do anything on each call.
#
# The first task function to be called is the LED blink task. This task has a period of 10 seconds and
# turns the LED ON at offset 0 and OFF again at offset 1.
# This means that any other task that has offset 0 could extend the ON time of the LED. This fact is used to
# indicate network activity.

	PER_LED		= 500		# 10 secs
	OFF_LED_ON	= 0			# LED ON at 0
	OFF_LED_OFF	= 1			# LED OFF at 1 (nominally 20 ms after LED_ON)

# The configuration above gives a system repetition time of 10 seconds. The periods and
# offsets of the remaining tasks are chosen to fit into this repetition cycle.
# For example, a task with a period of 30 seconds (3 cycles, 1500 ticks) would run in at the start
# of the 3rd cycle of its period by having an offset of 1000 or 1001. 1000 would mean that the task
# runs after the LED ON task, so might extend the ON period. 1001 means that the task runs after the
# LED OFF event, so wouldn't affect the LED blink unless its execution time is very long.

# NTP time requests happen at the start of every hour. Its execution time extends the LED ON time.
	PER_NTP		= 180000	# 60 mins
	OFF_NTP		= 0			# Start of the hour, during the LED ON period

# Server requests happen every 5 minutes, at the beginning of the final 10 second cycle of the minute,
# so that the request extends the LED blink
	PER_POST	= 15000
	OFF_POST	= 14500

# Read the internal temperatature sensor (T_pico) every minute in cycle 1 after LED OFF
	PER_TPICO	= 3000
	OFF_TPICO	= 501

# Print the status every minute in the second last cycle of the minute, after LED OFF
	PER_PRINT	= 3000
	OFF_PRINT	= 2001
