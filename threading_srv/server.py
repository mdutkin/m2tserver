import socketserver
import socket
import re
from socketserver import ThreadingMixIn
from threading_srv.base_http_handler import BaseRequestProcessor

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class ThreadedHTTPServer(ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in a separate thread."""

    request_queue_size = 1000
    timeout = 60
    allow_reuse_address = 1  # Seems to make sense in testing environment

    def __init__(self, listen_ip, listen_port, dispatcher, request_handler_class, bind_and_activate=True):
        self.dispatcher = dispatcher
        self.request_handler_class = request_handler_class
        # I pass here and `object` cause I know where it's used - only in finish_request method.
        # and actually, I use there my own dispatcher, so there's no need in `RequestHandlerClass`
        super(ThreadedHTTPServer, self).\
            __init__((listen_ip, listen_port), request_handler_class, bind_and_activate)

    def finish_request(self, request, client_address):
        """
        Finish one request by instantiating RequestHandlerClass.
        This method goes to separate thread
        """
        self.request_handler_class(request, client_address, self)

    def server_bind(self):
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

    def service_actions(self):
        # print('something in a loop')
        pass


class UrlDispatcher:
    def __init__(self, dispatcher_rules):
        self.dispatcher_rules = {k: {
            'rgx': re.compile(k, re.MULTILINE | re.IGNORECASE),
            'pattern': k,
            'cls': v
        } for k, v in dispatcher_rules.items()}

    def handler(self, url):
        for k, v in self.dispatcher_rules.items():
            if v['rgx'].match(url):
                return v['cls']
        return None


class Core:
    def __init__(self, dispatcher_rules):
        self._dispatcher_rules = dispatcher_rules
        self.server = None

    def run(self, listen_ip='127.0.0.1', listen_port=8888):
        self.server = ThreadedHTTPServer(
            listen_ip,
            listen_port,
            UrlDispatcher(self._dispatcher_rules),
            BaseRequestProcessor
        )
        self.server.serve_forever()
