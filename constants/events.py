# coding=utf-8
"""
Common app event constants
"""

##
# EVENTS

# APP EVENTS
EVENT_APP_STARTED = 'app:started'


# CONFIG EVENTS
EVENT_CHANGED_CONFIG = 'config:changed' # func(config)
EVENT_CHANGED_PARAMETER = 'config:*:changed' # func(key, value) ~ config:key1:changed
EVENT_CHANGED_PARAMETER_key = lambda k: EVENT_CHANGED_PARAMETER.replace('*', k)
DO_UPDATE_CONFIG = 'config:do:update'   # func(config_dict)
DO_SET_PARAMETER = 'config:do:set'      # func(key, value)


# DATA EVENTS
EVENT_DATA_LOADED = 'data:loaded'   # func(data)


# PANELS EVENTS
EVENT_PANELS_FILES_SELECTED = 'panels:files:selected'   # func(signal_id, signal)


# VISUALIZER EVENTS
EVENT_VISUALIZER_DRAW = 'visualizer:draw'   # func(visualizer)