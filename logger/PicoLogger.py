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

from machine import ADC, Pin, Timer, UART
import time
import micropython

class PicoLogger():
	# The constructor connects to the network, gets the time and configures the hardware
	#
	def __init__(self):
		self.tzoffset = 7200
		while True:
			try:
				Network.ConnectToWlan()
				break
			except:
				exc = sys.exception()
				fexc = traceback.format_exception(exc)
				for l in fexc:
					print(l.rstrip())
				print('')
				time.sleep(20)
				print('Retrying')
				
		while True:
			try:
				Network.NtpSetTime()
				break
			except:
				exc = sys.exception()
				fexc = traceback.format_exception(exc)
				for l in fexc:
					print(l.rstrip())
				print('')
				time.sleep(20)
				print('Retrying')

		self.led = Pin("LED", Pin.OUT)
		self.led.off()
		self.time_counter = 0
		self.uart =  UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=None, rx=Pin(17))
		self.uart_data = bytes()
		return

	# The main loop. One iteration lasts on average 20 ms. If less, a delay is introduced. If more,
	# then there is no delay, and the timing of subsequent loops is adjusted to compensate.
	# A counter is maintained. The counter wraps around every hour. Task timing can use this counter
	# with a modulo operation.
	#
	# SerialDataTask() runs every iteration, but after the LED on/off tasks
	#
	def MainLoop(self):
		then = time.ticks_ms()
		while True:
			if (self.time_counter % Config.PER_LED) == Config.OFF_LED_ON:
				self.led.on()
			if (self.time_counter % Config.PER_LED) == Config.OFF_LED_OFF:
				self.led.off()
			self.SerialDataTask()
			if (self.time_counter % Config.PER_NTP) == Config.OFF_NTP:
				self.NtpTask()
			if (self.time_counter % Config.PER_TPICO) == Config.OFF_TPICO:
				self.InternalTemperatureTask()
			if (self.time_counter % Config.PER_PRINT) == Config.OFF_PRINT:
				self.PrintTask()
				self.LogTask()		# Testing
			if (self.time_counter % Config.PER_POST) == Config.OFF_POST:
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

	# Set the time from an NTP server.
	#
	def NtpTask(self):
		print('NtpTask')
		try:
			Network.NtpSetTime()
		except:
			PicoLogger.PrintTrace()
		return

	# Print the status
	#
	def PrintTask(self):
		print('PrintTask')
		t = time.localtime(time.time()+self.tzoffset)
		print( '%04d-%02d-%02d %02d:%02d:%02d' % (t[0], t[1], t[2], t[3], t[4], t[5]))
		temp = Sensors.GetValue('T_pico', 9999)
		print('Pico temperature:', PicoLogger.TenthsToStr(temp), 'C')
		temp = Sensors.GetValue('T01', 9999)
		print('Indoor temperature:', PicoLogger.TenthsToStr(temp), 'C')
		micropython.mem_info()
		return

	# Read the internal temperature
	#
	def InternalTemperatureTask(self):
		print('InternalTemperatureTask')
		Sensors.LogMinMaxValue('T_pico', Sensors.ReadInternalTemperature())
		return

	# Read and process data from the serial sensors
	#
	def SerialDataTask(self):
#		print('SerialDataTask')
		while self.uart.any() > 0:
			c = self.uart.read(1)
			if c == b'\r' or c == b'\n':
				Sensors.ProcessSerialData(self.uart_data.decode('ascii'))
				self.uart_data = bytes()
			else:
				self.uart_data += c
		return

	# Post the status to the remote server
	#
	def LogTask(self):
		print('LogTask')
		try:
			t = time.localtime(time.time()+self.tzoffset)
			ans = Network.PostToServer(t)
			if ans.strip() != 'OK':
				print('Server responss:')
				print(ans)
		except:
			PicoLogger.PrintTrace()
		return

	# Convert a value in "tenths" to a string
	#
	@staticmethod
	def TenthsToStr(value):
		if value < 0:
			s = '-'
			value = -value
		else:
			s = ''
		vi = value//10
		vd = value%10
		return '%s%d.%d' % (s, vi, vd)

	# Print an exception stack trace
	#
	@staticmethod
	def PrintTrace():
		exc = sys.exception()
		fexc = traceback.format_exception(exc)
		for l in fexc:
			print(l.rstrip())
		print('')
