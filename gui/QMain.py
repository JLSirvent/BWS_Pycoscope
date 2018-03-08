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
import time
import datetime
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import Configuration, DataScan, QButtonsSet, QLogDialog, utils, QTabWidgetPlotting, DataCollection, DataScan_Processed

from ctypes import *
from picosdk import ps6000
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QWidget, QApplication


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
        self.data_scan_processed = DataScan_Processed.DataScan_Processed()

        self.ps_picoscope =  ps6000.Device()
        self.pmt_picoscope =  ps6000.Device()

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
        self.buttons_pannel.acquisition_launch_button.clicked.connect(self.acquisitions_thread)

        # Changes on textbox update configuration
        self.buttons_pannel.acquisition_config_pmt_in_start_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_pmt_in_end_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_pmt_out_start_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_pmt_out_end_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_ops_in_start_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_ops_in_end_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_ops_out_start_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_ops_out_end_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_ops_in_ref_txt.editingFinished.connect(self.updateconfiguration)
        self.buttons_pannel.acquisition_config_ops_out_ref_txt.editingFinished.connect(self.updateconfiguration)



    def connectScope(self):

        if self.buttons_pannel.scope_connect_status.text() == 'OFF':
            status_ps = self.ps_picoscope.open_unit(self.configuration.ps_pico_sn)
            status_pmt = self.pmt_picoscope.open_unit(self.configuration.pmt_pico_sn)
            if status_ps == 0 & status_pmt == 0:
                self.buttons_pannel.scope_connect_status.setText('ON')
                self.buttons_pannel.scope_connect_status.setStyleSheet(
                'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                self.buttons_pannel.scope_connect_status.repaint()
        else:
            status_ps = self.ps_picoscope.close_unit()
            status_pmt = self.pmt_picoscope.close_unit()
            if status_ps == 0 & status_pmt == 0:
                self.buttons_pannel.scope_connect_status.setText('OFF')
                self.buttons_pannel.scope_connect_status.setStyleSheet(
                'QLabel {background-color: red; font: bold 14px; text-align: center;}')
                self.buttons_pannel.scope_connect_status.repaint()


    def acquisitions_thread(self):
        self.data_collection = DataCollection.DataCollection(configuration = self.configuration,
                                                             data_scan=self.data_scan,
                                                             buttons_pannel=self.buttons_pannel,
                                                             ps_picoscope=self.ps_picoscope,
                                                             pmt_picoscope=self.pmt_picoscope)

        self.data_collection.notifyState.connect(self.onState)
        self.data_collection.fileReady.connect(self.onFileReady)
        self.data_collection.start()

    def onState(self, state):
        col = 'green'
        if state == 'IDLE':
            col = 'green'
        if state == 'Trig...':
            col = 'red'
        if state == 'Rec...':
            col = 'yellow'
        if state == 'Saving...':
            col = 'yellow'
        self.update_status_label(text=state, colour = col)

    def onFileReady(self,filename):
        self.buttons_pannel.update_file_list(self.configuration.app_datapath)

    def update_status_label(self,text,colour):
        self.buttons_pannel.acquisition_launch_status.setText(text)
        self.buttons_pannel.acquisition_launch_status.setStyleSheet('QLabel {background-color:'+colour+'; font: bold 14px; text-align: center;}')
        self.buttons_pannel.acquisition_launch_status.repaint()

    def load_data_from_dataset(self,item):
        # self.LogDialog.add('Loading scan data...', 'info')
        full_file_path = self.configuration.app_datapath + '/' + item.text().split('   ')[1] + '.mat'
        self.data_scan.load_data(full_file_path)
        self.data_scan_processed.process_data(self.data_scan,self.configuration)
        #self.plotting_tabs.tab_raw_data.actualise(self.data_scan,self.data_scan_processed,self.configuration)
        #self.plotting_tabs.tab_motion_data.actualise(self.data_scan_processed)

        self.plotting_tabs.tab_processed_profiles.actualise(X_IN = self.data_scan_processed.PS_POSA_IN_Proj,
                                                            X_OUT = self.data_scan_processed.PS_POSA_OUT_Proj,
                                                            Y_IN = self.data_scan_processed.PMT_IN,
                                                            Y_OUT = self.data_scan_processed.PMT_OUT)

    def updateconfiguration(self):
        self.configuration.def_ops_in_start = float(self.buttons_pannel.acquisition_config_ops_in_start_txt.text())
        self.configuration.def_ops_in_end = float(self.buttons_pannel.acquisition_config_ops_in_end_txt.text())
        self.configuration.def_ops_in_ref = float(self.buttons_pannel.acquisition_config_ops_in_ref_txt.text())
        self.configuration.def_ops_out_start = float(self.buttons_pannel.acquisition_config_ops_out_start_txt.text())
        self.configuration.def_ops_out_end = float(self.buttons_pannel.acquisition_config_ops_out_end_txt.text())
        self.configuration.def_ops_out_ref = float(self.buttons_pannel.acquisition_config_ops_out_ref_txt.text())

        self.configuration.def_pmt_in_start = float(self.buttons_pannel.acquisition_config_pmt_in_start_txt.text())
        self.configuration.def_pmt_in_end = float(self.buttons_pannel.acquisition_config_pmt_in_end_txt.text())
        self.configuration.def_pmt_out_start = float(self.buttons_pannel.acquisition_config_pmt_out_start_txt.text())
        self.configuration.def_pmt_out_end = float(self.buttons_pannel.acquisition_config_pmt_out_end_txt.text())

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








