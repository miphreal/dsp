# coding=utf-8
"""
Docstring
"""
__all__ = ['Conf', 'app_config']

from constants import events
from lib.event import app_events


class Conf(dict):
    def __init__(self, config=None, events_=app_events, *args, **kwargs):
        self.events = events_
        super(Conf, self).__init__(*args, **kwargs)
        self.update(config or {})

        self.events.on(events.DO_UPDATE_CONFIG, self._update)
        self.events.on(events.DO_SET_PARAMETER, self._set_parameter)

    def on(self, *args, **kwargs): return self.events.on(*args, **kwargs)
    def off(self, *args, **kwargs): return self.events.off(*args, **kwargs)
    def trigger(self, *args, **kwargs): return self.events.trigger(*args, **kwargs)

    def _set_parameter(self, key, value):
        self.__setattr__(key, value)

    def _update(self, config):
        for k,v in config.items():
            self.__setattr__(k, v)

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        changed = key not in self or (self.get(key) != value)
        self[key] = value
        if changed:
            self.events.trigger(events.EVENT_CHANGED_CONFIG, config=self)
            self.events.trigger(events.EVENT_CHANGED_PARAMETER.replace('*', key), key=key, value=value)


app_config = Conf()