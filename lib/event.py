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
    CO_FROM_THE_END = 1
    CO_FROM_CURRENT = 2
    CO_DEFAULT = CO_FROM_CURRENT

    # Triggering behavior
    TB_CALL_ONCE = 1 # will be fired only unique handlers on each event tree
    TB_CALL_EVERY = 2
    TB_DEFAULT = TB_CALL_ONCE


    def __init__(self, hierarchy=True, *args, **kwargs):
        super(Events, self).__init__(*args, **kwargs)
        self.hierarchy = hierarchy

    def _generate_events(self, event_name, events_scope=ES_PROPAGATE_DEFAULT):
        events = []

        if events_scope & self.ES_PROPAGATE_CURRENT:
            events.append(event_name)

        event_name += self.DELIMITER
        if events_scope & self.ES_PROPAGATE_TO_DEEP:
            events.extend(e for e in self if e.startswith(event_name))

        if events_scope & self.ES_PROPAGATE_TO_TOP:
            while self.DELIMITER in event_name and self.hierarchy:
                event_name = event_name.rpartition(self.DELIMITER)[0]
                events.append(event_name)

        return sorted(events)

    def _get_handlers(self, event_name, reversed_call_order=CO_DEFAULT, events_scope=ES_PROPAGATE_DEFAULT):
        handlers = []
        for event in self._generate_events(event_name, events_scope=events_scope):
            handlers.extend(h for h in self.get(event, []) if h not in handlers)
        if reversed_call_order == self.CO_FROM_CURRENT:
            return reversed(handlers)
        return handlers

    def _generate_re(self, event_name):
        safe = '.+'.join(re.escape(event_name).split('\\'+self.WILD_CARD))
        safe = '[^{}]+'.format(self.DELIMITER).join(safe.split('\\'+self.SOFT_WILD_CARD))
        return re.compile(r'^{safe}$'.format(safe=safe), re.UNICODE)

    def _prepare_events(self, events):
        if events is None:
            return None
        events = [events] if isinstance(events, basestring) else events
        prepared_events = []

        for event in events:
            event = event.strip()
            if self.WILD_CARD in event or self.SOFT_WILD_CARD in event:
                matcher = self._generate_re(event)
                prepared_events.extend(sorted(filter(matcher.match, self)))
            else:
                prepared_events.append(event)

        return prepared_events

    def trigger(self, events, call_once=TB_DEFAULT,
                reversed_call_order=CO_DEFAULT,
                propagate=ES_PROPAGATE_TO_TOP,
                *args, **kwargs):

        events = self._prepare_events(events)
        get_handlers = partial(self._get_handlers,
                               reversed_call_order=reversed_call_order,
                               events_scope=propagate
        )
        executed = set()
        results = []
        for handler in chain(*map(get_handlers, events)):
            if handler not in executed or not call_once:
                results.append(handler(*args, **kwargs))
                executed.add(handler)
        return results

    def on(self, events, handler):
        events = self._prepare_events(events)
        for event in events:
            handlers = self.setdefault(event, [])
            if handler not in handlers:
                handlers.append(handler)

    def off(self, events=None, handlers=None):
        events = self._prepare_events(events)
        if events is None and handlers is None:
            self.clear() # unbind all events
        elif handlers is None:
            map(lambda e: self.pop(e, None), events) # unbind custom events
        else:
            target_events = self.keys() if events is None else filter(lambda e: e in self, events)
            for hs in map(self.get, target_events):
                map(hs.remove, filter(lambda h: h in hs, handlers)) #unbind handlers


def test():
    e = Events()
    e.on('r:a:aa', lambda: 'r:a:aa')
    e.on('r:b:bb', lambda: 'r:b:bb')
    e.on('r:b', lambda: 'r:b')
    e.on('r:a', lambda: 'r:a')
    e.on('r', lambda: 'r')
    print "e.trigger('r:a:aa')", e.trigger('r:a:aa')
    print "e.trigger('r')", e.trigger('r')
    print "e.trigger(('r', 'r:b:bb'))", e.trigger(('r', 'r:b:bb'))
    print "e.trigger(('r', 'r:b:bb'), once=True)", e.trigger(('r', 'r:b:bb'), call_once=True)
    print "e.trigger(('r', 'r:b:bb'), once=True, reversed_call_order=CO_FROM_THE_END)", e.trigger(('r', 'r:b:bb'), call_once=True, reversed_call_order=Events.CO_FROM_THE_END)
    print "e.trigger(('r', 'r:b:bb'), once=False, reversed_call_order=CO_FROM_THE_END)", e.trigger(('r', 'r:b:bb'), call_once=False, reversed_call_order=Events.CO_FROM_THE_END)
    print "e.trigger('r:a:aa', reversed_call_order=CO_FROM_THE_END)", e.trigger('r:a:aa', reversed_call_order=Events.CO_FROM_THE_END)

    print 'r:*', e.trigger('r:*', propagate=Events.ES_PROPAGATE_CURRENT)
    print 'r:~', e.trigger('r:~')
    print '*:b', e.trigger('*:b')
    print '~:b', e.trigger('~:b')
    print '~:a:~', e.trigger('~:a:~')