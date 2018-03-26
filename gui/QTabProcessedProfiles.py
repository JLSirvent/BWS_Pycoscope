from __future__ import unicode_literals

import numpy as np
import mplCanvas


from PyQt5 import QtCore
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
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

        self.setLayout(main_layout)

    def actualise(self, X_IN, X_OUT, Y_IN, Y_OUT, stitleinfo):
        self.plot.fig.clear()
        self.plot.X_IN  = X_IN
        self.plot.Y_IN  = Y_IN
        self.plot.X_OUT = X_OUT
        self.plot.Y_OUT = Y_OUT
        self.plot.stitleinfo = stitleinfo
        self.plot.compute_initial_figure()
        self.plot.draw()

class plot(mplCanvas.mplCanvas):

    def __init__(self, parent, width, height, dpi):

        self.X_IN = [np.ones(200),np.ones(200)]
        self.Y_IN = [np.ones(4), np.ones(200), np.ones(200)]
        self.X_OUT = [np.ones(200),np.ones(200)]
        self.Y_OUT = [np.ones(4), np.ones(200), np.ones(200)]
        self.stitleinfo = ' '
        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self):

        self.fig.clear()
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        col = ['blue', 'red', 'yellow', 'green']

        for i in range(0,2):
            if i == 0:
                x = self.X_IN
                y = self.Y_IN
                s_title = 'IN'
                ax = ax1
            else:
                x = self.X_OUT
                y = self.Y_OUT
                s_title = 'OUT'
                ax = ax2

            def gauss(x, *p):
                a, b, c, d = p
                y = a * np.exp(-np.power((x - b), 2.) / (2. * c ** 2.)) + d

                return y
            for c in range(0,4):
                try:
                    _x = 1e3 * np.asarray(x[1])
                    _y = np.asarray(y[c][1])
                    a = np.max(_y) - np.min(_y)
                    mean = _x[np.where(_y == np.max(_y))[0]]
                    sigma = 50
                    o = np.min(_y)
                    try:
                        popt, pcov = curve_fit(gauss, _x, _y, p0=[a, mean, sigma, o])
                        ax.plot(_x, _y, color=col[c], label ='CH' + str(c+1) + r' $\sigma$:{0:.2f}'.format(popt[2])+ 'um' + r' $\mu$:{0:.2f}'.format(popt[1]) + 'um')
                        ax.plot(_x,gauss(_x,*popt),color ='black')
                    except:
                        ax.plot(_x, _y, color=col[c], label='CH' + str(c + 1) + ' Fit Error')
                except:
                    pass

            ax.legend(loc='upper right')
            ax.set_title('Beam profile - ' + s_title + '\n' + self.stitleinfo)
            ax.set_xlabel('Position [mm]')
            ax.set_ylabel('Amplitude [a.u]')

        self.fig.tight_layout()