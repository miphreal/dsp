# coding=utf-8
"""
Progress modal Frame
"""
import wx

from constants import events
from lib.config import app_config
from lib.event import trigger, on
from lib.i18n import gettext as _
from lib.log import get_logger


logger = get_logger('dsp.main_window')

DEFAULT_PROGRESS_CONFIG = {
    'main_progress_max': 100,
    'main_progress_position': 0,
    'main_progress_visible': False,
}
trigger(events.DO_UPDATE_CONFIG, DEFAULT_PROGRESS_CONFIG)


class ProgressWindow(wx.Dialog):
    SIZE = (300, 20)
    def __init__(self, parent):
        self.conf = app_config
        wx.Dialog.__init__(self, parent, -1, _('Progress'), size=self.SIZE,
            style=wx.DEFAULT_DIALOG_STYLE|wx.FRAME_NO_TASKBAR|wx.FRAME_NO_WINDOW_MENU|wx.BORDER_NONE)
        self.create_progress()
        on(events.EVENT_CHANGED_PARAMETER_key('main_progress_*'), self.evt_on_change_config_parameter)

    ##
    # Interface building
    def create_progress(self):
        self.panel = wx.Panel(self)
        self.progress = wx.Gauge(self.panel,
            range=self.conf.main_progress_max,
            pos=(0, 0),
            size=self.SIZE
        )
        self.progress.SetValue(self.conf.main_progress_position)

    def _show(self, visible):
        self.Center(wx.CENTER_ON_SCREEN)
        self.Show(visible)
        self.Update()

    def _progress_value(self, value):
        self.progress.SetValue(value)
        self.progress.Update()

    ##
    # Event handling
    def evt_on_change_config_parameter(self, key, value):

        if key == 'main_progress_visible':
            self._show(value)
        elif key == 'main_progress_position':
            self._progress_value(value)
        elif key == 'main_progress_max':
            self.progress.SetRange(value)


def progress_max(max_position=None):
    if max_position is not None:
        app_config.main_progress_max = max_position
    return app_config.main_progress_max

def progress_tick(add=1):
    app_config.main_progress_position += add

def progress_new(max_position=None):
    progress_max(max_position)
    app_config.main_progress_position = 0
    app_config.main_progress_visible = True

def progress_release():
    app_config.main_progress_visible = False
