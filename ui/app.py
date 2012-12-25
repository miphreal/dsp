# coding=utf-8
"""
Main Application class.
"""


import wx
import matplotlib
from constants import events
from lib.event import trigger

matplotlib.use('WXAgg')

from frames.main import MainWindow


class DSPApp(wx.App):
    def OnInit(self):
        self.window = MainWindow()
        self.SetTopWindow(self.window)
        trigger(events.EVENT_APP_STARTED)
        return True