#!/usr/bin/python3
#
# weather.py - weather logger
#
# (c) 2023 David Haworth

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
