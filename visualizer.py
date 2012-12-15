# coding=utf-8
"""
Set of classes to represent the data
"""
from lib.i18n import gettext as _


VISUALIZERS = []


class BaseVisualizer(object):
    visualizer_name = _('Base Visualizer')

    def __init__(self, canvas, data, parent_frame):
        self.canvas = canvas
        self.data = data
        self.frame = parent_frame


class TestVisualizer(BaseVisualizer):
    visualizer_name = _('Test Visualizer')


# Register
VISUALIZERS.append(TestVisualizer)
