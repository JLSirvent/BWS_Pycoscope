from __future__ import unicode_literals

import numpy as np
import mplCanvas

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

PLOT_WIDTH = 7
PLOT_HEIGHT = 8

class QtabProcessedProfiles(QWidget):

    def __init__(self, parent=None):

        super(QtabProcessedProfiles, self).__init__(parent=None)

        self.main_widget = QStackedWidget(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        main_layout = QVBoxLayout(self.main_widget)
        self.plot = plot(self.main_widget, width=PLOT_WIDTH, height=PLOT_HEIGHT, dpi=100)
        self.navi_toolbar = NavigationToolbar(self.plot, self)
        main_layout.addWidget(self.navi_toolbar)
        main_layout.addWidget(self.plot)

        self.x_IN = np.ones(200)
        self.y_IN = np.ones(200)

        self.x_OUT = np.ones(200)
        self.y_OUT = np.ones(200)

        self.setLayout(main_layout)

    def actualise(self):
        self.plot.fig.clear()
        self.plot.x_IN = self.x_IN
        self.plot.y_IN = self.y_IN
        self.plot.x_OUT = self.x_OUT
        self.plot.y_OUT = self.y_OUT
        self.plot.compute_initial_figure()
        self.plot.draw()

    def reset(self):
        self.plot.fig.clear()
        self.plot.x_IN = np.ones(200)
        self.plot.y_IN = np.ones(200)
        self.plot.x_OUT = np.ones(200)
        self.plot.y_OUT = np.ones(200)
        self.plot.compute_initial_figure()
        self.plot.draw()

class plot(mplCanvas.mplCanvas):

    def __init__(self, parent, width, height, dpi):

        self.x_IN = np.ones(200)
        self.y_IN = np.ones(200)
        self.x_OUT = np.ones(200)
        self.y_OUT = np.ones(200)

        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self):

        self.fig.clear()
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        ax1.plot(self.x_IN,self.y_IN)
        ax1.set_title('Beam IN profile')
        ax1.set_xlabel('Position [mm]')
        ax1.set_ylabel('Amplitude [a.u]')
        ax2.plot(self.x_OUT,self.y_OUT)
        ax2.set_title('Beam OUT profile')
        ax2.set_xlabel('Position [mm]')
        ax2.set_ylabel('Amplitude [a.u]')

        self.fig.tight_layout()