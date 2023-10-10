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
import time
from py.Config import Config
from Helpers import *

# ===
# Stores the current, min and max values for a given sensor
#
class Sensor():
	def __init__(self, name):
		self.name = name
		self.curtime = None
		self.curval = None
		self.minval = None
		self.maxval = None
		return

	# Update the stored sensor values from a temporary Sensor object
	#
	def Update(self, new):
		if self.curtime == None or self.curtime < new.curtime:
			self.curtime = new.curtime
			self.curval = new.curval
		if new.minval != None:
			if self.minval == None or self.minval > new.minval:
				self.minval = new.minval
		if new.maxval != None:
			if self.maxval == None or self.maxval < new.maxval:
				self.maxval = new.maxval
		return


# ===
# Stores the current, min and max values for all sensors for a given period
#
class Statistics():
	def __init__(self, per, td):
		self.period = per		# h (hourly)		d (daily)		m (monthly)
		self.timedate = td		# YYYY-MM-DD HH		YYYY-MM-DD		YYYY-MM
		self.sensors = {}
		for s in Config.sensornames:
			self.sensors[s] = Sensor(s)
		return

	# Find and update a stored sensor from a temporary sensor object
	#
	def Update(self, sensor):
		for s in self.sensors:
			if s == sensor.name:
				self.sensors[s].Update(sensor)
				return

	# Print a line of current values
	#
	def PrintHeaders(self):
		if self.period == 'h':
			line = '%16s' % ('Date/time')
		elif self.period == 'd':
			line = '%16s' % ('Date')
		elif self.period == 'm':
			line = '%16s' % ('Month')
		else:
			line = '%16s' % ('???')
			
		for s in self.sensors:
			sensor = self.sensors[s]
			line += '  %-15s' % (Config.sensornames[sensor.name])
		print(line)
		return

	# Print a line of current values
	#
	def PrintCurrent(self):
		line = '%16s' % ( self.timedate )
		for s in self.sensors:
			sensor = self.sensors[s]
			if sensor.curval == None:
				curval = '---'
			else:
				curval = '%d.%d' % (sensor.curval//10, sensor.curval%10)
			line += '  %-15s' % (curval)
		print(line)
		return

	# Print a line of min/max values
	#
	def PrintMinMax(self):
		line = '%16s' % ( self.timedate )
		for s in self.sensors:
			sensor = self.sensors[s]
			if sensor.minval == None:
				minval = '---'
			else:
				minval = '%d.%d' % (sensor.minval//10, sensor.minval%10)
			if sensor.maxval == None:
				maxval = '---'
			else:
				maxval = '%d.%d' % (sensor.maxval//10, sensor.maxval%10)
			tmp = '%s .. %s' % (minval, maxval)
			line += '  %-15s' % (tmp)
		print(line)
		return


# ===
# Stores the sensor values for all periods.
# Reads and analyses the log files and stores the sensor values
#
class Analyser():

	def __init__(self):
		self.diagnostics = []
		self.hourly = []		# Hourly statistics for now + past 24 hours
		self.daily = []			# Daily statistics for today + past 7 days
		self.monthly = []		# Monthly statistics for this month + last 12 months
		self.now = time.time()

		# Populate the stats arrays
		t = self.now
		for i in range(0,25):		# Current hour + previous 24 hours
			gmt = time.gmtime(t)
			tstr = '%04d-%02d-%02d %02d' % (gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour)
			s = Statistics('h', tstr)
			self.hourly.append(s)
			t -= 60*60

		t = self.now
		for i in range(0,8):		# Current day + previous 7 days
			gmt = time.gmtime(t)
			tstr = '%04d-%02d-%02d' % (gmt.tm_year, gmt.tm_mon, gmt.tm_mday)
			s = Statistics('d', tstr)
			self.daily.append(s)
			t -= 60*60*24

		gmt = time.gmtime(self.now)
		tm_mon = gmt.tm_mon
		tm_year = gmt.tm_year
		for i in range(0,13):		# Current month + previous 12 months
			tstr = '%04d-%02d' % (tm_year, tm_mon)
			s = Statistics('m', tstr)
			self.monthly.append(s)
			tm_mon -= 1
			if tm_mon < 1:
				tm_year -= 1
				tm_mon = 12
	
		return

	# Read all the log files
	#
	# To do: ignore files that are older than 13 months.
	#
	def ReadLogs(self):
		# Find list of files matching pattern dh-YYYYMMDD.log
		flist = []
		dir_obj = os.scandir()
		for dir_ent in dir_obj:
			if dir_ent.is_file():
				fname = dir_ent.name
				if len(fname) == len('dh-YYYYMMDD.log') and fname[0:3] == 'dh-' and fname[-4:] == '.log':
					flist.append(fname)
		dir_obj.close()

		# Read all the logs
		for fname in flist:
			self.ReadLog(fname)

		return

	# Read a single log file and analyse the content
	#
	def ReadLog(self, fname):
		log_file = open(fname, 'r')
		log = log_file.readlines()
		log_file.close()

		for line in log:
			self.AnalyseLine(line.strip())
		return

	# Analyse a single line of a log
	#
	def AnalyseLine(self, line):
		pairs = line.split('&')	# An array of key=value strings
		if len(pairs) < 3:
			print('Short line "' + line +'" ignored')
			return
		values = {}
		for pair in pairs:
			(key, value) = pair.split('=', 1)
			values[key] = value
		if not SanityCheck(values, False):
			return

		d = values['date']
		t = values['time']
		td = d[0:4] + '-' + d[4:6]
		monthly = self.FindStats(self.monthly, td)
		td += '-' + d[6:8]
		daily = self.FindStats(self.daily, td)
		td += ' ' + t[0:2]
		hourly = self.FindStats(self.hourly, td)
		if monthly == None and daily == None and hourly == None:
			return
		td += ':' + t[2:4] + ':' + t[4:6]
		s = Sensor(None)
		s.curtime = td
		for key in values:
			if key in ['date', 'time', 'from']:	# These aren't sensor fields; ignore them
				continue

			s.name = key
			s.minval = None
			s.maxval = None

			vals = values[key].split(',')
			s.curval = self.StrToInt(vals[0])
			if len(vals) > 1:
				s.minval = self.StrToInt(vals[1])
			if len(vals) > 2:
				s.maxval = self.StrToInt(vals[2])
			if len(vals) > 3:
				print('More than three values; remainder ignored')

			if hourly != None:
				hourly.Update(s)
			if daily != None:
				daily.Update(s)
			if monthly != None:
				monthly.Update(s)
		return

	def FindStats(self, stats, td):
		for s in stats:
			if s.timedate == td:
				return s
		return None

	def StrToInt(self, valstr):
		try:
			v = int(valstr)
		except:
			v = None
		return v

	def PrintStats(self):
		print(Config.title)
		print('All times are UTC')
		print()
		gmt = time.gmtime(self.now)
		utc = (gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, gmt.tm_min)
		print('Current time: %04d-%02d-%02d %02d:%02d' % utc)
		print()
		self.hourly[0].PrintHeaders()
		print('Current')
		self.hourly[0].PrintCurrent()
		print('Hour')
		self.hourly[0].PrintMinMax()
		print('Last 24 hours')
		for stats in self.hourly[1:]:
			stats.PrintMinMax()
		print()

		self.daily[0].PrintHeaders()
		print('Today')
		self.daily[0].PrintMinMax()
		print('Last 7 days')
		for stats in self.daily[1:]:
			stats.PrintMinMax()
		print()
		self.monthly[0].PrintHeaders()
		print('This month')
		self.monthly[0].PrintMinMax()
		print('Last 12 months')
		for stats in self.monthly[1:]:
			stats.PrintMinMax()
		print()
		return
