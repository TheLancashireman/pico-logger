#!/usr/bin/python3
#
# wlog.py - weather logger, incoming data
#
# (c) David Haworth

import os
import sys
import traceback
from Config import Config

# Input is a string containing a compressed date or time, e.g. YYYYMMDD or hhmmss
# Output is [YYYY, MM, DD] or [hh, mm, ss] (all as integers)
#
def DateTimeSplit(dt):
	x = int(dt)
	dt = [0, 0, 0]
	dt[2] = int(x % 100)
	x = int(x / 100)
	dt[1] = int(x % 100)
	x = int(x / 100)
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
def SanityCheck(params):
	try:
		v = params['date']
	except:
		return Error('date parameter not present.')

	ymd = DateTimeSplit(v)
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

	ymd = DateTimeSplit(v)
	if ymd[0] < 0 or ymd[0] > 23:
		return Error('hour not plausible.')
	if ymd[1] < 0 or ymd[1] > 59:
		return Error('minute not plausible.')
	if ymd[2] < 0 or ymd[2] > 59:
		return Error('second not plausible.')

	try:
		u = params['user']
		p = params['pass']
		if Config.passwords[u] != p:
			return Error('username/password mismatch.')
	except:
		return Error('username/password mismatch.')

	return True

# Process the incoming query
# Split up the query string into key,value pairs and perform some simple sanity checks
# If the checks are OK, write the querty string to the log file
#
def ProcessQuery(q):
	pairs = q.split('&')	# An array of key=value strings

	if len(pairs) < 5:
		return Error('QUERY_STRING contains fewer than five parameters.')

	params = {}

	for kv in pairs:
		k_v = kv.split('=', 1)	# Might be an = in the value (unlikely)
		if len(k_v) != 2:
			return Error('parameter "'+kv+' has no value.')
		params[k_v[0]] = k_v[1]

	if SanityCheck(params):
		# Ensure date and time are at the beginning of the line
		parts = [ 'date=' + params['date'], 'time=' + params['time'] ]
		# Append all parameters except date, time, user and pass
		for v in params:
			if v not in [ 'date', 'time', 'user', 'pass' ]:
				parts.append( v + '=' + params[v] )
		# Open the file and write the parts joined with '&'
		fname = params['user'] + '-' + params['date'] + '.log'
		f = open(fname, 'a')
		line = '&'.join(parts)
		f.write(line+'\n')
		f.close()

	return True

# Logger main function.
# Separate function so that it's easy to trap and report exceptions
#
def Logger():
	q = os.environ.get('QUERY_STRING')
	if q == None:
		return Error('QUERY_STRING not set')

	if len(q) < len('date=20230916&time=222900&x=y'):	# Minimal log data
		return Error('QUERY_STRING too short')

	if len(q) > 1000:									# Should be enough for anyone ;-)
		return Error('QUERY_STRING too long')

	if not ProcessQuery(q):
		print('QUERY_STRING = ' + q)
		return False

	return True

# Do the job ...
#
print('Content-type: text/plain')
print('')

try:
	if Logger():
		print('OK')
except:
	print('Sorry; an exception occurred.')
	print('QUERY_STRING', os.environ.get('QUERY_STRING'))

	# For some reason, getting the exception type on my web host fails silently.
	# This is for local debugging
	exc = sys.exception()
	fexc = traceback.format_exception(exc)
	for l in fexc:
		print(l.rstrip())
	print('')

exit(0)
