from http.server import BaseHTTPRequestHandler as RequestProcessor, HTTPStatus
import socket
from urllib.parse import urlparse

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class BaseRequestProcessor(RequestProcessor):
    supported_methods = ['get', 'post', 'put', 'delete', 'head', 'update', 'options']

    def __init__(self, request, client_address, server):
        self.raw_requestline = None
        self.requestline = ''
        self.request_version = ''
        self.command = ''
        self.close_connection = True
        self.user = object()
        self.initialize()
        super(BaseRequestProcessor, self).__init__(request, client_address, server)

    def initialize(self):
        pass

    def after_response(self):
        pass

    def get_request_handler(self, url):
        """
        Pass here a full url and get a corresponding RequestDispatcher class
        :param url: str url
        """
        url = urlparse(url)
        return self.server.dispatcher.handler(url.path)

    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            # here we have self.headers, self.command and self.path
            mname = self.command.lower()
            request_handler_cls = self.get_request_handler(self.path)
            if not request_handler_cls:
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "Url (%r) not found" % self.path)
                return
            if not hasattr(request_handler_cls, mname) or mname not in request_handler_cls.supported_methods:
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                return
            request_handler = request_handler_cls(self)
            method = getattr(request_handler, mname)
            # check authorization hook
            if not request_handler.authorize():
                self.send_error(
                    HTTPStatus.UNAUTHORIZED,
                    "Not authorized")
                return
            method()
            # after response has been sent BaseRequestHandler method
            request_handler.after_response()
            self.wfile.flush()  # actually send the response if not already done.
        except socket.timeout as e:
            # a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return
        finally:
            # after response has been sent BaseRequestProcessor method
            self.after_response()


class BaseRequestHandler:
    supported_methods = ['get', 'post', 'put', 'delete', 'head', 'update', 'options']

    def __init__(self, request_processor):
        self.rp = request_processor
        self.initialize()

    def initialize(self):
        pass

    def authorize(self) -> bool:
        return True

    def after_response(self):
        pass

    def write(self, msg, encode=True):
        if encode:
            msg = msg.encode('utf-8')
        self.rp.wfile.write(msg)

    def write_error(self, code, message=None, explain=None):
        self.rp.send_error(self, code, message, explain)

    def add_header(self, header, value):
        if not hasattr(self.rp, '_headers_buffer'):
            self.rp._headers_buffer = []
        self.rp._headers_buffer.append(
            ("%s: %s\r\n" % (header, value)).encode('latin-1', 'strict')
        )

    # def set_response_code(self, code):

    def get(self):
        raise NotImplementedError('You should implement `GET` method')

    def post(self):
        raise NotImplementedError('You should implement `POST` method')

    def put(self):
        raise NotImplementedError('You should implement `PUT` method')

    def delete(self):
        raise NotImplementedError('You should implement `DELETE` method')

    def head(self):
        raise NotImplementedError('You should implement `HEAD` method')

    def update(self):
        raise NotImplementedError('You should implement `UPDATE` method')

    def options(self):
        raise NotImplementedError('You should implement `OPTIONS` method')
