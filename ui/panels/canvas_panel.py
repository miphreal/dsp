# coding=utf-8
"""
Main panel to draw graphics
"""

import wx


class CanvasPanel(wx.ScrolledWindow):
    SCROLL_STEP = 20


    def __init__(self, main_frame=None, *args, **kwargs):
        self.main_frame = main_frame
        super(CanvasPanel, self).__init__(*args, style=wx.TAB_TRAVERSAL, **kwargs)

    def update_scroll(self, size):
        self.SetScrollbars(0, self.SCROLL_STEP, 0, size[1]/self.SCROLL_STEP + 1)

