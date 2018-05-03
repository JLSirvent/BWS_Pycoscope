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
import Configuration, DataScan, QButtonsSet, QLogDialog, utils, QTabWidgetPlotting, DataCollection, DataCollection_VFC, DataScan_Processed, QTabWidgetButtons, FESAControlsUpdater

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

        #self.buttons_pannel = QButtonsSet.QButtonsSet(self)
        self.tab_buttons_pannel = QTabWidgetButtons.QTabWidgetButtons(self)
        self.LogDialog = QLogDialog.QLogDialog()
        self.plotting_tabs = QTabWidgetPlotting.QTabWidgetPlotting()

        # Application Layout
        self.header = QHBoxLayout()
        self.header.addWidget(self.Title)
        self.header.addWidget(self.CERN_logo, 0, QtCore.Qt.AlignRight)

        self.mainLayout2 = QHBoxLayout()
        self.mainLayout2.addWidget(self.tab_buttons_pannel)
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
        self.tab_buttons_pannel.buttons_pannel.update_file_list(self.configuration.app_datapath)
        self.tab_buttons_pannel.buttons_pannel.set_defaults_at_startup(self.configuration)
        self.tab_buttons_pannel.buttons_pannel_config.set_defaults_at_startup(self.configuration)

        # Actions

        # Scope
        self.tab_buttons_pannel.buttons_pannel.scope_connect_btn.clicked.connect(self.connectScope)
        self.tab_buttons_pannel.buttons_pannel.dataset_list.itemDoubleClicked.connect(self.load_data_from_dataset)
        self.tab_buttons_pannel.buttons_pannel.acquisition_launch_button.clicked.connect(self.acquisitions_thread)

        # HV
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ONOFF.clicked.connect(self.HV_ONOFF)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ControlV_txt.editingFinished.connect(self.FESAEditText)

        # FW
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_ONOFF.clicked.connect(self.FW_ONOFF)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_DoHome.clicked.connect(self.FW_HOME)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Position_set.currentIndexChanged.connect(self.FESAEditText)

        # LTIM
        self.tab_buttons_pannel.buttons_pannel.cycle_selector_LTIM_ONOFF.clicked.connect(self.LTIM_ONOFF)
        self.tab_buttons_pannel.buttons_pannel.cycle_selector_dly_txt.editingFinished.connect(self.FESAEditText)
        self.tab_buttons_pannel.buttons_pannel.cycle_selector_combo.currentIndexChanged.connect(self.FESAEditText)

        # Changes on textbox update configuration
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_in_start_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_in_end_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_out_start_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_out_end_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_start_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_end_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_start_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_end_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_ref_txt.editingFinished.connect(self.updateconfiguration)
        self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_ref_txt.editingFinished.connect(self.updateconfiguration)

        # FESA Controls Updater
        #self.controls_update = FESAControlsUpdater.FESAControlsUpdater(tab_buttons_pannel = self.tab_buttons_pannel)
        #self.controls_update.start()


    def connectScope(self):

        if self.tab_buttons_pannel.buttons_pannel.scope_connect_status.text() == 'OFF':
            status_ps = self.ps_picoscope.open_unit(self.configuration.ps_pico_sn)
            status_pmt = self.pmt_picoscope.open_unit(self.configuration.pmt_pico_sn)
            if status_ps == 0 & status_pmt == 0:
                self.tab_buttons_pannel.buttons_pannel.scope_connect_status.setText('ON')
                self.tab_buttons_pannel.buttons_pannel.scope_connect_status.setStyleSheet(
                'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                self.tab_buttons_pannel.buttons_pannel.scope_connect_status.repaint()
        else:
            status_ps = self.ps_picoscope.close_unit()
            status_pmt = self.pmt_picoscope.close_unit()
            if status_ps == 0 & status_pmt == 0:
                self.tab_buttons_pannel.buttons_pannel.scope_connect_status.setText('OFF')
                self.tab_buttons_pannel.buttons_pannel.scope_connect_status.setStyleSheet(
                'QLabel {background-color: red; font: bold 14px; text-align: center;}')
                self.tab_buttons_pannel.buttons_pannel.scope_connect_status.repaint()


    def acquisitions_thread(self):
        self.data_collection = DataCollection_VFC.DataCollection_VFC(configuration=self.configuration,
                                                             data_scan=self.data_scan,
                                                             tab_buttons_pannel=self.tab_buttons_pannel,
                                                             ps_picoscope=self.ps_picoscope,
                                                             pmt_picoscope=self.pmt_picoscope,
                                                             plotting_tabs=self.plotting_tabs,
                                                             data_scan_processed=self.data_scan_processed)

        self.data_collection.notifyState.connect(self.onState)
        self.data_collection.fileReady.connect(self.onFileReady)
        self.data_collection.start()

    def onState(self, state):
        col = 'green'
        if state == 'IDLE':
            col = 'green'
        if state == 'Trig...':
            col = 'red'
        if state == 'Rec...' or state == 'Saving...' or state == 'Process..' or state == 'Plotting':
            col = 'yellow'

        self.update_status_label(text=state, colour = col)

    def onFileReady(self,filename):
        self.tab_buttons_pannel.buttons_pannel.update_file_list(self.configuration.app_datapath)

    def update_status_label(self,text,colour):
        self.tab_buttons_pannel.buttons_pannel.acquisition_launch_status.setText(text)
        self.tab_buttons_pannel.buttons_pannel.acquisition_launch_status.setStyleSheet('QLabel {background-color:'+colour+'; font: bold 14px; text-align: center;}')
        self.tab_buttons_pannel.buttons_pannel.acquisition_launch_status.repaint()

    def load_data_from_dataset(self,item):
        # self.LogDialog.add('Loading scan data...', 'info')
        full_file_path = self.configuration.app_datapath + '/' + item.text().split('   ')[1] + '.mat'

        self.data_scan.load_data_v2(full_file_path)

        try:
            title = self.data_scan.InfoData_CycleStamp + ' ' + self.data_scan.InfoData_CycleName + ' AcqDly: ' + str(self.data_scan.InfoData_AcqDelay) + 'ms'
        except:
            title = ''

        if self.tab_buttons_pannel.buttons_pannel.updater_raw.isChecked() | self.tab_buttons_pannel.buttons_pannel.updater_motion.isChecked() | self.tab_buttons_pannel.buttons_pannel.updater_profile.isChecked() | self.tab_buttons_pannel.buttons_pannel.updater_rds.isChecked():

            self.data_scan_processed.process_data(self.data_scan, self.configuration)

            if self.tab_buttons_pannel.buttons_pannel.updater_raw.isChecked():
                self.plotting_tabs.tab_raw_data.actualise(self.data_scan,self.data_scan_processed,self.configuration)

            if self.tab_buttons_pannel.buttons_pannel.updater_motion.isChecked():
                self.plotting_tabs.tab_motion_data.actualise(self.data_scan_processed)

            if self.tab_buttons_pannel.buttons_pannel.updater_profile.isChecked():
                self.plotting_tabs.tab_processed_profiles.actualise(X_IN=self.data_scan_processed.PS_POSA_IN_Proj,
                                                                    X_OUT=self.data_scan_processed.PS_POSA_OUT_Proj,
                                                                    Y_IN=self.data_scan_processed.PMT_IN,
                                                                    Y_OUT=self.data_scan_processed.PMT_OUT,
                                                                    Imax_IN=self.data_scan_processed.PMT_IN_Imax,
                                                                    Imax_OUT=self.data_scan_processed.PMT_OUT_Imax,
                                                                    Qtot_IN=self.data_scan_processed.PMT_IN_Qtot,
                                                                    Qtot_OUT=self.data_scan_processed.PMT_OUT_Qtot,
                                                                    stitleinfo=title)

            if self.tab_buttons_pannel.buttons_pannel.updater_rds.isChecked():
                self.plotting_tabs.tab_rds_data.actualise(self.data_scan_processed,self.configuration)

    def updateconfiguration(self):
        self.configuration.def_ops_in_start = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_start_txt.text())
        self.configuration.def_ops_in_end = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_end_txt.text())
        self.configuration.def_ops_in_ref = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_ref_txt.text())
        self.configuration.def_ops_out_start = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_start_txt.text())
        self.configuration.def_ops_out_end = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_end_txt.text())
        self.configuration.def_ops_out_ref = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_ref_txt.text())

        self.configuration.def_pmt_in_start = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_in_start_txt.text())
        self.configuration.def_pmt_in_end = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_in_end_txt.text())
        self.configuration.def_pmt_out_start = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_out_start_txt.text())
        self.configuration.def_pmt_out_end = float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_out_end_txt.text())

    def closeEvent(self, event):
        print("Closing the app")
        self.deleteLater()

    def HV_ONOFF(self):
        FESAControlsUpdater.SendFESAcommands(tab_buttons_pannel=self.tab_buttons_pannel, action='HV_ONOFF')

    def FW_ONOFF(self):
        FESAControlsUpdater.SendFESAcommands(tab_buttons_pannel=self.tab_buttons_pannel, action='FW_ONOFF')

    def LTIM_ONOFF(self):
        FESAControlsUpdater.SendFESAcommands(tab_buttons_pannel=self.tab_buttons_pannel, action='LTIM_ONOFF')

    def FW_HOME(self):
        FESAControlsUpdater.SendFESAcommands(tab_buttons_pannel=self.tab_buttons_pannel, action='FW_DoHome')

    def FESAEditText(self):
        print('hi!')
        FESAControlsUpdater.SendFESAcommands(tab_buttons_pannel=self.tab_buttons_pannel, action='')

def main():
    app = QApplication(sys.argv)
    ex = QMain()
    ex.move(100, 100)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()








