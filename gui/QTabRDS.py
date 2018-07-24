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

        self.Threshold = np.ones(3)

        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self):

        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)

        try:

            for i in range(0,2):
                if i==0:
                    ax = ax1
                    Scan = 'IN'
                    TimesA = self.TimesAIn
                    TimesB = self.TimesBIn
                    Tlim = 50
                else:
                    ax = ax2
                    Scan = 'OUT'
                    TimesA = self.TimesAOut
                    TimesB = self.TimesBOut
                    Tlim = 410

                offset = 100

                DistancesA = np.diff(TimesA[offset:TimesA.size - 1 - offset])
                DistancesB = np.diff(TimesB[offset:TimesB.size - 1 - offset])

                #RDS_A = np.divide(DistancesA[previous_periods:DistancesA.size], DistancesA[0:DistancesA.size - 1])
                #RDS_B = np.divide(DistancesB[previous_periods:DistancesB.size], DistancesB[0:DistancesB.size - 1])

                previous_periods = 4
                DistancesA_norm = []
                DistancesB_norm = []

                for i in range(previous_periods,DistancesA.size):
                    DistancesA_norm.append(np.mean(DistancesA[i-previous_periods:i]))
                for i in range(previous_periods,DistancesB.size):
                    DistancesB_norm.append(np.mean(DistancesB[i-previous_periods:i]))

                RDS_A = np.asarray(np.divide(DistancesA[previous_periods:DistancesA.size], DistancesA_norm))
                RDS_B = np.asarray(np.divide(DistancesB[previous_periods:DistancesB.size], DistancesB_norm))

                RDS_A = RDS_A[np.where(TimesA[0:len(RDS_A)]<Tlim)[0]]
                RDS_B = RDS_B[np.where(TimesB[0:len(RDS_B)]<Tlim)[0]]

                SSL_A = len(np.where((RDS_A>self.Threshold[0])&(RDS_A<self.Threshold[1]))[0])
                DSL_A = len(np.where((RDS_A>self.Threshold[1])&(RDS_A<self.Threshold[2]))[0])
                TSL_A = len(np.where(RDS_A>self.Threshold[2])[0])

                SSL_B = len(np.where((RDS_B>self.Threshold[0])&(RDS_B<self.Threshold[1]))[0])
                DSL_B = len(np.where((RDS_B>self.Threshold[1])&(RDS_B<self.Threshold[2]))[0])
                TSL_B = len(np.where(RDS_B>self.Threshold[2])[0])

                STD_A = np.std(RDS_A[(RDS_A>0.85)&(RDS_A<1.1)])
                STD_B = np.std(RDS_B[(RDS_B>0.85)&(RDS_B<1.1)])

                print(STD_A)

                ax.axhspan(self.Threshold[1], self.Threshold[0], color='black', alpha=0.1)
                ax.axhspan(self.Threshold[2], self.Threshold[1], color='red', alpha=0.1)

                ax.plot(TimesA[0:len(RDS_A)], RDS_A, '.', color='blue', label = 'Sensor A - Total: ' + str(len(RDS_A)) + ' SSL:' +str(SSL_A)+ ' DSL:' + str(DSL_A)+' TSL:' + str(TSL_A) +' STD_Pitch:{:.2f}'.format(100*STD_A) + '%' )
                ax.plot(TimesB[0:len(RDS_B)], RDS_B, '.', color='red', label = 'Sensor B - Total: ' + str(len(RDS_B)) + ' SSL:' +str(SSL_B)+ ' DSL:' + str(DSL_B)+' TSL:' + str(TSL_B) + ' STD_Pitch:{:.2f}'.format(100*STD_B) + '%' )
                ax.set_ylim(0.6,1.4)
                ax.set_title('Relative Distance Signature - ' + Scan)
                ax.set_xlabel('Time [ms]')
                ax.set_ylabel('RDS')
                ax.legend()
        except:
            pass

        self.fig.tight_layout()