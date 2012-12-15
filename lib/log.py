# coding=utf-8
"""
Logging system
"""

import logging
import sys


_subscribers = []

class LogListener(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        map(lambda func: func(msg), _subscribers)


def get_logger(name=None):
    return logging.getLogger(name)

def setup(level=logging.DEBUG, FORMAT=u'%(asctime)-15s - %(levelname)s:%(name)-10s: %(message)s'):
    logging.basicConfig(format=FORMAT, level=level)
    logger = get_logger()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)

    listener = LogListener()
    listener.setLevel(level)
    logger.addHandler(listener)

def subscribe(func):
    """
    `func` has following format:
        def my_func(msg): pass
    """
    global _subscribers
    if callable(func) and func not in _subscribers:
        _subscribers.append(func)

def unsubscribe(func):
    global _subscribers
    _subscribers = filter(lambda f: f is not func, _subscribers)