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

from machine import ADC, Pin, Timer
import time
import network
import socket
import struct

class PicoLogger():
	# The constructor connects to the network, gets the time and configures the hardware
	#
	def __init__(self):
		self.ConnectToWlan(Config.WLAN_SSID, Config.WLAN_PASSWD)
		self.SetTime()
		self.led = Pin("LED", Pin.OUT)
		self.led.off()
		self.time_counter = 0
		self.sensor = {}
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

	# Blink the LED. On for 20ms (one iteration) per 5 secs (250 iterations
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
			self.SetTime()
		return

	# Print the status every minute at 3 seconds offset
	#
	def PrintTask(self):
		if (self.time_counter % 3000) == 150:
			t = time.localtime(time.time()+7200)
			temp = self.GetSensor('T_int', 9999)
			print('%04d-%02d-%02d %02d:%02d:%02d %d.%d C' % (t[0], t[1], t[2], t[3], t[4], t[5], temp//10, temp%10))
		return

	# Read the internal temperature every minute at 2 seconds offset
	#
	def InternalTemperatureTask(self):
		if (self.time_counter % 3000) == 100:
			self.sensor['T_int'] = self.ReadInternalTemperature()
		return

	# Get a sensor value, or the given default if no value recorded yet
	#
	def GetSensor(self, sensor, dflt):
		try:
			return self.sensor[sensor]
		except:
			pass
		return dflt

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
	def ReadInternalTemperature(self):
		adc = machine.ADC(4)
		a = adc.read_u16()
		t10 = 4372 - a * 292586 // 1000000
		return t10

	# Set the time from an NTP server
	#
	def SetTime(self):
		ntp_query = bytearray(48)
		ntp_query[0] = 0x1B
		addr = socket.getaddrinfo(Config.NTP_SERVER, 123)[0][-1]
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			s.settimeout(1)
			res = s.sendto(ntp_query, addr)
			msg = s.recv(48)
		finally:
			s.close()
		val = struct.unpack("!I", msg[40:44])[0]
		t = val - Config.NTP_DELTA	
		tm = time.gmtime(t)
		machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
		return

	# Connect to WLAN
	#
	def ConnectToWlan(self, ssid, passwd):
		print('Connecting to WLAN ...')
		wlan = network.WLAN(network.STA_IF)
		wlan.active(True)
		wlan.connect(ssid, passwd)
		while not wlan.isconnected():
			pass
		print('... Connected')
		return
