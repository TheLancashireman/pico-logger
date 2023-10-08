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

# This is the main program of the user interface

import os
import sys
import traceback

def AddLineToBody(body, line):
	body += line.rstrip()+'<br/>\n'
	return body

def MakeBody():
	body = ''
	body = AddLineToBody(body, 'Current directory: '+os.getcwd())
	body = AddLineToBody(body, 'Environment variables:')
	for k, v in os.environ.items():
		body = AddLineToBody(body, '&nbsp;&nbsp;&nbsp;'+k+'&nbsp;&nbsp;=&nbsp;&nbsp;'+v)
	return body

# html_head - prints the content type, doctype and the html header
def html_head(title):
	print('Content-type: text/html')
	print('')
	print('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"')
	print('    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
	print('')
	print('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">')
	print(' <head>')
	print('  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
	print('  <meta name="viewport" content="width=device-width, initial-scale=1.0" />')
	print('  <meta name="description" content="" />')
	print('  <meta name="author" content="TheLancashireman" />')
	print('  <meta name="generator" content="dhGalleryMaker" />')
	print('  <title>'+title+'</title>')
	print(' </head>')
	return

# html_body - prints the body
def html_body(header, text):
	print(' <body>')
	print('')
	print('  <div id="thumbs">')
	print('   <h1>'+header+'</h1>')
	if text != '':
		print('   <p>'+text+'</p>')

	print('  </div>')
	print('')
	print('</body>')
	print('</html>')
	return

html_head('Python3 availability test')

try:
	body = MakeBody()
	html_body('Does it work?', body)
except:
	exc = sys.exception()
	fexc = traceback.format_exception(exc)
	body = '<pre>\n'
	for l in fexc:
		body += l
	body += '</pre>\n'
	html_body('An exception occurred', body)

exit(0)
