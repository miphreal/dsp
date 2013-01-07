# coding=utf-8
"""
Set of panels to show state information
"""

import wx
import numpy as np

from constants import events
from lib.config import app_config
from lib.event import on, trigger
from lib.i18n import gettext as _
from lib.log import subscribe


class BaseInfo(wx.Panel):
    def __init__(self, main_frame, *args, **kwargs):
        self.conf = app_config
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
    _fields = (
        (_('Range'), 'range'),
        (_('Number of values'), 'num'),
        (_('Abs Max'), 'abs_max'),
        (_('Abs Min'), 'abs_min'),
        (_('Power of signal'), 'power'),
        (_('Range of vibration'), 'range_vibration'),
        (_('Average value'), 'avg'),
        (_('Effective value'), 'avg_sqr'),
    )

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
        for field, func_name in self._fields:
            self._insert_entry(field, unicode(getattr(self, func_name)(data)))

    def _insert_entry(self, label, value):
        index = self.list_ctrl_info.GetItemCount()
        self.list_ctrl_info.InsertStringItem(index, label)
        self.list_ctrl_info.SetStringItem(index, 1, value)

    def _f(self, data):
        position = self.conf.draw_position
        page_size = self.conf.draw_page_size
        floor = int(position - page_size if position > page_size else 0)
        ceil = int(position if position >= page_size else page_size)
        return np.array(data.float_data[floor:ceil])

    def num(self, data):
        return len(self._f(data))

    def range(self, data):
        position = self.conf.draw_position
        page_size = self.conf.draw_page_size
        floor = int(position - page_size if position > page_size else 0)
        ceil = int(position if position >= page_size else page_size)
        return '%.4f - %.4f sec' % (data.to_time(floor), data.to_time(ceil))

    def abs_max(self, data):
        d = self._f(data)
        return np.abs(np.max(d))

    def abs_min(self, data):
        d = self._f(data)
        return np.abs(np.min(d))

    def avg(self, data):
        d = self._f(data)
        return np.average(d)

    def power(self, data):
        d = self._f(data)
        return np.average(np.square(d))

    def range_vibration(self, data):
        d = self._f(data)
        return np.max(d) - np.min(d)

    def avg_sqr(self, data):
        import math
        return math.sqrt(self.power(data))


class Properties(BaseInfo):
    slider_label = _('Frame position: %s/%s')
    zoom_label = _('Zoom: %s%% (width: %s)')

    ZOOM_DIM = 1000000

    def _init(self):
        self.max_data_size = 0

        # init ui
        self._create_slider()
        self._create_zoom()
        self._create_color_props()

        # bind events
        on(events.EVENT_DATA_LOADED, self.evt_on_data_load)
        self.slider.Bind(wx.EVT_SCROLL_ENDSCROLL, self.evt_set_config_scroll_position)
        self.slider.Bind(wx.EVT_SCROLL_THUMBTRACK, self.evt_update_scroll_label)
        self.zoom.Bind(wx.EVT_SCROLL_ENDSCROLL, self.evt_set_config_zoom)
        self.zoom.Bind(wx.EVT_SCROLL_THUMBTRACK, self.evt_update_zoom_label)

        self.button_facecolor.Bind(wx.EVT_COLOURPICKER_CHANGED, self.evt_on_select_bg_colour)
        self.button_static_cursor_color.Bind(wx.EVT_COLOURPICKER_CHANGED, self.evt_on_select_static_cursor_color)
        self.button_dynamic_cursor_color.Bind(wx.EVT_COLOURPICKER_CHANGED, self.evt_on_select_dynamic_cursor_color)

    def _create_slider(self):
        self.slider_text = wx.StaticText(self, label=self.slider_label % (0, self.max_data_size))
        self.slider = wx.Slider(self, value=0, maxValue=0)
        self.sizer.Add(self.slider, 0, wx.EXPAND)
        self.sizer.Add(self.slider_text, 0, wx.ALIGN_CENTER_HORIZONTAL)

    def _update_slider(self):
        self.slider.SetMax(self.max_data_size)
        self.slider.SetValue(self.conf.draw_page_size)
        self.slider_text.SetLabel(self.slider_label % (self.slider.GetValue(), self.max_data_size))

    def _create_zoom(self):
        self.zoom_text = wx.StaticText(self, label=self.zoom_label % ('~', self.conf.draw_page_size))
        self.zoom = wx.Slider(self, minValue=1, maxValue=self.ZOOM_DIM, value=1)
        self.sizer.Add(self.zoom_text, 0, wx.ALIGN_LEFT)
        self.sizer.Add(self.zoom, 0, wx.EXPAND)

    def _zoom_get_percent(self): return float(self.zoom.GetValue()) / self.ZOOM_DIM * 100.0
    def _zoom_get_page_size(self): return int(round(float(self.zoom.GetValue()) / self.ZOOM_DIM * self.max_data_size))
    def _zoom_get_zoom_value_from_page_size(self): return float(self.conf.draw_page_size) / self.max_data_size * self.ZOOM_DIM

    def _update_zoom(self, set_value=True):
        if set_value:
            self.zoom.SetValue(self._zoom_get_zoom_value_from_page_size())
        self.zoom_text.SetLabel(self.zoom_label % (self._zoom_get_percent(), self._zoom_get_page_size()))

    def _create_color_props(self):
        self.colour_box = wx.StaticBox(self, label=_('Colours'))
        self.colour_box_sizer = wx.StaticBoxSizer(self.colour_box)

        self.colour_box_sizer.Add(wx.StaticText(self, label=_('Background Color:')), 0, wx.ALIGN_CENTER_VERTICAL)
        self.button_facecolor = wx.ColourPickerCtrl(self, col=self.conf.draw_facecolor)
        self.colour_box_sizer.Add(self.button_facecolor, 0, wx.ALIGN_CENTER_VERTICAL)
        self.colour_box_sizer.AddSpacer(20)

        self.colour_box_sizer.Add(wx.StaticText(self, label=_('Static Cursor Color:')), 0, wx.ALIGN_CENTER_VERTICAL)
        self.button_static_cursor_color = wx.ColourPickerCtrl(self, col=self.conf.draw_static_cursor_color)
        self.colour_box_sizer.Add(self.button_static_cursor_color, 0, wx.ALIGN_CENTER_VERTICAL)
        self.colour_box_sizer.AddSpacer(20)

        self.colour_box_sizer.Add(wx.StaticText(self, label=_('Dynamic Cursor Color:')), 0, wx.ALIGN_CENTER_VERTICAL)
        self.button_dynamic_cursor_color = wx.ColourPickerCtrl(self, col=self.conf.draw_dynamic_cursor_color)
        self.colour_box_sizer.Add(self.button_dynamic_cursor_color, 0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.Add(self.colour_box_sizer, 0, wx.EXPAND)

    def evt_on_data_load(self, *args, **kwargs):
        data = self.data
        if data:
            self.max_data_size = data.max_data_size()
            self.conf.draw_page_size = data.pluck('slice_freq').next()
            self._update_slider()
            self._update_zoom()

    def evt_update_scroll_label(self, event):
        self.slider_text.SetLabel(self.slider_label % (self.slider.GetValue(), self.max_data_size))

    def evt_set_config_scroll_position(self, event):
        self.conf.draw_position = self.slider.GetValue()

    def evt_update_zoom_label(self, event):
        self._update_zoom(False)

    def evt_set_config_zoom(self, event):
        self.conf.draw_page_size = self._zoom_get_page_size()

    def evt_on_select_bg_colour(self, event):
        self.conf.draw_facecolor = '#{:02X}{:02X}{:02X}'.format(*event.Colour.Get())

    def evt_on_select_static_cursor_color(self, event):
        self.conf.draw_static_cursor_color = '#{:02X}{:02X}{:02X}'.format(*event.Colour.Get())

    def evt_on_select_dynamic_cursor_color(self, event):
        self.conf.draw_dynamic_cursor_color = '#{:02X}{:02X}{:02X}'.format(*event.Colour.Get())


class Log(BaseInfo):
    def _init(self):
        self.text_ctrl_log = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.sizer.Add(self.text_ctrl_log, 1, wx.EXPAND, 0)

        subscribe(self.on_log)

    def on_log(self, msg):
        self.text_ctrl_log.AppendText(msg + '\n\n')