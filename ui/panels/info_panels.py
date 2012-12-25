# coding=utf-8
"""
Set of panels to show state information
"""

import wx


class BaseInfo(wx.Panel):
    def __init__(self, main_frame=None, *args, **kwargs):
        self.main_frame = kwargs.get('main_frame')
        self.events = self.main_frame.events
        super(BaseInfo, self).__init__(*args, **kwargs)

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
    pass


class SignalInfo(BaseInfo):
    pass


class Values(BaseInfo):
    pass


class Properties(BaseInfo):
    pass

