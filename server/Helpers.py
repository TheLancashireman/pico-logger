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

# This is the server-side part of the logger. Incoming data is logged to a
# file with the user and date in the name

import os
import sys
import traceback
from py.Config import Config

# Input is a string containing a compressed date or time, e.g. YYYYMMDD or hhmmss
# Output is [YYYY, MM, DD] or [hh, mm, ss] (all as integers)
#
def DateTimeSplit(dt):
	x = int(dt)
	dt = [0, 0, 0]
	dt[2] = x % 100
	x = x // 100
	dt[1] = x % 100
	x = x // 100
	dt[0] = x
	return dt

# Print an error message
#
def Error(str):
	print('Error:', str)
	return False

# Report an error if any of the data is crap
#
maxdays = [ 29, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
def SanityCheck(params, check_creds=True):
	try:
		v = params['date']
	except:
		return Error('date parameter not present.')

	try:
		ymd = DateTimeSplit(v)
	except:
		return Error('invalid date.')
	if ymd[0] < 2000:
		return Error('year not plausible.')
	if ymd[1] < 1 or ymd[1] > 12:
		return Error('month not plausible.')
	maxindex = ymd[1]
	if ( ((ymd[0] % 4) == 0) and ((ymd[0] % 100) != 0) ) or ((ymd[0] % 400) == 0):
		maxindex = 0	# Divides by 4 but not by 100 ==> leap year
	if ymd[2] < 1 or ymd[2] > maxdays[maxindex]:
		return Error('day of month not plausible.')

	try:
		v = params['time']
	except:
		return Error('time parameter not present.')

	try:
		ymd = DateTimeSplit(v)
	except:
		return Error('invalid time.')
	if ymd[0] < 0 or ymd[0] > 23:
		return Error('hour not plausible.')
	if ymd[1] < 0 or ymd[1] > 59:
		return Error('minute not plausible.')
	if ymd[2] < 0 or ymd[2] > 59:
		return Error('second not plausible.')

	if check_creds:
		try:
			u = params['user']
			p = params['pass']
			if Config.passwords[u] != p:
				return Error('username/password mismatch.')
		except:
			return Error('username/password mismatch.')

	return True
