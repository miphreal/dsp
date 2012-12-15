# coding=utf-8
"""
Set of classes to represent the data
"""
import numpy as np

from lib.i18n import gettext as _


VISUALIZERS = []


class BaseVisualizer(object):
    visualizer_name = _('Base Visualizer')

    def __init__(self, canvas, data, parent_frame):
        self.canvas = canvas
        self.data = data
        self.frame = parent_frame
        self.draw()

    def draw(self):
        pass


class TestVisualizer(BaseVisualizer):
    visualizer_name = _('Test Visualizer')

    def draw(self):
        def f(t):
            return np.exp(-t) * np.cos(2 * np.pi * t)

        t1 = np.arange(0.0, 5.0, 0.1)
        t2 = np.arange(0.0, 5.0, 0.02)

        plt = self.canvas.figure.add_subplot(311)
        plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')

        plt = self.canvas.figure.add_subplot(312)
        plt.plot(t2, np.cos(2 * np.pi * t2), 'r--')

        mu, sigma = 100, 15
        x = mu + sigma * np.random.randn(10000)

        plt = self.canvas.figure.add_subplot(313, xlabel='Smarts', ylabel='Probability')
        # the histogram of the data
        n, bins, patches = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)

        plt.set_title('Histogram of IQ')
        plt.text(60, .025, r'$\mu=100,\ \sigma=15$')

        plt.axis([40, 160, 0, 0.03])
        plt.grid(True)

        self.canvas.figure.tight_layout()
        self.canvas.draw()


class ParametersVisualizer(BaseVisualizer):
    visualizer_name = _('Signal Info')


# Register
VISUALIZERS.extend([
    TestVisualizer
])
