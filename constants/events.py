# coding=utf-8
"""
Common app event constants
"""

##
# EVENTS

# APP EVENTS
EVENT_APP_STARTED = 'app:started'


# DATA EVENTS
EVENT_DATA_LOADED = 'data:loaded'   # func(data)


# PANELS EVENTS
EVENT_PANELS_FILES_SELECTED = 'panels:files:selected'   # func(signal_id, signal)


# VISUALIZER EVENTS
EVENT_VISUALIZER_DRAW = 'visualizer:draw'   # func(visualizer)