# coding=utf-8
"""
Set of classes to represent the data
"""
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from matplotlib.widgets import MultiCursor

from constants import events
from lib.config import app_config
from lib.event import app_events, trigger, on
from lib.i18n import gettext as _


VISUALIZERS = []

DEFAULT_DRAW_CONFIG = {
    'draw_dpi': 100,
    'draw_figure_height': 2.0,
    'draw_page_size': 1000,
    'draw_position': 0,
    'draw_facecolor': '#D4EF9F',
    'draw_static_cursor_color': '#21009B',
    'draw_dynamic_cursor_color': '#FF4D4D',
}
app_events.trigger(events.DO_UPDATE_CONFIG, DEFAULT_DRAW_CONFIG)


class BaseVisualizer(object):
    visualizer_name = _('Base Visualizer')

    def __init__(self, canvas_panel, data, parent_frame):
        trigger(events.EVENT_VISUALIZER_DRAW, visualizer=self)
        self.conf = app_config

        # variables section
        self.canvas_panel = canvas_panel
        self.data = data
        self.processed_data = None
        self.frame = parent_frame
        self.events = app_events
        self.plots = []
        self.vline = []

        # calculate data
        self.process()

        # prepare canvas
        size = self.canvas_panel.Size
        figsize = (float(size[0]) / self.conf.draw_dpi, self.conf.draw_figure_height * len(self.data))
        self.fig = Figure(
            dpi=self.conf.draw_dpi,
            facecolor=self.conf.draw_facecolor,
            figsize=figsize
        )
        self.canvas = FigCanvas(self.canvas_panel, -1, self.fig)

        # display controls
        self.draw()

        # bind events
        on(events.EVENT_VISUALIZER_DRAW, self.on_any_visualizer_draw)
        self.conf.on(events.EVENT_CHANGED_PARAMETER_key('draw_*'), self.on_config_changed)
        self.on('button_press_event', self.on_button_press_event)
        self.on('motion_notify_event', self.on_motion_notify_event)

    def create_cursor(self):
        self.cursor = MultiCursor(self.fig.canvas, self.plots, color=self.conf.draw_dynamic_cursor_color, lw=1)

    def create_vline(self):
        self.vline.extend(plot.axvline(color=self.conf.draw_static_cursor_color) for plot in self.plots)

    def on(self, event, func):
        """ Canvas events """
        self.fig.canvas.mpl_connect(event, func)

    def on_any_visualizer_draw(self, visualizer):
        if visualizer is not self:
            self.clear()

    def on_config_changed(self, key, value):
        if key in ('draw_position', 'draw_page_size'):
            self.update_plots()
        elif key in ('draw_dpi', 'draw_figure_height', 'draw_facecolor'):
            self.update_figure()
        elif key == 'draw_static_cursor_color':
            for line in self.vline:
                line.set_color(value)
            self.canvas.draw()
        elif key == 'draw_dynamic_cursor_color':
            for line in self.cursor.lines:
                line.set_color(value)
            self.canvas.draw()

    def on_button_press_event(self, event):
        self.update_vline(event.xdata)

    def on_motion_notify_event(self, event): pass

    def update_vline(self, x):
        for line in self.vline:
            line.set_xdata(x)
        self.canvas.draw()

    def update_plots(self):
        position = self.conf.draw_position
        page_size = self.conf.draw_page_size
        frame = (position - page_size if position > page_size else 0,
                 position if position >= page_size else page_size)
        for plt in self.plots:
            plt.set_xlim(frame)
        self.canvas.draw()

    def update_figure(self):
        self.fig.set_dpi(self.conf.draw_dpi)
        self.fig.set_figheight(self.conf.draw_figure_height * len(self.data))
        self.fig.set_facecolor(self.conf.draw_facecolor)
        self.canvas_panel.SetBackgroundColour(self.conf.draw_facecolor)
        self.canvas_panel.Update()
        self.canvas.draw()

    def create_aux(self):
        self.create_cursor()
        self.create_vline()
        self.canvas.figure.tight_layout()
        self.canvas_panel.update_scroll(self.canvas.Size)

    def draw(self):
        """Visualizes calculated data"""

    def clear(self):
        """Clear canvas"""
        self.canvas.figure.clear()
        self.canvas.draw()

    def process(self):
        """Calculates needed information"""
        self.processed_data = self.data

    def print_figure(self, path):
        """Export canvas into the file ``path``"""
        self.canvas.print_figure(path, dpi=self.conf.draw_dpi)


class SignalsMapVisualizer(BaseVisualizer):
    visualizer_name = _('Clear Signals Map Visualizer')

    def process(self):
        self.processed_data = self.data

    def create_plots(self):
        for i, data in enumerate(self.processed_data, 1):
            plt = self.canvas.figure.add_subplot(len(self.processed_data), 1, i)
            plt.set_xlim([0, self.conf.draw_page_size])
            plt.plot(data.float_data, 'k-')

            self.plots.append(plt)

    def draw(self):
        self.create_plots()

        self.create_aux()

        self.canvas.draw()

# Register
VISUALIZERS.extend([
    SignalsMapVisualizer,
])
