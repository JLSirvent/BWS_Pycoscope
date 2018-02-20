from __future__ import unicode_literals


import mplCanvas
import numpy as np
import ops_processing

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


PLOT_WIDTH = 7
PLOT_HEIGHT = 8

class QTabRawData(QWidget):

    def __init__(self, parent=None):

        super(QTabRawData, self).__init__(parent=None)

        self.main_widget = QStackedWidget(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        main_layout = QVBoxLayout(self.main_widget)
        self.plot = plot(self.main_widget, width=PLOT_WIDTH, height=PLOT_HEIGHT, dpi=100)
        self.navi_toolbar = NavigationToolbar(self.plot, self)
        main_layout.addWidget(self.navi_toolbar)
        main_layout.addWidget(self.plot)

        self.setLayout(main_layout)

    def actualise(self, Data, Configuration):

        self.plot.fig.clear()
        self.plot.y_SA_IN = Data.PS_PSA_IN
        self.plot.y_SB_IN = Data.PS_PSB_IN
        self.plot.x_IN = Data.PS_Time_IN

        self.plot.y_SA_OUT= Data.PS_PSA_OUT
        self.plot.y_SB_OUT = Data.PS_PSB_OUT
        self.plot.x_OUT = Data.PS_Time_OUT

        self.plot.y_PMTA_IN = Data.PMT_PMTA_IN
        self.plot.y_PMTB_IN = Data.PMT_PMTB_IN
        self.plot.y_PMTC_IN = Data.PMT_PMTC_IN
        self.plot.y_PMTD_IN = Data.PMT_PMTD_IN
        self.plot.x_PMT_IN = Data.PMT_Time_IN

        self.plot.y_PMTA_OUT = Data.PMT_PMTA_OUT
        self.plot.y_PMTB_OUT = Data.PMT_PMTB_OUT
        self.plot.y_PMTC_OUT = Data.PMT_PMTC_OUT
        self.plot.y_PMTD_OUT = Data.PMT_PMTD_OUT
        self.plot.x_PMT_OUT = Data.PMT_Time_OUT

        self.plot.compute_initial_figure(Configuration)
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

        self.y_SA_IN = np.ones(200)
        self.y_SB_IN = np.ones(200)
        self.x_IN = np.ones(200)

        self.y_SA_OUT = np.ones(200)
        self.y_SB_OUT = np.ones(200)
        self.x_OUT = np.ones(200)

        self.y_PMTA_IN = np.ones(200)
        self.y_PMTB_IN = np.ones(200)
        self.y_PMTC_IN = np.ones(200)
        self.y_PMTD_IN = np.ones(200)
        self.x_PMT_IN = np.ones(200)

        self.y_PMTA_OUT = np.ones(200)
        self.y_PMTB_OUT = np.ones(200)
        self.y_PMTC_OUT = np.ones(200)
        self.y_PMTD_OUT = np.ones(200)
        self.x_PMT_OUT = np.ones(200)

        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self, configuration=None):

        self.fig.clear()
        ax1 = self.fig.add_subplot(321)
        ax2 = self.fig.add_subplot(322)
        ax3 = self.fig.add_subplot(323)
        ax4 = self.fig.add_subplot(324)
        ax5 = self.fig.add_subplot(325)
        ax6 = self.fig.add_subplot(326)

        try:
            P = ops_processing.process_position(self.y_SA_IN, configuration, 1/(1e-3*(self.x_IN[1]-self.x_IN[0])), 1e-3*self.x_IN[0], return_processing=True)
            ax1.plot(P[0], P[1], linewidth=0.5)
            ax1.plot(P[2], P[3], '.', markersize=2)
            ax1.plot(P[4], P[5], '.', markersize=2)
            ax1.plot(P[6], P[7], '-', linewidth=0.5, color='black')
            # Added by Jose --> Visually identify references detection
            refX = P[9]
            refY = P[1][np.where(P[0] > P[9])[0][0]]
            ax1.plot(refX, refY, '.', markersize=5, color='#f93eed')
            # ----
        except:
            ax1.plot(self.x_IN, self.y_SA_IN, linewidth=0.5)
            print('Error processing Sensor A_IN')
        ax1.set_title('OPS - SA IN')
        ax1.set_xlabel('Time [ms]')
        ax1.set_ylabel('Amplitude [a.u]')

        try:
            P = ops_processing.process_position(self.y_SA_OUT, configuration, 1/(1e-3*(self.x_OUT[1]-self.x_OUT[0])), 1e-3*self.x_OUT[0], return_processing=True)
            ax2.plot(P[0], P[1], linewidth=0.5)
            ax2.plot(P[2], P[3], '.', markersize=2)
            ax2.plot(P[4], P[5], '.', markersize=2)
            ax2.plot(P[6], P[7], '-', linewidth=0.5, color='black')
            # Added by Jose --> Visually identify references detection
            refX = P[9]
            refY = P[1][np.where(P[0] > P[9])[0][0]]
            ax2.plot(refX, refY, '.', markersize=5, color='#f93eed')
            # ----
        except:
            ax2.plot(self.x_OUT, self.y_SA_OUT, linewidth=0.5)
            print('Error processing Sensor A_OUT')
        ax2.set_title('OPS - SA OUT')
        ax2.set_xlabel('Time [ms]')
        ax2.set_ylabel('Amplitude [a.u]')

        try:
            P = ops_processing.process_position(self.y_SB_IN, configuration, 1/(1e-3*(self.x_IN[1]-self.x_IN[0])), 1e-3*self.x_IN[0], return_processing=True)
            ax3.plot(P[0], P[1], linewidth=0.5)
            ax3.plot(P[2], P[3], '.', markersize=2)
            ax3.plot(P[4], P[5], '.', markersize=2)
            ax3.plot(P[6], P[7], '-', linewidth=0.5, color='black')
            # Added by Jose --> Visually identify references detection
            refX = P[9]
            refY = P[1][np.where(P[0] > P[9])[0][0]]
            ax3.plot(refX, refY, '.', markersize=5, color='#f93eed')
            # ----
        except:
            ax3.plot(self.x_IN, self.y_SB_IN, linewidth=0.5)
            print('Error processing Sensor B_IN')

        ax3.set_title('OPS - SB IN')
        ax3.set_xlabel('Time [ms]')
        ax3.set_ylabel('Amplitude [a.u]')

        try:
            P = ops_processing.process_position(self.y_SB_OUT, configuration, 1/(1e-3*(self.x_OUT[1]-self.x_OUT[0])), 1e-3*self.x_OUT[0], return_processing=True)
            ax4.plot(P[0], P[1], linewidth=0.5)
            ax4.plot(P[2], P[3], '.', markersize=2)
            ax4.plot(P[4], P[5], '.', markersize=2)
            ax4.plot(P[6], P[7], '-', linewidth=0.5, color='black')
            # Added by Jose --> Visually identify references detection
            refX = P[9]
            refY = P[1][np.where(P[0] > P[9])[0][0]]
            ax4.plot(refX, refY, '.', markersize=5, color='#f93eed')
            # ----
        except:
            ax4.plot(self.x_OUT, self.y_SB_OUT, linewidth=0.5)
            print('Error processing Sensor B_OUT')

        ax4.set_title('OPS - SB OUT')
        ax4.set_xlabel('Time [ms]')
        ax4.set_ylabel('Amplitude [a.u]')

        try:
            ax5.plot(self.x_PMT_IN, self.y_PMTA_IN, color = 'blue')
        except:
            pass
        try:
            ax5.plot(self.x_PMT_IN, self.y_PMTB_IN, color = 'red')
        except:
            pass
        try:
            ax5.plot(self.x_PMT_IN, self.y_PMTC_IN, color = 'green')
        except:
            pass
        try:
            ax5.plot(self.x_PMT_IN, self.y_PMTD_IN, color = 'yellow')
        except:
            pass

        ax5.set_title('PMTs IN')
        ax5.set_xlabel('Time [ms]')
        ax5.set_ylabel('Amplitude [mV]')

        try:
            ax6.plot(self.x_PMT_OUT, self.y_PMTA_OUT, color = 'blue')
        except:
            pass
        try:
            ax6.plot(self.x_PMT_OUT, self.y_PMTB_OUT, color = 'red')
        except:
            pass
        try:
            ax6.plot(self.x_PMT_OUT, self.y_PMTC_OUT, color = 'green')
        except:
            pass
        try:
            ax6.plot(self.x_PMT_OUT, self.y_PMTD_OUT, color = 'yellow')
        except:
            pass
        ax6.set_title('PMTs OUT')
        ax6.set_xlabel('Time [ms]')
        ax6.set_ylabel('Amplitude [mV]')

        self.fig.tight_layout()