# coding=utf-8
"""
Main Window. It contains basic UI.
"""
from functools import partial

import os

import wx

from data import data_factory, SOURCE_DATA_TYPES_LINE
from lib.event import app_events
from lib.i18n import gettext as _
from lib.log import get_logger
from ui.panels import info_panels
from ui.panels.canvas_panel import CanvasPanel
from visualizer import VISUALIZERS


logger = get_logger('dsp.main_window')


class MainWindow(wx.Frame):
    title = _('Digital Signal Processing')

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        # to handle/trigger app events
        # A little convention:
        # namespaces: 'visualizer:'
        self.events = app_events

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.create_menu()
        self.create_tool_bar()
#        self.create_status_bar()

        self.create_canvas_panel()
        self.sizer.Add(self.canvas_panel, 3, wx.EXPAND, 0)

        self.create_info_panel()
        self.sizer.Add(self.info_panel, 1, wx.EXPAND, 0)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.Layout()

        self.Maximize()
        self.Show(True)

        self.data = None
        self.visualizer = None

    ##
    # Interface building
    def create_menu(self):
        self.menu_bar = wx.MenuBar()

        menu_file = wx.Menu()
        m_open = menu_file.Append(-1, _('Open data source'))
        menu_file.AppendSeparator()
        m_expt = menu_file.Append(-1, _('Save plot'))
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, _('Exit'))
        self.menu_bar.Append(menu_file, _('File'))

        menu_signal = wx.Menu()
        m_info = menu_signal.Append(-1, _('Signal Info Panel'), kind=wx.ITEM_CHECK)
        menu_signal.AppendSeparator()
        for visualiser in VISUALIZERS:
            item = menu_signal.Append(-1, visualiser.visualizer_name)
            self.Bind(wx.EVT_MENU, partial(self.on_choose_visualizer, visualizer_class=visualiser), item)

        self.menu_bar.Append(menu_signal, _('Signal'))

        menu_about = wx.Menu()
        m_author = menu_about.Append(-1, _('Author'))
        self.menu_bar.Append(menu_about, _('About'))

        # bind events
        self.Bind(wx.EVT_MENU, self.on_open, m_open)
        self.Bind(wx.EVT_MENU, self.on_export_image, m_expt)
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        self.Bind(wx.EVT_MENU, self.on_info_panel, m_info)

        # bind to the frame
        self.SetMenuBar(self.menu_bar)

    def create_tool_bar(self):
        pass

    def create_status_bar(self):
        self.status_bar = self.CreateStatusBar()

    def create_canvas_panel(self):
        self.canvas_panel = CanvasPanel(main_frame=self, parent=self)

    def create_info_panel(self):
        self.info_panel = wx.Notebook(self, -1, style=0)
        self.info_panel.Hide()
        self.info_panel_files = info_panels.Files(main_frame=self, parent=self.info_panel)
        self.info_panel_signal_info = info_panels.SignalInfo(main_frame=self, parent=self.info_panel)
        self.info_panel_values = info_panels.Values(main_frame=self, parent=self.info_panel)
        self.info_panel_properties = info_panels.Properties(main_frame=self, parent=self.info_panel)

        self.info_panel.AddPage(self.info_panel_files, _('Files'))
        self.info_panel.AddPage(self.info_panel_signal_info, _('Signal Info'))
        self.info_panel.AddPage(self.info_panel_values, _('Values'))
        self.info_panel.AddPage(self.info_panel_properties, _('Property'))

    ##
    # Event handling

    # Menu events
    def on_open(self, event):
        dlg = wx.FileDialog(
            self,
            message=_('Open data source'),
            defaultDir=os.getcwd(),
            defaultFile='',
            wildcard=SOURCE_DATA_TYPES_LINE,
            style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.data = data_factory(path)

    def on_choose_visualizer(self, event, visualizer_class=None):
        self.visualizer = visualizer_class(self.canvas_panel, self.data, self) if visualizer_class is not None else None

    def on_export_image(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog(
            self,
            message=_("Save plot as..."),
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.visualizer.print_figure(path)

    def on_exit(self, event):
        self.Destroy()

    def on_info_panel(self, event):
        self.info_panel.Show(not self.info_panel.IsShown())





