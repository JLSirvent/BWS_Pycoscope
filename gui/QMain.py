#   --------------------------------------------------------------------------
# Copyright (c) <2018> <Jose Luis Sirvent>
# BE-BI-PM, CERN (European Organization for Nuclear Research)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#   --------------------------------------------------------------------------
#
#   Not fully documented


from __future__ import unicode_literals

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QWidget, QApplication

from picosdk import ps6000

import Configuration, DataScan, QButtonsSet, QLogDialog, utils, QTabWidgetPlotting

class QMain(QWidget):

    def __init__(self, parent=None):
        '''
        Main Widget of the window to display all the tab
        :param parent:
        '''

        super(QMain, self).__init__(parent)

        # Configuration and Data objects
        self.configuration = Configuration.Configuration()
        self.data_scan = DataScan.DataScan()
        self.ps_picoscope =  ps6000.Device()

        # Application Components
        self.setWindowTitle('LIU-BWS MD Application')

        self.Title = QLabel('LIU-BWS MD Application')
        f = QtGui.QFont('Arial', 20, QtGui.QFont.Bold)
        f.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.Title.setFont(QtGui.QFont('Arial', 20, QtGui.QFont.Bold))
        self.Title.setContentsMargins(10, 10, 10, 10)

        self.CERN_logo = QLabel()
        self.CERN_logo_image = QtGui.QPixmap(utils.resource_path("images/cern_logo.jpg"))
        self.CERN_logo_image = self.CERN_logo_image.scaledToHeight(60, QtCore.Qt.SmoothTransformation)
        self.CERN_logo.setPixmap(self.CERN_logo_image)

        self.buttons_pannel = QButtonsSet.QButtonsSet(self)
        self.LogDialog = QLogDialog.QLogDialog()
        self.plotting_tabs = QTabWidgetPlotting.QTabWidgetPlotting()

        # Application Layout
        self.header = QHBoxLayout()
        self.header.addWidget(self.Title)
        self.header.addWidget(self.CERN_logo, 0, QtCore.Qt.AlignRight)

        self.mainLayout2 = QHBoxLayout()
        self.mainLayout2.addWidget(self.buttons_pannel)
        self.mainLayout2.addWidget(self.plotting_tabs)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.header)
        self.mainLayout.addLayout(self.mainLayout2)
        self.mainLayout.addWidget(self.LogDialog)
        self.setLayout(self.mainLayout)

        # Window properties
        self.setWindowTitle('LIU-BWS MD Application')
        self.setMinimumSize(1200, 900)

        # Initialization
        self.buttons_pannel.update_file_list(self.configuration.app_datapath)
        self.buttons_pannel.set_defaults_at_startup(self.configuration)

        # Actions
        self.buttons_pannel.scope_connect_btn.clicked.connect(self.connectScope)
        self.buttons_pannel.dataset_list.itemDoubleClicked.connect(self.load_data_from_dataset)
        self.buttons_pannel.acquisition_launch_button.clicked.connect(self.acquisitions)


    def connectScope(self):
        #self.LogDialog.add('Connecting scopes...', 'info')
        status_ps = self.ps_picoscope.open_unit(self.configuration.sco_ps_pico_sn)
        #status_pmt = self.pmt_picoscope.open_unit(self.configuration.sco_pmt_pico_sn)

    def acquisitions(self):

        # Scopes configuration:
        # --------------------
        s_A, state_A = self.ps_picoscope.get_channel_state(channel=self.ps_picoscope.m.Channels.A)
        s_B, state_B = self.ps_picoscope.get_channel_state(channel=self.ps_picoscope.m.Channels.B)

        # Channel Config:
        state_A.coupling = self.ps_picoscope.m.Couplings.dc1M
        state_A.bwlimit = self.ps_picoscope.m.BWLimit.bw_20M
        state_A.enabled = True
        state_A.offset = 0
        state_A.range = self.ps_picoscope.m.Ranges.r50mv

        state_B.coupling = self.ps_picoscope.m.Couplings.dc1M
        state_B.bwlimit = self.ps_picoscope.m.BWLimit.bw_20M
        state_B.enabled = True
        state_B.offset = 0
        state_B.range = self.ps_picoscope.m.Ranges.r50mv

        status_A = self.ps_picoscope.set_channel(channel=self.ps_picoscope.m.Channels.A, state=state_A)
        status_B = self.ps_picoscope.set_channel(channel=self.ps_picoscope.m.Channels.B, state=state_B)



    def load_data_from_dataset(self,item):
        # self.LogDialog.add('Loading scan data...', 'info')
        full_file_path = self.configuration.app_datapath + '/' + item.text() + '.mat'
        self.data_scan.load_data(full_file_path)
        self.plotting_tabs.tab_raw_data.actualise(self.data_scan,self.configuration)

    def closeEvent(self, event):
        print("Closing the app")
        self.deleteLater()

def main():
    app = QApplication(sys.argv)
    ex = QMain()
    ex.move(100, 100)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()








