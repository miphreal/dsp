# coding=utf-8
"""
Set of panels to show state information
"""

import wx

from constants import events
from lib.event import on
from lib.log import subscribe


class BaseInfo(wx.Panel):
    def __init__(self, main_frame, *args, **kwargs):
        self.main_frame = main_frame
        super(BaseInfo, self).__init__(*args, **kwargs)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._init()
        self.SetSizer(self.sizer)

    def _init(self):
        """Initialize. Must be overridden"""

    @property
    def data(self):
        if self.main_frame:
            return self.main_frame.data
        return []

    @property
    def visualizer(self):
        if self.main_frame:
            return self.main_frame.visualizer
        return None


class Files(BaseInfo):
    def _init(self):
        self.list_box_files = wx.ListBox(self)
        self.sizer.Add(self.list_box_files, 1, wx.EXPAND, 0)
        on(events.EVENT_DATA_LOADED, self.on_data_load)

    def on_data_load(self, *args, **kwargs):
        self.list_box_files.SetItems([f.file_name for f in self.data])


class SignalInfo(BaseInfo):
    pass


class Values(BaseInfo):
    pass


class Properties(BaseInfo):
    pass


class Log(BaseInfo):
    def _init(self):
        self.text_ctrl_log = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.sizer.Add(self.text_ctrl_log, 1, wx.EXPAND, 0)

        subscribe(self.on_log)

    def on_log(self, msg):
        self.text_ctrl_log.AppendText(msg + '\n\n')