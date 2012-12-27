# coding=utf-8
"""
Set of panels to show state information
"""

import wx

from constants import events
from lib.event import on, trigger
from lib.i18n import gettext as _
from lib.log import subscribe


class BaseInfo(wx.Panel):
    def __init__(self, main_frame, *args, **kwargs):
        self.main_frame = main_frame
        super(BaseInfo, self).__init__(*args, **kwargs)
        self.sizer = self._get_sizer()
        self._init()
        self.SetSizer(self.sizer)

    def _init(self):
        """Initialize. Must be overridden"""

    def _get_sizer(self):
        return wx.BoxSizer(wx.VERTICAL)

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


class SignalInfo(BaseInfo):
    def _get_sizer(self):
        return wx.BoxSizer(wx.HORIZONTAL)

    def _init(self):
        self.list_box_files = wx.ListBox(self)
        self.sizer.Add(self.list_box_files, 1, wx.EXPAND, 0)

        self.list_ctrl_info = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_ALIGN_LEFT | wx.SUNKEN_BORDER)
        self.list_ctrl_info.InsertColumn( 0, _('Parameter'), width=400)
        self.list_ctrl_info.InsertColumn( 1, _('Value'), width=200)
        self.sizer.Add(self.list_ctrl_info, 1, wx.EXPAND, 0)

        on(events.EVENT_DATA_LOADED, self.on_data_load)
        self.list_box_files.Bind(wx.EVT_LISTBOX, self.on_select_signal)

    def on_select_signal(self, event):
        self._show_signal_info(signal_id=event.Int)
        trigger(events.EVENT_PANELS_FILES_SELECTED, signal_id=event.Int, signal=self.data[event.Int])

    def on_data_load(self, *args, **kwargs):
        # init file list
        self.list_box_files.SetItems([f.file_name for f in self.data])
        self.list_box_files.Select(0)

        # init signal info
        self._show_signal_info()

    def _show_signal_info(self, signal_id=0):
        self.list_ctrl_info.DeleteAllItems()
        data = self.data[signal_id]
        for field in data.header._fields:
            self._insert_entry(_(field), unicode(getattr(data.header, field)))

    def _insert_entry(self, label, value):
        index = self.list_ctrl_info.GetItemCount()
        self.list_ctrl_info.InsertStringItem(index, label)
        self.list_ctrl_info.SetStringItem(index, 1, value)



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