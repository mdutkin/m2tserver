from threading_srv import ThreadedHTTPServer
from threading_srv import BaseHandler
from threading_srv.middleware import AuthorizationMixin
import threading
import redis
from threading_srv.utils import EventDispatcher
import time

redis_host = '127.0.0.1'
redis_port = 6379
redis_db = 0
redis_connection_pool_kwargs = {}

r = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=redis_host,
        port=str(redis_port),
        db=redis_db,
        decode_responses=True,
        **redis_connection_pool_kwargs
    ),
)
r.set('auth', 'Hello, World!')


signals = EventDispatcher()


class CustomBaseHandler(AuthorizationMixin, BaseHandler):

    counter = 0

    def say(self, *args, **kwargs):
        self.go = True
        print('let\' say: ', args, kwargs)

    def after_response(self):
        signals.unsubscribe(self.say)

    def initialize(self):
        # here subscribe
        self.go = False
        signals.subscribe(self.say, channel='general')

    def authorize(self):
        """
        authorize via redis (just check some keys)
        """
        auth = r.get('auth')
        self.user = {
            'id': 1,
            'some_token': auth
        }
        return auth

    def get(self):
        CustomBaseHandler.counter += 1
        print(CustomBaseHandler.counter)
        while not self.go:
            time.sleep(0.01)
        self.send_response(200)
        self.end_headers()
        message = threading.currentThread().getName()
        self.wfile.write(('token for %s is `%s`\n' % (message, self.user['some_token'])).encode('utf-8'))

    def head(self):
        signals.publish('my msg', 'general')
        self.send_response(200)
        self.end_headers()


if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8080), CustomBaseHandler)
    print('Starting server, use <Ctrl-C> to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
