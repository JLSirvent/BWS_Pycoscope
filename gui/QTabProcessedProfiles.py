from __future__ import unicode_literals

import numpy as np
import mplCanvas


from PyQt5 import QtCore
from scipy.optimize import curve_fit
from scipy.stats import chisquare,chi2
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

    def actualise(self, X_IN, X_OUT, Y_IN, Y_OUT, stitleinfo,Imax_IN, Imax_OUT, Qtot_IN, Qtot_OUT):
        self.plot.fig.clear()
        self.plot.X_IN  = X_IN
        self.plot.Y_IN  = Y_IN
        self.plot.X_OUT = X_OUT
        self.plot.Y_OUT = Y_OUT
        self.plot.Qtot_OUT = Qtot_OUT
        self.plot.Qtot_IN = Qtot_IN
        self.plot.Imax_OUT = Imax_OUT
        self.plot.Imax_IN = Imax_IN
        self.plot.stitleinfo = stitleinfo
        self.plot.compute_initial_figure()
        self.plot.draw()

class plot(mplCanvas.mplCanvas):

    def __init__(self, parent, width, height, dpi):

        self.X_IN = [np.ones(200),np.ones(200),np.ones(200),np.ones(200)]
        self.Y_IN = [np.ones(4), np.ones(200), np.ones(200)]
        self.X_OUT = [np.ones(200),np.ones(200), np.ones(200),np.ones(200)]
        self.Y_OUT = [np.ones(4), np.ones(200), np.ones(200)]
        self.Imax_OUT = [0, 0, 0, 0]
        self.Imax_IN =  [0, 0, 0, 0]
        self.Qtot_IN =  [0, 0, 0, 0]
        self.Qtot_OUT =  [0, 0, 0, 0]
        self.stitleinfo = ' '
        super(plot, self).__init__(parent, width, height, dpi)

    def compute_initial_figure(self):

        self.fig.clear()
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        col = ['blue', 'red', 'green', 'yellow']

        for i in range(0,2):
            if i == 0:
                x = self.X_IN
                y = self.Y_IN
                Imax = self.Imax_IN
                Qtot = self.Qtot_IN
                s_title = 'IN'
                ax = ax1
            else:
                x = self.X_OUT
                y = self.Y_OUT
                Imax = self.Imax_OUT
                Qtot = self.Qtot_OUT
                s_title = 'OUT'
                ax = ax2

            def gauss(x, *p):
                a, b, c, d = p
                y = a * np.exp(-np.power((x - b), 2.) / (2. * c ** 2.)) + d

                return y
            for c in range(0,4):
                try:
                    _x = np.asarray(x[c][1])
                    _y = np.asarray(y[c][1])
                    a = np.max(_y) - np.min(_y)
                    mean = _x[np.where(_y == np.max(_y))[0]]
                    sigma = 1
                    o = np.min(_y)

                    try:
                        popt, pcov = curve_fit(gauss, _x, _y, p0=[a, mean, sigma, o])
                        fit_y = gauss(_x, *popt)

                        # Goodness of FIT
                        ss_res = np.sum((_y - fit_y) ** 2)
                        ss_tot = np.sum((_y - np.mean(_y)) ** 2)
                        r_squared = 1 - (ss_res / ss_tot)

                        # Normalized data for all channels
                        _ynorm = _y*np.max(_y)**-1
                        fit_ynorm = fit_y*np.max(_y)**-1
                        baseline = np.min(fit_ynorm)

                        rmse = 10000*(_ynorm.size)**-1 * np.sum((_ynorm-fit_ynorm)**2)
                        # if baseline < 0:
                        X2 = chisquare(f_obs=_ynorm-baseline+0.1, f_exp=fit_ynorm-baseline+0.1)

                        # else:
                        # X2 = chisquare(f_obs=_ynorm, f_exp=fit_ynorm)

                        #X2[0] = X2[0] * len(_ynorm)**-1
                        #print(X2[0])
                        ax.plot(_x, _y, color=col[c], label ='CH' + str(c+1) + r' $\sigma$:{0:.2f}'.format(popt[2])+ 'mm' + r' $\mu$:{0:.2f}'.format(popt[1]) + 'mm\nX2:{0:.2f} '.format(X2[0]) + ' RMSE:{:.1f} '.format(rmse) +'R2:{:.3f}'.format(r_squared)+ '\nImax:{0:.1f}'.format(Imax[c])+ 'uA Qtot:{0:.1f}'.format(Qtot[c]) + 'nC')
                        ax.plot(_x,fit_y,color ='black')
                        #if c==0:
                        #   ax.set_xlim(popt[1]-6*popt[2],popt[1]+6*popt[2])
                    except:
                        ax.plot(_x, _y, color=col[c], label='CH' + str(c + 1) + ' Fit Error' + '\nImax:{0:.1f}'.format(Imax[c])+ 'uA Qtot:{0:.1f}'.format(Qtot[c]) + 'nC')
                except:
                    print('Error showing fancy plot!')

            ax.legend(loc='upper right')
            ax.set_title('Beam profile - ' + s_title + ' ' + self.stitleinfo)
            ax.set_xlabel('Position [mm]')
            ax.set_ylabel('Amplitude [a.u]')

        self.fig.tight_layout()