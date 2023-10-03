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

from Config import Config

from machine import ADC, Pin
import time

# A single sensor value along with timestamp (for age) and mean value calculation
#
class Sensor():
	def __init__(self, current):
		self.current = current
		self.timestamp = time.time()
		self.sum = current
		self.count = 1
		return

	def NewValue(self, current):
		self.current = current
		self.timestamp = time.time()
		self.sum += current
		self.count += 1
		return

	def GetCurrent(self):
		if (time.time - self.timestamp) > Config.SENSOR_AGE:
			return None
		return self.current

	def GetMean(self):
		return (self.sum + self.count//2) // self.count		# Round to nearest

	def ClearMean(self):
		self.sum = self.current
		self.count = 1
		return

# Stores and manipulates the sensor values and provides functions to read the built-in sensors
#
class Sensors():
	sensors = {}

	# Log a single measured value. Create a sensor instance if not already present
	#
	@staticmethod
	def LogValue(name, value):
		try:
			s = Sensors.sensors[name]
		except:
			s = Sensor(value)
			Sensors.sensors[name] = s
			return
		s.NewValue(value)
		return

	# Get the most recent value of a sensor
	# ToDo: handling of stale values?
	#
	@staticmethod
	def GetValue(name, dflt = None):
		try:
			s = Sensors.sensors[name]
		except:
			return dflt
		return s.current

	# Get the values of all sensors as strings
	# Returns an array of elements of the form 'name=value'
	#
	@staticmethod
	def GetAllValues():
		l = []
		for name in Sensors.sensors:
			v = Sensors.GetValue(name)
			l.append(name+'='+str(v))
		return l

	# Read the internal temperature sensor and return the value in tenths of a degree C
	#
	# From RP2040 datasheet:
	# The temperature sensor measures the Vbe voltage of a biased bipolar diode, connected to the fifth ADC channel
	# (AINSEL=4). Typically, Vbe = 0.706V at 27 degrees C, with a slope of -1.721mV per degree.
	#
	# v = a * 3.3 / 65536
	# t = 27 - (v - 0.706)/0.001721
	#
	# ==> t = 27 + 410.226612434631 - v * 581.057524694944
	# ==> t = 437.226612434631 - a * 3.3 * 581.057524694944 / 65536
	# ==> t = 437.226612434631 - a * 0.029258572868
	# Multiply by 10 to get t10 in tenths of a degree:
	# ==> t10 = 4372.26612434631 - a * 0.29258572868
	# Convert to integer arithmetic:
	# ==> t10 = 4372 - a * 292586 / 1000000
	#
	@staticmethod
	def ReadInternalTemperature():
		adc = machine.ADC(4)
		a = adc.read_u16()
		t10 = 4372 - a * 292586 // 1000000
		return t10
