from __future__ import unicode_literals


import mplCanvas
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


PLOT_WIDTH = 7
PLOT_HEIGHT = 8

class QTabMotionData(QWidget):

    def __init__(self, parent=None):

        super(QTabMotionData, self).__init__(parent=None)

        self.main_widget = QStackedWidget(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        main_layout = QVBoxLayout(self.main_widget)
        self.plot = plot(self.main_widget, width=PLOT_WIDTH, height=PLOT_HEIGHT, dpi=100)
        self.navi_toolbar = NavigationToolbar(self.plot, self)
        main_layout.addWidget(self.navi_toolbar)
        main_layout.addWidget(self.plot)

        self.setLayout(main_layout)

    def actualise(self, data_processed):

        self.plot.fig.clear()
        self.plot.PosA_IN = data_processed.PS_POSA_IN
        self.plot.PosB_IN = data_processed.PS_POSB_IN
        self.plot.PosA_OUT = data_processed.PS_POSA_OUT
        self.plot.PosB_OUT = data_processed.PS_POSB_OUT
        self.plot.compute_initial_figure()
        self.plot.draw()

    def reset(self):
        self.plot.fig.clear()
        self.plot.compute_initial_figure()
        self.plot.draw()

class plot(mplCanvas.mplCanvas):

    def __init__(self, parent, width, height, dpi):

        self.PosA_IN = [np.ones(200), np.ones(200)]
        self.PosB_IN = [np.ones(200), np.ones(200)]

        self.PosA_OUT = [np.ones(200), np.ones(200)]
        self.PosB_OUT = [np.ones(200), np.ones(200)]

        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self):

        self.fig.clear()
        ax1 = self.fig.add_subplot(321)
        ax2 = self.fig.add_subplot(322)
        ax3 = self.fig.add_subplot(323)
        ax4 = self.fig.add_subplot(324)
        ax5 = self.fig.add_subplot(325)
        ax6 = self.fig.add_subplot(326)

        N = 10
        for i in range(0,2):
            if i==0:
                ax_pos = ax1
                ax_spe = ax3
                ax_ecc = ax5
                Scan = 'IN'
                Pos_A = self.PosA_IN
                Pos_B = self.PosB_IN
            else:
                ax_pos = ax2
                ax_spe = ax4
                ax_ecc = ax6
                Scan = 'OUT'
                Pos_A = self.PosA_OUT
                Pos_B = self.PosB_OUT

            ax_pos.plot(Pos_A[0], Pos_A[1])
            ax_pos.plot(Pos_B[0], Pos_B[1])
            ax_pos.set_title('Position - ' + Scan)
            ax_pos.set_xlabel('Time [ms]')
            ax_pos.set_ylabel('Position [rad]')

            try:
                SpeedA = np.divide(np.diff(Pos_A[1]),np.diff(1e-3*Pos_A[0]))
                SpeedA = np.convolve(SpeedA, np.ones((N,)) / N, mode='valid')
                SpeedB = np.divide(np.diff(Pos_B[1]), np.diff(1e-3*Pos_B[0]))
                SpeedB = np.convolve(SpeedB, np.ones((N,)) / N, mode='valid')

                ax_spe.plot(Pos_A[0][0:SpeedA.size],SpeedA)
                ax_spe.plot(Pos_B[0][0:SpeedB.size],SpeedB)

                ax_spe.set_title('Speed - ' + Scan)
                ax_spe.set_xlabel('Time [ms]')
                ax_spe.set_ylabel('Speed [rad/d]')
            except:
                pass

            ax_ecc.set_title('Eccentricity - ' + Scan)
            ax_ecc.set_xlabel('Time [ms]')
            ax_ecc.set_ylabel('Error [urad]')


        self.fig.tight_layout()