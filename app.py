from threading_srv import BaseRequestHandler
from threading_srv import Core
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


class CustomBaseHandler(BaseRequestHandler):

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

    def gett(self):
        CustomBaseHandler.counter += 1
        print(CustomBaseHandler.counter)
        while not self.go:
            time.sleep(0.01)
        # self.send_response(200)
        # self.end_headers()
        message = threading.currentThread().getName()
        self.write('token for %s is `%s`\n' % (message, self.user['some_token']))

    def get(self):
        # self.send_response(200)
        # self.end_headers()
        message = threading.currentThread().getName()
        self.write('token for %s is `%s`\n' % (message, self.user['some_token']))

    def head(self):
        signals.publish('my msg', 'general')
        # self.send_response(200)
        # self.end_headers()


if __name__ == '__main__':
    app = Core({
        r'/sub': CustomBaseHandler,
        r'/pub': CustomBaseHandler
    })
    try:
        print('Starting server, use <Ctrl-C> to stop')
        app.run('0.0.0.0', 8080)
    except KeyboardInterrupt:
        pass
