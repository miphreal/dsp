# coding=utf-8
"""
Main panel to draw graphics
"""

import wx


class CanvasPanel(wx.Panel):
    def __init__(self, main_frame=None, *args, **kwargs):
        self.main_frame = kwargs.get('main_frame')
        self.events = self.main_frame.events
        super(CanvasPanel, self).__init__(*args, **kwargs)

