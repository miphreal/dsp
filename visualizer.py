# coding=utf-8
"""
Set of classes to represent the data
"""
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from constants import events

from lib.event import app_events, trigger, on
from lib.i18n import gettext as _


VISUALIZERS = []


class BaseVisualizer(object):
    visualizer_name = _('Base Visualizer')
    DPI = 100
    FIGURE_HEIGHT = 2.0

    def __init__(self, canvas_panel, data, parent_frame):
        trigger(events.EVENT_VISUALIZER_DRAW, visualizer=self)

        self.canvas_panel = canvas_panel
        self.data = data
        self.frame = parent_frame
        self.events = app_events

        self.dpi = self.DPI
        self.figure_height = self.FIGURE_HEIGHT

        size = self.canvas_panel.Size
        figsize = (float(size[0])/self.dpi, self.figure_height * len(self.data))
        self.fig = Figure(dpi=self.dpi, facecolor='w', figsize=figsize)
        self.canvas = FigCanvas(self.canvas_panel, -1, self.fig)

        self.process()
        self.draw()

        on(events.EVENT_VISUALIZER_DRAW, self.on_any_visualizer_draw)

    def on_any_visualizer_draw(self, visualizer):
        if visualizer is not self:
            self.clear()

    def draw(self):
        """Visualizes calculated data"""

    def clear(self):
        """Clear canvas"""
        self.canvas.figure.clear()
        self.canvas.draw()

    def process(self):
        """Calculates needed information"""

    def print_figure(self, path):
        """Export canvas into the file ``path``"""
        self.canvas.print_figure(path, dpi=self.dpi)


class TestVisualizer(BaseVisualizer):
    visualizer_name = _('Test Visualizer')

    def draw(self):
#        def f(t):
#            return np.exp(-t) * np.cos(2 * np.pi * t)
#
#        t1 = np.arange(0.0, 5.0, 0.1)
#        t2 = np.arange(0.0, 5.0, 0.02)
#
#        plt = self.canvas.figure.add_subplot(311)
#        plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')

        plt = self.canvas.figure.add_subplot(111)
        plt.plot(self.data[0].float_data, 'k-')

#        mu, sigma = 100, 15
#        x = mu + sigma * np.random.randn(10000)
#
#        plt = self.canvas.figure.add_subplot(313, xlabel='Smarts', ylabel='Probability')
#        # the histogram of the data
#        n, bins, patches = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)
#
#        plt.set_title('Histogram of IQ')
#        plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
#
#        plt.axis([40, 160, 0, 0.03])
#        plt.grid(True)

        self.canvas.figure.tight_layout()
        self.canvas.draw()


class SignalsMapVisualizer(BaseVisualizer):
    visualizer_name = _('Signals Map Visualizer')

    def draw(self):


        for i, data in enumerate(self.data, 1):
            plt = self.canvas.figure.add_subplot(len(self.data), 1, i)
            plt.plot(data.float_data, 'k-')

        self.canvas.figure.tight_layout()
        self.canvas_panel.update_scroll(self.canvas.Size)
        self.canvas.draw()

# Register
VISUALIZERS.extend([
    TestVisualizer,
    SignalsMapVisualizer,
])
