# coding=utf-8
"""
Main Window. It contains basic UI.
"""

import os

import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas

from data import data_factory, SOURCE_DATA_TYPES_LINE
from lib.i18n import gettext as _
from lib.log import get_logger
from visualizer import VISUALIZERS, TestVisualizer


logger = get_logger('dsp.main_window')


class MainWindow(wx.Frame):
    title = _('Digital Signal Processing')

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title, size=(800, 650))

        self.create_menu()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_main_panel()

        self.Centre()
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
        m_info = menu_signal.Append(-1, _('Signal Info'))
        menu_signal.AppendSeparator()
        for visualiser in VISUALIZERS:
            menu_signal.Append(-1, visualiser.visualizer_name)
        self.menu_bar.Append(menu_signal, _('Signal'))

        menu_about = wx.Menu()
        m_author = menu_about.Append(-1, _('Author'))
        self.menu_bar.Append(menu_about, _('About'))

        # bind events
        self.Bind(wx.EVT_MENU, self.on_open, m_open)
        self.Bind(wx.EVT_MENU, self.on_export_image, m_expt)
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        # bind to the frame
        self.SetMenuBar(self.menu_bar)

    def create_tool_bar(self):
        pass

    def create_status_bar(self):
        self.status_bar = self.CreateStatusBar()

    def create_main_panel(self):
        #test behavior
        self.panel = wx.Panel(self)
        self.dpi = 100
        self.fig = Figure(dpi=self.dpi, facecolor='w')
        self.canvas = FigCanvas(self.panel, -1, self.fig)

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
            self.visualizer = TestVisualizer(self.canvas, self.data, self)

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
            self.canvas.print_figure(path, dpi=self.dpi)

    def on_exit(self, event):
        self.Destroy()





