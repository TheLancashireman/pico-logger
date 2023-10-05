# Server for Pico logger

This is the server-side scripting for the logger.

* wlog.py - accepts http/https GET requests with parameters and stores the parameters.
* weather.py - analyses the stored data and produces web pages of stats etc. Currently a dummy.
* index.html - a page that is displayed if the request URL is only the directory. Currently a dummy.

## wlog.py

wlog.py has some basic sanity checking:

* There is a limit to the total length of the query string.
* A date parameter with a more-or-less valid date is required.
* A time parameter with a more-or-less valid time is required.
* (Future) username and password fields may be required.

The entire query string is stored appended to a plain text file. The name of the file contains
the date and time and (future) the username.

The response to the GET command is a text/plain file. If the data gets logged, the file just contains
OK. If an error is detected (invalid or missing date, time, username, password, ...) the response
contains the error message (to do: also the query string). If a Python exception is trapped, the response
contains the query string and the traceback.
