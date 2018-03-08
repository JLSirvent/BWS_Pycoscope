from __future__ import unicode_literals


import mplCanvas
import numpy as np
import utils

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

    def actualise(self, Data, Data_processed, Configuration):

        self.plot.fig.clear()
        self.plot.y_SA_IN = Data.PS_PSA_IN * Data.PS_Factors[0]
        self.plot.y_SB_IN = Data.PS_PSB_IN * Data.PS_Factors[1]

        self.plot.SA_IN_P = Data_processed.PS_POSA_IN_P
        self.plot.SB_IN_P = Data_processed.PS_POSB_IN_P
        self.plot.x_IN = Data.PS_TimesStart[0] + 1e3*(1.0*np.asarray(range(0,len(Data.PS_PSA_IN))) / Data.PS_Fs)

        self.plot.y_SA_OUT = Data.PS_PSA_OUT * Data.PS_Factors[0]
        self.plot.y_SB_OUT = Data.PS_PSB_OUT * Data.PS_Factors[1]

        self.plot.SA_OUT_P = Data_processed.PS_POSA_OUT_P
        self.plot.SB_OUT_P = Data_processed.PS_POSB_OUT_P
        self.plot.x_OUT = Data.PS_TimesStart[1] + 1e3*(1.0*np.asarray(range(0,len(Data.PS_PSA_OUT))) / Data.PS_Fs)

        self.plot.y_PMTA_IN = Data.PMT_PMTA_IN * Data.PMT_Factors[0]
        self.plot.y_PMTB_IN = Data.PMT_PMTB_IN * Data.PMT_Factors[1]
        self.plot.y_PMTC_IN = Data.PMT_PMTC_IN * Data.PMT_Factors[2]
        self.plot.y_PMTD_IN = Data.PMT_PMTD_IN * Data.PMT_Factors[3]
        self.plot.x_PMT_IN = Data.PMT_TimesStart[0] + 1e3*(1.0*np.asarray(range(0,len(Data.PMT_PMTA_IN))) / Data.PMT_Fs)

        self.plot.y_PMTA_OUT = Data.PMT_PMTA_OUT * Data.PMT_Factors[0]
        self.plot.y_PMTB_OUT = Data.PMT_PMTB_OUT * Data.PMT_Factors[1]
        self.plot.y_PMTC_OUT = Data.PMT_PMTC_OUT * Data.PMT_Factors[2]
        self.plot.y_PMTD_OUT = Data.PMT_PMTD_OUT * Data.PMT_Factors[3]
        self.plot.x_PMT_OUT = Data.PMT_TimesStart[1] + 1e3*(1.0*np.asarray(range(0,len(Data.PMT_PMTA_OUT))) / Data.PMT_Fs)

        self.plot.compute_initial_figure(Configuration)
        self.plot.draw()

class plot(mplCanvas.mplCanvas):

    def __init__(self, parent, width, height, dpi):

        self.y_SA_IN = np.ones(200)
        self.y_SB_IN = np.ones(200)
        self.SA_IN_P = np.ones(200)
        self.SB_IN_P = np.ones(200)
        self.x_IN = np.ones(200)

        self.y_SA_OUT = np.ones(200)
        self.y_SB_OUT = np.ones(200)
        self.SA_OUT_P = np.ones(200)
        self.SB_OUT_P = np.ones(200)
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
            Amplitude = np.max(self.y_SA_IN)
            Offset = np.min(self.y_SA_IN)
            ax1.plot(self.x_IN, self.y_SA_IN, linewidth=0.5)
            ax1.plot( self.SA_IN_P[2],  self.SA_IN_P[3]*Amplitude+Offset, '.', markersize=2)
            ax1.plot( self.SA_IN_P[4],  self.SA_IN_P[5]*Amplitude+Offset, '.', markersize=2)
            ax1.plot( self.SA_IN_P[6],  self.SA_IN_P[7]*Amplitude+Offset, '-', linewidth=0.5, color='black')
            refX = self.SA_IN_P[9]
            refY = self.y_SA_IN[np.where(self.x_IN > refX)[0][0]]
            ax1.plot(refX, refY, '.', markersize=5, color='#f93eed')
            ax1.set_title('OPS - SA IN')
            ax1.set_xlabel('Time [ms]')
            ax1.set_ylabel('Amplitude [a.u]')
        except:
            pass

        try:
            Amplitude = np.max(self.y_SA_OUT)
            Offset = np.min(self.y_SA_OUT)
            ax2.plot(self.x_OUT, self.y_SA_OUT, linewidth=0.5)
            ax2.plot( self.SA_OUT_P[2],  self.SA_OUT_P[3]*Amplitude+Offset, '.', markersize=2)
            ax2.plot( self.SA_OUT_P[4],  self.SA_OUT_P[5]*Amplitude+Offset, '.', markersize=2)
            ax2.plot( self.SA_OUT_P[6],  self.SA_OUT_P[7]*Amplitude+Offset, '-', linewidth=0.5, color='black')
            refX = self.SA_OUT_P[9]
            refY = self.y_SA_OUT[np.where(self.x_OUT > refX)[0][0]]
            ax2.plot(refX, refY, '.', markersize=5, color='#f93eed')
            ax2.set_title('OPS - SA OUT')
            ax2.set_xlabel('Time [ms]')
            ax2.set_ylabel('Amplitude [a.u]')
        except:
            pass

        try:
            Amplitude = np.max(self.y_SB_IN)
            Offset = np.min(self.y_SB_IN)
            ax3.plot(self.x_IN, self.y_SB_IN, linewidth=0.5)
            ax3.plot(self.SB_IN_P[2], self.SB_IN_P[3] * Amplitude + Offset, '.', markersize=2)
            ax3.plot(self.SB_IN_P[4], self.SB_IN_P[5] * Amplitude + Offset, '.', markersize=2)
            ax3.plot(self.SB_IN_P[6], self.SB_IN_P[7] * Amplitude + Offset, '-', linewidth=0.5, color='black')
            refX = self.SB_IN_P[9]
            refY = self.y_SB_IN[np.where(self.x_IN > refX)[0][0]]
            ax3.plot(refX, refY, '.', markersize=5, color='#f93eed')
            ax3.set_title('OPS - SB IN')
            ax3.set_xlabel('Time [ms]')
            ax3.set_ylabel('Amplitude [a.u]')
        except:
            pass

        try:
            Amplitude = np.max(self.y_SB_OUT)
            Offset = np.min(self.y_SB_OUT)
            ax4.plot(self.x_OUT, self.y_SB_OUT, linewidth=0.5)
            ax4.plot(self.SB_OUT_P[2], self.SB_OUT_P[3] * Amplitude + Offset, '.', markersize=2)
            ax4.plot(self.SB_OUT_P[4], self.SB_OUT_P[5] * Amplitude + Offset, '.', markersize=2)
            ax4.plot(self.SB_OUT_P[6], self.SB_OUT_P[7] * Amplitude + Offset, '-', linewidth=0.5, color='black')
            refX = self.SB_OUT_P[9]
            refY = self.y_SB_OUT[np.where(self.x_OUT > refX)[0][0]]
            ax4.plot(refX, refY, '.', markersize=5, color='#f93eed')
            ax4.set_title('OPS - SB OUT')
            ax4.set_xlabel('Time [ms]')
            ax4.set_ylabel('Amplitude [a.u]')
        except:
            pass

        color = ['blue','red','yellow','green']
        for i in range(0,2):
            if i ==1:
                PMT_i = [self.y_PMTA_IN, self.y_PMTB_IN, self.y_PMTC_IN, self.y_PMTD_IN]
                PMT_x = self.x_PMT_IN
                s_title = 'IN'
                ax_pmt = ax5
            else:
                PMT_i = [self.y_PMTA_OUT, self.y_PMTB_OUT, self.y_PMTC_OUT, self.y_PMTD_OUT]
                PMT_x = self.x_PMT_OUT
                s_title = 'OUT'
                ax_pmt = ax6

            for c in range(0,4):
                try:
                    PMT= PMT_i[c]
                    Fs = 1/(1e-3*(PMT_x[1]-PMT_x[0]))
                    Start = PMT_x[0]
                    PMT_f = utils.process_profile(PMT, Fs, Start, configuration.pmt_filterfreq_rawview, configuration.pmt_downsample_rawview)
                    ax_pmt.plot(PMT_f[0], PMT_f[1], color = color[c])
                except:
                    pass
                ax_pmt.set_title('PMTs ' + s_title)
                ax_pmt.set_xlabel('Time [ms]')
                ax_pmt.set_ylabel('Amplitude [mV]')

        self.fig.tight_layout()