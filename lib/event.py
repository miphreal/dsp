# coding=utf-8
"""
Class to generate custom events
"""

import re
from itertools import chain
from functools import partial


class Events(dict):
    """
    Allows to organize hierarchical event tree.
    To determine hierarchy it's using ':' delimiter in names.

    Example:
        >>> e = lib.event.Events()
        >>> e.on('r:a:aa', lambda: 'aa')
        >>> e.on('r:b:bb', lambda: 'bb')
        >>> e.on('r:a', lambda: 'a')
        >>> e.on('r:b', lambda: 'b')
        >>> e.on('r', lambda: 'r')
        >>> e.trigger('r:a:aa')
        ['r', 'a', 'aa']
        >>> e.trigger('r')
        ['r']
        >>> e.off('r:a')
        >>> e.trigger('r:a:aa')
        ['r', 'aa']
        >>> e.trigger('r:*', propagate=ES_PROPAGATE_CURRENT)
        ['r:a', 'r:a:aa', 'r:b', 'r:b:bb']

    r:* = [r:a, r:b, r:a:aa, r:b:bb]
    r:~ = [r:a, r:b]
    *:bb = [r:b:bb]
    ~:b = [r:b]
    ~:bb = []

    * - 1+ any symbols
    ~ - 1+ any symbols except :

    If you use

    """

    DELIMITER = ':'
    WILD_CARD = '*'
    SOFT_WILD_CARD = '~'

    # Events scope types
    ES_PROPAGATE_TO_TOP = 1
    ES_PROPAGATE_CURRENT = 2
    ES_PROPAGATE_TO_DEEP = 4

    ES_PROPAGATE_DEFAULT = ES_PROPAGATE_TO_TOP|ES_PROPAGATE_CURRENT

    # Handlers call order
    CO_FROM_THE_END = 1 # if current 3: [h5 h4 h3 h2 h1]
    CO_FROM_CURRENT = 2 # if current 3: [h3 h1 h2 h3 h4]
    CO_FROM_THE_BEGIN = 3 # [h1 h2 h3 h4 h5]
    CO_DEFAULT = CO_FROM_CURRENT

    # Triggering behavior
    TB_CALL_ONCE = 1 # will be fired only unique handlers
    TB_CALL_EVERY = 2
    TB_DEFAULT = TB_CALL_ONCE

    # To avoid mix kwarg arguments
    KWARGS_PREFIX = 'event_opt_'


    def __init__(self, *args, **kwargs):
        super(Events, self).__init__(*args, **kwargs)

    def _generate_events(self, event_name, events_scope=ES_PROPAGATE_DEFAULT):
        events = []

        if events_scope & self.ES_PROPAGATE_TO_TOP:
            event = event_name
            while self.DELIMITER in event:
                event = event.rpartition(self.DELIMITER)[0]
                events.append(event)

        if events_scope & self.ES_PROPAGATE_TO_DEEP:
            event = event_name + self.DELIMITER
            events.extend(e for e in self if e.startswith(event))

        events.sort()

        if events_scope & self.ES_PROPAGATE_CURRENT:
            events.insert(0, event_name)

        return events

    def _get_handlers(self, event_name, call_order=CO_DEFAULT, events_scope=ES_PROPAGATE_DEFAULT):
        events = self._generate_events(event_name, events_scope=events_scope)
        if call_order == self.CO_FROM_THE_BEGIN:
            events.sort()
        elif call_order == self.CO_FROM_THE_END:
            events.sort(reverse=True)
        return chain(*[self.get(event, []) for event in events])

    def _generate_re(self, event_name):
        safe = '.+'.join(re.escape(event_name).split('\\'+self.WILD_CARD))
        safe = '[^{}]+'.format(self.DELIMITER).join(safe.split('\\'+self.SOFT_WILD_CARD))
        return re.compile(r'^{safe}$'.format(safe=safe), re.UNICODE)

    def _prepare_events(self, events):
        events = [events] if isinstance(events, basestring) else (events or [])
        prepared_events = []

        for event in events:
            event = event.strip()
            if self.WILD_CARD in event or self.SOFT_WILD_CARD in event:
                matcher = self._generate_re(event)
                prepared_events.extend(sorted(filter(matcher.match, self)))
            prepared_events.append(event)

        return prepared_events

    def _prepare_handlers(self, handlers):
        return [handlers] if callable(handlers) else (handlers or [])

    def _option(self, kw, option, default=None):
        return kw.pop(self.KWARGS_PREFIX+option, default)

    def options(self, **kwargs):
        """
        Reorganize options to pass to the trigger func
        """
        return dict((self.KWARGS_PREFIX+k, v) for k,v in kwargs.items())

    def trigger(self, events, *args, **kwargs):
        """
        Important: options should be passed with KWARGS_PREFIX in name.
        It helps to avoid mixing of same arguments in bind functions.
        """
        unique_call = self._option(kwargs, 'unique_call', self.TB_DEFAULT)
        call_order = self._option(kwargs, 'call_order', self.CO_DEFAULT)
        propagate = self._option(kwargs, 'propagate', self.ES_PROPAGATE_DEFAULT)

        events = self._prepare_events(events)
        get_handlers_func = partial(self._get_handlers,
            call_order=call_order,
            events_scope=propagate
        )
        executed = set()
        results = []
        for handler in chain(*map(get_handlers_func, events)):
            if handler not in executed or unique_call == self.TB_CALL_EVERY:
                results.append(handler(*args, **kwargs))
                executed.add(handler)
        return results

    def on(self, event_or_events, handler_or_handlers):
        events = self._prepare_events(event_or_events)
        handlers = self._prepare_handlers(handler_or_handlers)
        for event in events:
            hs = self.setdefault(event, [])
            hs.extend(filter(lambda h: h not in hs, handlers))

    def off(self, events=None, handlers=None):
        if events is None and handlers is None:
            self.clear() # unbind all events
        elif handlers is None:
            events = self._prepare_events(events)
            map(lambda e: self.pop(e, None), events) # unbind custom events
        else:
            target_events = self.keys() if events is None else filter(lambda e: e in self, self._prepare_events(events))
            for hs in map(self.get, target_events):
                map(hs.remove, filter(lambda h: h in hs, handlers)) #unbind handlers


# Registers common app events
app_events = Events()
trigger = app_events.trigger
on = app_events.on
off = app_events.off
opts = app_events.options


def test():
    e = Events()
    e.on('r:a:aa', lambda: 'r:a:aa')
    e.on('r:b:bb', lambda: 'r:b:bb')
    e.on('r:b', lambda: 'r:b')
    e.on('r:a', lambda: 'r:a')
    e.on('r', lambda: 'r')
    e.on(['1:2:3:4:5', '~:~:3'], [lambda: 'x', lambda: 'y'])

    print "e.trigger('r:a:aa')", e.trigger('r:a:aa')
    print "e.trigger('r')", e.trigger('r')
    print "e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'))
    print "once: e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'), **e.options(unique_call=Events.TB_CALL_ONCE))
    print "once, reversed: e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'),
        **e.options(unique_call=Events.TB_CALL_ONCE, call_order=Events.CO_FROM_THE_END))
    print "every, reversed: e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'),
        **e.options(unique_call=Events.TB_CALL_EVERY, call_order=Events.CO_FROM_THE_END))
    print "reversed: e.trigger('r:a:aa')", e.trigger('r:a:aa', **e.options(call_order=Events.CO_FROM_THE_END))

    print 'r:*', e.trigger('r:*', **e.options(propagate=Events.ES_PROPAGATE_CURRENT))
    print 'r:~', e.trigger('r:~')
    print '*:b', e.trigger('*:b')
    print '~:b', e.trigger('~:b')
    print '~:a:~', e.trigger('~:a:~')

    return e