# coding=utf-8
"""
Main Window. It contains basic UI.
"""


import os
import wx

from lib.i18n import gettext as _


class MainWindow(wx.Frame):
    title = _('Digital Signal Processing')

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)

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
        pass

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





