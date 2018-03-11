from http.server import HTTPServer
from socketserver import ThreadingMixIn

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    request_queue_size = 1000
    timeout = 60

