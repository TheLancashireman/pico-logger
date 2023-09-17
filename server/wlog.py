#!/usr/bin/python3
#
# wlog.py - weather logger, incoming data
#
# (c) 2023 David Haworth

import os
import sys
import traceback

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

# Raise a ValueError if any of the data is crap
#
maxdays = [ 29, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
def SanityCheck(params):
	v = params['date']
	ymd = DateTimeSplit(v)
	if ymd[0] < 2000:
		raise ValueError('year not plausible.')
	if ymd[1] < 1 or ymd[1] > 12:
		raise ValueError('month not plausible.')
	maxindex = ymd[1]
	if ( ((ymd[0] % 4) == 0) and ((ymd[0] % 100) != 0) ) or ((ymd[0] % 400) == 0):
		maxindex = 0	# Divides by 4 but not by 100 ==> leap year
	if ymd[2] < 1 or ymd[2] > maxdays[maxindex]:
		raise ValueError('day of month not plausible.')

	v = params['time']
	ymd = DateTimeSplit(v)
	if ymd[0] < 0 or ymd[0] > 23:
		print('Hour:', ymd[0])
		raise ValueError('hour not plausible.')
	if ymd[1] < 0 or ymd[1] > 59:
		raise ValueError('minute not plausible.')
	if ymd[2] < 0 or ymd[2] > 59:
		raise ValueError('second not plausible.')

	return True

# Process the incoming query
# Split up the query string into key,value pairs and perform some simple sanity checks
# If the checks are OK, write the querty string to the log file
#
def ProcessQuery(q):
	pairs = q.split('&')	# An array of key=value strings

	if len(pairs) < 3:
		print('Error! QUERY_STRING contains fewer than three parameters')
		return False

	params = {}

	for kv in pairs:
		k_v = kv.split('=', 1)	# Might be an = in the value (unlikely)
		if len(k_v) != 2:
			print('Error! parameter "'+kv+' has no value')
			return False
		params[k_v[0]] = k_v[1]

	if SanityCheck(params):
		f = open('log-'+params['date']+'.log', 'a')
		f.write(q+'\n')
		f.close()

	return True

# Logger main function.
# Separate function so that it's easy to trap and report exceptions
#
def Logger():
	q = os.environ.get('QUERY_STRING')
	if q == None:
		print('Error! QUERY_STRING not set')
		return
#	print('QUERY_STRING =', q)	# Debug

	if len(q) < len('date=20230916&time=222900&x=y'):	# Minimal log data
		print('Error! QUERY_STRING too short')
		return

	if len(q) > 256:									# Should be enough for anyone ;-)
		print('Error! QUERY_STRING too long')
		return

	if ProcessQuery(q):
		print('OK')
	else:
		print('QUERY_STRING =', q)
	return

# Do the job ...
#
print('Content-type: text/plain')
print('')

try:
	Logger()
except:
	exc = sys.exception()
	fexc = traceback.format_exception(exc)
	print('QUERY_STRING', os.environ.get('QUERY_STRING'))
	for l in fexc:
		print(l)
	print('')

exit(0)
