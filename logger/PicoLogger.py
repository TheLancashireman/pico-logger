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
from Network import Network
from Sensors import Sensors

from machine import ADC, Pin, Timer
import time

class PicoLogger():
	# The constructor connects to the network, gets the time and configures the hardware
	#
	def __init__(self):
		self.tzoffset = 7200
		Network.ConnectToWlan()
		Network.NtpSetTime()
		self.led = Pin("LED", Pin.OUT)
		self.led.off()
		self.time_counter = 0
		return

	# The main loop. One iteration lasts on average 20 ms. If less, a delay is introduced. If more,
	# then there is no delay, and the timing of subsequent loops is adjusted to compensate.
	# A counter is maintained. The counter wraps around every hour. Task timing can use this counter
	# with a modulo operation.
	#
	def MainLoop(self):
		then = time.ticks_ms()
		while True:
			self.BlinkerTask()
			self.NtpTask()
			self.InternalTemperatureTask()
			self.PrintTask()
			self.LogTask()

			# This code should give a loop period of 20 ms regardless of how much processing is done
			# in the loop ... up to a point.
			# If one iteration takes longer than 20 ms, subsequent iterations have no delay until the
			# loop "catches up"
			now = time.ticks_ms()
			diff = time.ticks_diff(now, then)
			if diff < 20:
				time.sleep_ms(20 - diff)
			then = time.ticks_add(then, 20)
			self.time_counter += 1
			if self.time_counter >= 180000:		# 60*60*1000/20 = 1 hour
				self.time_counter = 0
		return

	# Blink the LED. On for 20ms (one iteration) per 5 secs (250 iterations)
	#
	def BlinkerTask(self):
		t = self.time_counter % 250
		if t == 0:
			self.led.on()
		elif t == 1:
			self.led.off()
		return

	# Set the time from an NTP server. Every hour at 7 seconds past
	#
	def NtpTask(self):
		if self.time_counter == 350:
			Network.NtpSetTime()
		return

	# Print the status every minute at 3 seconds offset
	#
	def PrintTask(self):
		if (self.time_counter % 3000) == 150:
			t = time.localtime(time.time()+self.tzoffset)
			temp = Sensors.GetValue('T_pico', 9999)
			if temp < 0:
				s = '-'
				temp = -temp
			else:
				s = ''
			ti = temp//10
			td = temp%10
			print('%04d-%02d-%02d %02d:%02d:%02d %s%d.%d C' % (t[0], t[1], t[2], t[3], t[4], t[5], s, ti, td))
		return

	# Read the internal temperature every minute at 2 seconds offset
	#
	def InternalTemperatureTask(self):
		if (self.time_counter % 3000) == 100:
			Sensors.LogValue('T_pico', Sensors.ReadInternalTemperature())
		return

	# Log the status every 5 minutes at 100 milliseconds offset
	#
	def LogTask(self):
		if (self.time_counter % 15000) == 5:
			t = time.localtime(time.time()+self.tzoffset)
			before = time.ticks_ms()
			ans = Network.PostToServer(t)
			print ('Execution time for PostToServer():', time.ticks_diff(time.ticks_ms(), before))
			print('Server says', ans)
		return
