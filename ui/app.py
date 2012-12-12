# coding=utf-8
"""
Main Application class.
"""


import wx
import matplotlib
matplotlib.use('WXAgg')

from frames.main import MainWindow


class DSPApp(wx.App):
    def OnInit(self):
        self.window = MainWindow()
        self.SetTopWindow(self.window)
        return True