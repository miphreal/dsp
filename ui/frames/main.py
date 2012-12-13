# coding=utf-8
"""
Main Window. It contains basic UI.
"""


import os

import wx
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas

from lib.i18n import gettext as _


class MainWindow(wx.Frame):
    title = _('Digital Signal Processing')

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title, size=(800, 650))

        self.create_menu()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_main_panel()

        self.Centre()
        self.Show()

    ##
    # Interface building

    def create_menu(self):
        self.menu_bar = wx.MenuBar()

        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, _('Save plot'))
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, _('Exit'))
        self.menu_bar.Append(menu_file, _('File'))

        menu_signal = wx.Menu()
        m_info = menu_signal.Append(-1, _('Signal Info'))
        self.menu_bar.Append(menu_signal, _('Signal'))

        menu_about = wx.Menu()
        m_author = menu_about.Append(-1, _('Author'))
        self.menu_bar.Append(menu_about, _('About'))

        # bind events
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


        def f(t):
            return np.exp(-t) * np.cos(2*np.pi*t)

        t1 = np.arange(0.0, 5.0, 0.1)
        t2 = np.arange(0.0, 5.0, 0.02)

        plt = self.fig.add_subplot(311)
        plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')

        plt = self.fig.add_subplot(312)
        plt.plot(t2, np.cos(2*np.pi*t2), 'r--')

        mu, sigma = 100, 15
        x = mu + sigma * np.random.randn(10000)

        plt = self.fig.add_subplot(313, xlabel='Smarts', ylabel='Probability')
        # the histogram of the data
        n, bins, patches = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)

        plt.set_title('Histogram of IQ')
        plt.text(60, .025, r'$\mu=100,\ \sigma=15$')

        plt.axis([40, 160, 0, 0.03])
        plt.grid(True)

        self.fig.tight_layout()
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        self.canvas.draw()

    ##
    # Event handling

    # Menu events
    def on_export_image(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)

    def on_exit(self, event):
        self.Destroy()





