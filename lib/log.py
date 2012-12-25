# coding=utf-8
"""
Logging system
"""

import logging
import sys

from lib.event import app_events


LOGGER_EVENT = 'logging:log'


class LogListener(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        app_events.trigger(LOGGER_EVENT, msg)


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
    app_events.on(LOGGER_EVENT, func)

def unsubscribe(func):
    app_events.off(LOGGER_EVENT, func)