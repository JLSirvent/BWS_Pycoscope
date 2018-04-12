from __future__ import unicode_literals


import mplCanvas
import numpy as np
import utils
import matplotlib.pyplot as plt

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


PLOT_WIDTH = 7
PLOT_HEIGHT = 8

class QTabRDS(QWidget):

    def __init__(self, parent=None):

        super(QTabRDS, self).__init__(parent=None)

        self.main_widget = QStackedWidget(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        main_layout = QVBoxLayout(self.main_widget)
        self.plot = plot(self.main_widget, width=PLOT_WIDTH, height=PLOT_HEIGHT, dpi=100)
        self.navi_toolbar = NavigationToolbar(self.plot, self)
        main_layout.addWidget(self.navi_toolbar)
        main_layout.addWidget(self.plot)

        self.setLayout(main_layout)

    def actualise(self, data_processed, configuration):

        self.plot.fig.clear()
        self.plot.TimesAIn = data_processed.PS_POSA_IN[0]
        self.plot.TimesBIn = data_processed.PS_POSB_IN[0]
        self.plot.TimesAOut = data_processed.PS_POSA_OUT[0]
        self.plot.TimesBOut = data_processed.PS_POSB_OUT[0]
        self.plot.Threshold = configuration.ops_relative_distance_correction_prameters
        self.plot.compute_initial_figure()
        self.plot.draw()

    def reset(self):
        self.plot.fig.clear()
        self.plot.compute_initial_figure()
        self.plot.draw()

class plot(mplCanvas.mplCanvas):

    def __init__(self, parent, width, height, dpi):

        self.TimesAIn = np.ones(200)
        self.TimesBIn = np.ones(200)

        self.TimesAOut = np.ones(200)
        self.TimesBOut = np.ones(200)

        self.Threshold = np.ones(2)

        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self):

        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)

        for i in range(0,2):
            if i==0:
                ax = ax1
                Scan = 'IN'
                TimesA = self.TimesAIn
                TimesB = self.TimesBIn
            else:
                ax = ax2
                Scan = 'OUT'
                TimesA = self.TimesAOut
                TimesB = self.TimesBOut

            offset = 100
            DistancesA = np.diff(TimesA[offset:TimesA.size - 1 - offset])
            DistancesB = np.diff(TimesB[offset:TimesB.size - 1 - offset])

            RDS_A = np.divide(DistancesA[1:DistancesA.size], DistancesA[0:DistancesA.size - 1])
            RDS_B = np.divide(DistancesB[1:DistancesB.size], DistancesB[0:DistancesB.size - 1])

            ax.axhspan(self.Threshold[1], self.Threshold[0], color='black', alpha=0.1)

            ax.plot(TimesA[0:RDS_A.size], RDS_A, '.', color='blue')
            ax.plot(TimesB[0:RDS_B.size], RDS_B, '.', color='red')
            ax.set_title('Relative Distance Signature - ' + Scan)
            ax.set_xlabel('Time [ms]')
            ax.set_ylabel('RDS')
            ax.legend('Sensor A', 'Sensor B')

        self.fig.tight_layout()