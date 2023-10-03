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

import time
import network
import socket
import struct
import urequests

class Network():
	# Connect to WLAN
	#
	@staticmethod
	def ConnectToWlan():
		print('Connecting to WLAN ...')
		wlan = network.WLAN(network.STA_IF)
		wlan.active(True)
		wlan.connect(Config.WLAN_SSID, Config.WLAN_PASSWD)
		while not wlan.isconnected():
			pass
		print('... Connected')
		return

	# Set the time from an NTP server
	#
	@staticmethod
	def NtpSetTime():
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

	# Post all available sensor data to the server
	# Parameter t is a time tuple (YYYY, MM, DD, hh, mm, ss)
	#
	@staticmethod
	def PostToServer(t):
		urlstr = '?'.join([Config.LOG_SERVER, Config.LOG_ID])
		datestr = 'date=%04d%02d%02d' % (t[0], t[1], t[2])
		timestr = 'time=%02d%02d%02d' % (t[3], t[4], t[5])
		response = urequests.get('&'.join([urlstr, datestr, timestr] + Sensors.GetAllValues()))
		x = response.text
		response.close()
		return x
