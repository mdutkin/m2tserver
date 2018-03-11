from http.server import BaseHTTPRequestHandler, HTTPStatus
import socket

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class BaseHandler(BaseHTTPRequestHandler):
    supported_methods = ['get', 'post', 'put', 'delete', 'head', 'update', 'options']

    def __init__(self, request, client_address, server):
        self.raw_requestline = None
        self.requestline = ''
        self.request_version = ''
        self.command = ''
        self.close_connection = True
        self.user = object()
        self.initialize()
        super(BaseHandler, self).__init__(request, client_address, server)

    def initialize(self):
        pass

    def authorize(self) -> bool:
        self.user = {}
        return True

    def after_response(self):
        pass

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

            mname = self.command.lower()
            if not hasattr(self, mname) or mname not in BaseHandler.supported_methods:
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            # check authorization hook
            if not self.authorize():
                self.send_error(
                    HTTPStatus.UNAUTHORIZED,
                    "Not authorized")
                return
            method()
            self.wfile.flush()  # actually send the response if not already done.
        except socket.timeout as e:
            # a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return
        finally:
            # after response has been sent
            self.after_response()
