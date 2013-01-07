# coding=utf-8
"""
Set of classes to represent the data
"""
import wx
import numpy as np
from matplotlib import ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from matplotlib.widgets import MultiCursor

from constants import events
from lib.config import app_config
from lib.event import app_events, trigger, on
from lib.i18n import gettext as _
from ui.frames.progress import progress_new, progress_release, progress_tick


VISUALIZERS = []

DEFAULT_DRAW_CONFIG = {
    'draw_dpi': 100,
    'draw_figure_height': 2.0,
    'draw_page_size': 3000,
    'draw_position': 0,
    'draw_facecolor': '#D4EF9F',
    'draw_static_cursor_color': '#21009B',
    'draw_dynamic_cursor_color': '#FF4D4D',
    'draw_plot_line_color': 'k',
    'draw_plot_line_linestyle': '-',
    'draw_plot_grid': True,
    'draw_plot_xlabel': 't, c',
    'draw_plot_title_color': '#395404',
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
        self.canvas_width, self.canvas_height = self.canvas_panel.Size
        figsize = (float(self.canvas_width) / self.conf.draw_dpi, self.conf.draw_figure_height * len(self.data))
        self.fig = Figure(
            dpi=self.conf.draw_dpi,
            facecolor=self.conf.draw_facecolor,
            figsize=figsize
        )
        self.canvas = FigCanvas(self.canvas_panel, -1, self.fig)

        # display controls
        self.draw()

        # bind events
        self.canvas_panel.Bind(wx.EVT_SIZE, self.evt_on_resize_panel)
        on(events.EVENT_VISUALIZER_DRAW, self.on_any_visualizer_draw)
        self.conf.on(events.EVENT_CHANGED_PARAMETER_key('draw_*'), self.on_config_changed)
        self.on('button_press_event', self.on_button_press_event)
        self.on('motion_notify_event', self.on_motion_notify_event)

    def create_cursor(self):
        if self.plots:
            self.cursor = MultiCursor(self.fig.canvas, self.plots, color=self.conf.draw_dynamic_cursor_color, lw=1)
            self.cursor.val_texts = []
            for i, plot in enumerate(self.plots):
                val_text = plot.text(0.15, 1.04, '', transform=plot.transAxes, fontsize=9, color=self.conf.draw_dynamic_cursor_color)
                val_text.plot = plot
                val_text.data = self.processed_data[i]
                self.cursor.val_texts.append(val_text)

    def create_vline(self):
        for i, plot in enumerate(self.plots):
            line = plot.axvline(color=self.conf.draw_static_cursor_color)
            line.plot = plot
            line.data = self.processed_data[i]
            line.val_text = plot.text(0.05, 1.04, '', transform=plot.transAxes, fontsize=9, color=self.conf.draw_static_cursor_color)
            self.vline.append(line)

    def on(self, event, func):
        """ Canvas events """
        self.fig.canvas.mpl_connect(event, func)

    def on_any_visualizer_draw(self, visualizer):
        if visualizer is not self:
            self.clear()
            self.conf.off(events.EVENT_CHANGED_PARAMETER_key('draw_*'), [self.on_config_changed])

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
        self.update_vline(event)
        if event.inaxes is not None and self.canvas.widgetlock.available(self):
            self.events.trigger(events.EVENT_VISUALIZER_STATIC_CURSOR_CHANGED, plot_event=event, data=self.processed_data)

    def on_motion_notify_event(self, event):
        self.update_cursor_label(event)
        if event.inaxes is not None and self.canvas.widgetlock.available(self):
            self.events.trigger(events.EVENT_VISUALIZER_DYNAMIC_CURSOR_CHANGED, plot_event=event, data=self.processed_data)

    def evt_on_resize_panel(self, event):
        cur_width = self.canvas_panel.Size[0]
        if self.canvas_width != cur_width:
            self.canvas_width = cur_width
            self.fig.set_figwidth(float(self.canvas_width) / self.conf.draw_dpi)
            self.canvas_panel.Refresh()
            self.canvas.draw()

    def _prepare_static_cursor_value(self, data, event):
        return '(%.3f, %.3f)' % (
            data.to_time(event.xdata),
            data.to_value(event.xdata))

    def update_vline(self, event):
        if event.inaxes:
            for line in self.vline:
                line.set_xdata(event.xdata)
                line.val_text.set_text(self._prepare_static_cursor_value(line.data, event))
            self.canvas.draw()

    def _prepare_dynamic_cursor_label(self, data, event):
        return '(%.3f, %.3f)' % (
            data.to_time(event.xdata),
            data.to_value(event.xdata))

    def update_cursor_label(self, event):
        if event.inaxes and False: #disabled
            for text in self.cursor.val_texts:
                text.set_text(self._prepare_dynamic_cursor_label(text.data, event))
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

            plt.set_title('%s signal' % i, fontsize=9, x=0.02, color=self.conf.draw_plot_title_color)

            plt.set_xlim([0, self.conf.draw_page_size])
            plt.plot(data.float_data, color=self.conf.draw_plot_line_color, linestyle=self.conf.draw_plot_line_linestyle)
            plt.grid(self.conf.draw_plot_grid)

            plt.set_xlabel(self.conf.draw_plot_xlabel, fontsize=9, color=self.conf.draw_plot_title_color)
            plt.xaxis.set_label_coords(1.03, -0.02)

            plt.xaxis.set_major_locator(ticker.LinearLocator(numticks=15))
            plt.xaxis.set_major_formatter(ticker.FuncFormatter(func=lambda x, pos: '%.3f' % data.to_time(x)))

            plt.tick_params(axis='both', which='major', labelsize=9)
            plt.tick_params(axis='both', which='minor', labelsize=7)

            self.plots.append(plt)
            progress_tick()

    def draw(self):
        progress_new(len(self.processed_data) + 2)
        self.create_plots()

        self.create_aux()
        progress_tick()

        self.canvas.draw()
        progress_release()


class SpectreVisualizer(BaseVisualizer):
    visualizer_name = _('Spectre Visualizer')

    def process(self):
        from scipy import fftpack

        def get_spectrum(signal, fq):
            signal = np.array(signal)
            n = len(signal)
            half = n / 2
            tm = float(n) / fq # time

            FFT = fftpack.fft(signal) / n

            frq = np.arange(half) / tm
            return frq, np.abs(FFT[:half])

        self.processed_data = []
        for data in self.data:
            fq = data.header.data_size / data.header.total_rcv_time

            position = self.conf.draw_position
            page_size = self.conf.draw_page_size
            frame = (int(position - page_size if position > page_size else 0),
                     int(position if position >= page_size else page_size))

            spectrum = get_spectrum(data.float_data[slice(*frame)], fq)

            self.processed_data.append(spectrum)

    def create_plots(self):
        for i, data in enumerate(self.processed_data, 1):
            plt = self.canvas.figure.add_subplot(len(self.processed_data), 1, i)

            plt.set_title('%s signal' % i, fontsize=9, x=0.02, color=self.conf.draw_plot_title_color)

            fq, amp = data
            lines = plt.plot(fq, amp, color=self.conf.draw_plot_line_color, linestyle=self.conf.draw_plot_line_linestyle)
            plt.fq_amp_lines = lines
            plt.grid(self.conf.draw_plot_grid)

            plt.set_xlabel('Fq, Hz', fontsize=9, color=self.conf.draw_plot_title_color)
            plt.xaxis.set_label_coords(1.03, -0.02)

            plt.tick_params(axis='both', which='major', labelsize=9)
            plt.tick_params(axis='both', which='minor', labelsize=7)

            self.plots.append(plt)
            progress_tick()

    def draw(self):
        progress_new(len(self.processed_data) + 2)
        self.create_plots()

        self.create_aux()
        progress_tick()

        self.canvas.draw()
        progress_release()

    def update_plots(self):
        self.process()
        for i, data in enumerate(self.processed_data):
            plt = self.plots[i]
            fq, amp = data
            line = plt.fq_amp_lines[0]
            line.set_xdata(fq)
            line.set_ydata(amp)

        self.canvas.draw()

    def _to_amp(self, data, x):
        from scipy.interpolate import splrep, splev
        tck = splrep(data[0], data[1], k=1, s=0)
        return splev(x, tck)

    def _prepare_static_cursor_value(self, data, event):
        return '(%.3f, %.3f)' % (
            event.xdata,
            self._to_amp(data, event.xdata))

class WaveletsVisualizer(BaseVisualizer):
    visualizer_name = _('Wavelets Visualizer')

    def process(self):
        import pywt
        self.processed_data = []
        for data in (d.clone() for d in self.data):
            data.float_data = pywt.dwt(data.float_data, 'db20', 'sp1')
            self.processed_data.append(data)

    def _to_sec(self, data, x):
        t = np.linspace(0.0, data.header.total_rcv_time / 2, len(data.float_data[1]))
        return t[int(round(x))]

    def create_plots(self):
        for i, data in enumerate(self.processed_data, 1):
            plt = self.canvas.figure.add_subplot(len(self.processed_data), 1, i)

            plt.set_title('%s signal' % i, fontsize=9, x=0.02, color=self.conf.draw_plot_title_color)

            plt.set_xlim([0, self.conf.draw_page_size])

            plt.plot(data.float_data[1], color=self.conf.draw_plot_line_color, linestyle=self.conf.draw_plot_line_linestyle)

            plt.grid(self.conf.draw_plot_grid)

            plt.set_xlabel(self.conf.draw_plot_xlabel, fontsize=9, color=self.conf.draw_plot_title_color)
            plt.xaxis.set_label_coords(1.03, -0.02)

            plt.xaxis.set_major_locator(ticker.LinearLocator(numticks=15))
            plt.xaxis.set_major_formatter(ticker.FuncFormatter(func=lambda x, pos: '%.3f' % self._to_sec(data, x)))

            plt.tick_params(axis='both', which='major', labelsize=9)
            plt.tick_params(axis='both', which='minor', labelsize=7)

            self.plots.append(plt)
            progress_tick()

    def draw(self):
        progress_new(len(self.processed_data) + 2)
        self.create_plots()

        self.create_aux()
        progress_tick()

        self.canvas.draw()
        progress_release()

    def update_plots(self):
        position = self.conf.draw_position
        page_size = self.conf.draw_page_size
        frame = (position - page_size if position > page_size else 0,
                 position if position >= page_size else page_size)
        for plt in self.plots:
            plt.set_xlim(frame)
        self.canvas.draw()

    def _prepare_static_cursor_value(self, data, event):
        return '(%.3f, %.3f)' % (
            self._to_sec(data, event.xdata),
            data.float_data[1][int(round(event.xdata))])


class SpectrogramVisualizer(SpectreVisualizer):
    visualizer_name = _('Spectrogram Visualizer')

    def process(self):
        self.processed_data = []
        for data in self.data:
            position = self.conf.draw_position
            page_size = self.conf.draw_page_size
            frame = (int(position - page_size if position > page_size else 0),
                     int(position if position >= page_size else page_size))

            self.processed_data.append(data.float_data[slice(*frame)])

    def create_plots(self):
        for i, data in enumerate(self.processed_data, 1):
            plt = self.canvas.figure.add_subplot(len(self.processed_data), 1, i)

            plt.set_title('%s signal' % i, fontsize=9, x=0.02, color=self.conf.draw_plot_title_color)
            origin_data = self.data[i-1]
            plt.specgram(data, Fs=origin_data.header.data_size/origin_data.header.total_rcv_time)

            plt.grid(self.conf.draw_plot_grid)
            plt.xaxis.set_label_coords(1.03, -0.02)

            plt.tick_params(axis='both', which='major', labelsize=9)
            plt.tick_params(axis='both', which='minor', labelsize=7)

            self.plots.append(plt)
            progress_tick()

    def draw(self):
        progress_new(len(self.processed_data) + 2)
        self.create_plots()

        self.canvas.figure.tight_layout()
        self.canvas_panel.update_scroll(self.canvas.Size)
        progress_tick()

        self.canvas.draw()
        progress_release()

    def update_plots(self):
        pass


# Register
VISUALIZERS.extend([
    SignalsMapVisualizer,
    SpectreVisualizer,
    WaveletsVisualizer,
    SpectrogramVisualizer,
])
