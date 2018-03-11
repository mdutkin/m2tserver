import threading

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class EventDispatcher:
    """
    In case you want to communicate between threads you can use this class
    """

    def __init__(self):
        self.channels = dict()
        self.r_lock = threading.RLock()

    def __channel_cleanup(self):
        for c in self.channels:
            for i, cb in enumerate(self.channels[c]):
                if not cb:
                    del self.channels[c][i]
            if len(c) == 0:
                del self.channels[c]

    def subscribe(self, cb, channel='*'):
        with self.r_lock:
            # print('subscribed %s' % hex(id(cb)))
            if channel not in self.channels:
                self.channels[channel] = list()
            self.channels[channel].append(cb)
            self.__channel_cleanup()

    def unsubscribe(self, cb):
        with self.r_lock:
            break_all = False
            for c in self.channels:
                if break_all:
                    break
                for i, _cb in enumerate(self.channels[c]):
                    if cb == _cb:
                        # print('unsubscribed %s' % hex(id(_cb)))
                        del self.channels[c][i]
                        break_all = True
                        break
        print(len(self.channels), [len(self.channels[x]) for x in self.channels])

    def publish(self, msg='', channel='*', *args, **kwargs):
        with self.r_lock:
            if channel == '*':
                # publish to all channels
                for c in self.channels:
                    for i, cb in enumerate(self.channels[c]):
                        if cb is not None:
                            cb(msg, *args, **kwargs)
                        else:
                            # lost reference
                            del self.channels[c][i]
            else:
                if channel in self.channels:
                    for i, cb in enumerate(self.channels[channel]):
                        if cb is not None:
                            cb(msg, *args, **kwargs)
                        else:
                            # lost reference
                            del self.channels[channel][i]
