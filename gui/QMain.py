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
import Configuration, DataScan, QButtonsSet, QLogDialog, utils, QTabWidgetPlotting, DataCollection

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


    def connectScope(self):
        #self.LogDialog.add('Connecting scopes...', 'info')
        status_ps = self.ps_picoscope.open_unit(self.configuration.ps_pico_sn)
        status_pmt = self.pmt_picoscope.open_unit(self.configuration.pmt_pico_sn)

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

    def acquisitions(self):

        while True:
            # Scopes configuration:
            # --------------------
            # Data Collection
            Timebase_OPS = 8
            Sample_Interval_OPS = (Timebase_OPS - 4) / 0.15625
            Fs_Ops = 1/(1e-9*Sample_Interval_OPS)  # ~ 40MSPS
            MaxSamples_OPS = int(0.5*Fs_Ops)

            Timebase_PMT = 2
            Sample_Interval_PMT = (2 ** Timebase_PMT) / 5.0
            Fs_Pmt = 1/(1e-9*Sample_Interval_PMT) # ~ 1GSPS
            MaxSamples_PMT = int(0.4*Fs_Pmt)

            # Info Collection PMT:

            InRange_PMT = [float(self.buttons_pannel.acquisition_config_pmt_in_start_txt.text()),
                           float(self.buttons_pannel.acquisition_config_pmt_in_end_txt.text())]

            OutRange_PMT = [float(self.buttons_pannel.acquisition_config_pmt_out_start_txt.text()),
                            float(self.buttons_pannel.acquisition_config_pmt_out_end_txt.text())]

            PMT_Ranges = [self.buttons_pannel.scope_config_box_pmt_ch1.currentIndex() + 1,
                          self.buttons_pannel.scope_config_box_pmt_ch2.currentIndex() + 1,
                          self.buttons_pannel.scope_config_box_pmt_ch3.currentIndex() + 1,
                          self.buttons_pannel.scope_config_box_pmt_ch4.currentIndex() + 1]

            Index_Start_In_PMT = int(1e-3 * InRange_PMT[0] * Fs_Pmt)
            Samples_In_PMT = int(1e-3 * (InRange_PMT[1] - InRange_PMT[0]) * Fs_Pmt)
            Index_Start_Out_PMT = int(1e-3 * OutRange_PMT[0] * Fs_Pmt)
            Samples_Out_PMT = int(1e-3 * (OutRange_PMT[1] - OutRange_PMT[0]) * Fs_Pmt)

            BuffLen_PMT = int(1.2*1e-3*np.amax([InRange_PMT[1]-InRange_PMT[0],OutRange_PMT[1]-OutRange_PMT[0]])*Fs_Pmt)
            status_pmt_locate_buffer = [0, 0, 0, 0]

            # Info Collection OPS:

            InRange_OPS = [float(self.buttons_pannel.acquisition_config_ops_in_start_txt.text()),
                           float(self.buttons_pannel.acquisition_config_ops_in_end_txt.text())]

            OutRange_OPS = [float(self.buttons_pannel.acquisition_config_ops_out_start_txt.text()),
                            float(self.buttons_pannel.acquisition_config_ops_out_end_txt.text())]

            OPS_Ranges = [self.buttons_pannel.scope_config_box_ops_ch1.currentIndex()+1,
                          self.buttons_pannel.scope_config_box_ops_ch2.currentIndex()+1]

            Index_Start_In_OPS = int(1e-3 * InRange_OPS[0] * Fs_Ops)
            Samples_In_OPS = int(1e-3 * (InRange_OPS[1] - InRange_OPS[0]) * Fs_Ops)
            Index_Start_Out_OPS = int(1e-3 * OutRange_OPS[0] * Fs_Ops)
            Samples_Out_OPS = int(1e-3 * (OutRange_OPS[1] - OutRange_OPS[0]) * Fs_Ops)

            BuffLen_OPS = int(1.2*1e-3*np.amax([InRange_OPS[1]-InRange_OPS[0],OutRange_OPS[1]-OutRange_OPS[0]])*Fs_Ops)

            status_ps_locate_buffer = [0, 0]

            print('a')

            # Buffers preparation PMT
            data_pmt = {}
            for i in range(0,4):
                data_pmt[i] = {}
                data_pmt[i]["max"] = np.empty(BuffLen_PMT, dtype=c_int16)
            self.pmt_picoscope.release_all_buffers()

            # Buffers preparation OPS
            data_ops = {}
            for i in range(0,2):
                data_ops[i] = {}
                data_ops[i]["max"] = np.empty(BuffLen_OPS, dtype=c_int16)
            self.ps_picoscope.release_all_buffers()
            print('b')

            # Channels and data buffers configuration PMT
            for i in range(0,4):
                s_i, state_i = self.pmt_picoscope.get_channel_state(channel=i)
                # Channel Config:
                state_i.coupling = self.pmt_picoscope.m.Couplings.dc50
                state_i.bwlimit = self.pmt_picoscope.m.BWLimit.bw_full
                if PMT_Ranges[i] == 1:
                    state_i.enabled = False
                else:
                    state_i.enabled = True
                state_i.offset = 0
                state_i.range = PMT_Ranges[i]
                status_i_set_channel = self.pmt_picoscope.set_channel(channel=i, state=state_i)
                # Buffers Config:
                status_pmt_locate_buffer[i] = self.pmt_picoscope._set_data_buffers(line=i,
                                                                                   buffer_max=data_pmt[i]["max"].ctypes,
                                                                                   buffer_min=None,
                                                                                   bufflen=BuffLen_PMT,
                                                                                   segment=0,
                                                                                   mode=self.pmt_picoscope.m.RatioModes.raw)
                print(status_pmt_locate_buffer[i])

            # Channels and data buffers configuration OPS
            for i in range(0,2):
                s_i, state_i = self.ps_picoscope.get_channel_state(channel=i)
                # Channel Config:
                state_i.coupling = self.ps_picoscope.m.Couplings.dc1M
                state_i.bwlimit = self.ps_picoscope.m.BWLimit.bw_20M
                if OPS_Ranges[i] == 1:
                    state_i.enabled = False
                else:
                    state_i.enabled = True
                state_i.offset = 0
                state_i.range = OPS_Ranges[i]
                status_i_set_channel = self.ps_picoscope.set_channel(channel=i, state=state_i)
                # Buffers Config:
                status_ps_locate_buffer[i] = self.ps_picoscope._set_data_buffers(line=i,
                                                                                 buffer_max=data_ops[i]["max"].ctypes,
                                                                                 buffer_min=None,
                                                                                 bufflen=BuffLen_OPS,
                                                                                 segment=0,
                                                                                 mode=self.ps_picoscope.m.RatioModes.raw)
                print(status_ps_locate_buffer[i])
            print('c')

            # Trigger configuration of both scopes
            triggerChannel = self.ps_picoscope.m.TriggerChannels.Aux
            direction = self.ps_picoscope.m.ThresholdDirections.rising
            thresholdVoltage = 0.5
            Wait = 2000

            status_trigger = self.ps_picoscope.set_simple_trigger(enabled=True, source=triggerChannel, threshold=thresholdVoltage, direction=direction, waitfor=Wait)
            status_trigger = self.pmt_picoscope.set_simple_trigger(enabled=True, source=triggerChannel, threshold=thresholdVoltage, direction=direction, waitfor=Wait)

            print('d')

            # Arming Scopes for acquisition when trigger is generated OPS
            self.pmt_picoscope._collect_cb_type = self.pmt_picoscope._block_ready()
            self.pmt_picoscope._collect_cb_func = self.pmt_picoscope._collect_cb_type(self.pmt_picoscope._collect_cb)
            status = self.pmt_picoscope._run_block(pretrig=0, posttrig=MaxSamples_PMT, timebase=Timebase_PMT, oversample=0, ref_time=None,
                                                  segment=0, ref_cb=self.pmt_picoscope._collect_cb_func, ref_cb_param=None)
            print(status)

            # Arming Scopes for acquisition when trigger is generated PMT
            self.ps_picoscope._collect_cb_type = self.ps_picoscope._block_ready()
            self.ps_picoscope._collect_cb_func = self.ps_picoscope._collect_cb_type(self.ps_picoscope._collect_cb)
            status = self.ps_picoscope._run_block(pretrig=0, posttrig=MaxSamples_OPS, timebase=Timebase_OPS, oversample=0, ref_time=None,
                                                  segment=0, ref_cb=self.ps_picoscope._collect_cb_func, ref_cb_param=None)
            print(status)

            # Wait for trigger
            self.update_status_label('Trig...', 'red')
            self.pmt_picoscope._collect_event.wait()
            self.ps_picoscope._collect_event.wait()

            self.pmt_picoscope._collect_event.clear()
            self.ps_picoscope._collect_event.clear()

            print('e')

            self.update_status_label('Rec...', 'yellow')
            # Recover info into bufffers: OPS
            self.data_scan.PS_Factors =[self.ps_picoscope.m.Ranges.values[
                                        self.ps_picoscope._channel_set[0].range]/self.ps_picoscope.info.max_adc,
                                        self.ps_picoscope.m.Ranges.values[
                                        self.ps_picoscope._channel_set[1].range] / self.ps_picoscope.info.max_adc]
            self.data_scan.PS_Fs = Fs_Ops
            self.data_scan.PS_TimesStart = [InRange_OPS[0],OutRange_OPS[0]]

            overvoltaged = c_int16(0)
            # OPS IN
            status_read = self.ps_picoscope._get_values(start=Index_Start_In_OPS,
                                                        ref_samples=byref(c_uint32(Samples_In_OPS)),
                                                        ratio=1,
                                                        mode=self.ps_picoscope.m.RatioModes.none,
                                                        segment=0,
                                                        ref_overflow=byref(overvoltaged))

            self.data_scan.PS_PSA_IN = data_ops[0]['max'][0:Samples_In_OPS]
            self.data_scan.PS_PSB_IN = data_ops[1]['max'][0:Samples_In_OPS]

            #self.data_scan.PMT_Time_IN = np.asarray(range(Index_Start_In_OPS,Index_Start_In_OPS+Samples_In_OPS))/Fs_Ops

            print('f')

            # OPS Out
            status_read = self.ps_picoscope._get_values(start=Index_Start_Out_OPS,
                                                        ref_samples=byref(c_uint32(Samples_Out_OPS)),
                                                        ratio=1,
                                                        mode=self.ps_picoscope.m.RatioModes.none,
                                                        segment=0,
                                                        ref_overflow=byref(overvoltaged))

            self.data_scan.PS_PSA_OUT = data_ops[0]['max'][0:Samples_Out_OPS]
            self.data_scan.PS_PSB_OUT = data_ops[1]['max'][0:Samples_Out_OPS]

            #self.data_scan.PMT_Time_OUT = np.asarray(range(Index_Start_Out_OPS,Index_Start_Out_OPS+Samples_Out_OPS))/Fs_Ops

            print('g')

            # Recover info into bufffers: PMT
            self.data_scan.PMT_Factors = [self.pmt_picoscope.m.Ranges.values[
                                          self.pmt_picoscope._channel_set[0].range] / self.pmt_picoscope.info.max_adc,
                                          self.pmt_picoscope.m.Ranges.values[
                                          self.pmt_picoscope._channel_set[1].range] / self.pmt_picoscope.info.max_adc,
                                          self.pmt_picoscope.m.Ranges.values[
                                          self.pmt_picoscope._channel_set[2].range] / self.pmt_picoscope.info.max_adc,
                                          self.pmt_picoscope.m.Ranges.values[
                                          self.pmt_picoscope._channel_set[3].range] / self.pmt_picoscope.info.max_adc]

            self.data_scan.PMT_Fs = Fs_Pmt
            self.data_scan.PMT_TimesStart = [InRange_PMT[0],OutRange_PMT[0]]

            # PMT IN
            status_read = self.pmt_picoscope._get_values(start=Index_Start_In_PMT,
                                                         ref_samples=byref(c_uint32(Samples_In_PMT)),
                                                         ratio=1,
                                                         mode=self.pmt_picoscope.m.RatioModes.none,
                                                         segment=0,
                                                         ref_overflow=byref(overvoltaged))
            print(status_read)
            print('g1')
            self.data_scan.PMT_PMTA_IN = data_pmt[0]['max'][0:Samples_In_PMT]
            self.data_scan.PMT_PMTB_IN = data_pmt[1]['max'][0:Samples_In_PMT]
            self.data_scan.PMT_PMTC_IN = data_pmt[2]['max'][0:Samples_In_PMT]
            self.data_scan.PMT_PMTD_IN = data_pmt[3]['max'][0:Samples_In_PMT]

            #self.data_scan.PMT_Time_IN = np.asarray(range(Index_Start_In_PMT, Index_Start_In_PMT + Samples_In_PMT)) / Fs_Pmt

            print('h')

            # PMT Out
            status_read = self.pmt_picoscope._get_values(start=Index_Start_Out_PMT,
                                                         ref_samples=byref(c_uint32(Samples_Out_PMT)),
                                                         ratio=1,
                                                         mode=self.pmt_picoscope.m.RatioModes.none,
                                                         segment=0,
                                                         ref_overflow=byref(overvoltaged))

            self.data_scan.PMT_PMTA_OUT = data_pmt[0]['max'][0:Samples_Out_PMT]
            self.data_scan.PMT_PMTB_OUT = data_pmt[1]['max'][0:Samples_Out_PMT]
            self.data_scan.PMT_PMTC_OUT = data_pmt[2]['max'][0:Samples_Out_PMT]
            self.data_scan.PMT_PMTD_OUT = data_pmt[3]['max'][0:Samples_Out_PMT]

            #self.data_scan.PMT_Time_OUT = np.asarray(range(Index_Start_Out_PMT, Index_Start_Out_PMT + Samples_Out_PMT)) / Fs_Pmt

            # SAVE DATA IN MAT FORMAT
            # TimeStamping on file name
            self.update_status_label('Saving...', 'yellow')
            t = time.time()
            st = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H-%M-%S')
            filename = st + '.mat'
            sio.savemat(filename,
                        {'PMT_Fs': self.data_scan.PMT_Fs,
                         'PMT_Factors': self.data_scan.PMT_Factors,
                         'PMT_TimesStart': self.data_scan.PMT_TimesStart,
                         'PMT_PMTA_IN': self.data_scan.PMT_PMTA_IN,
                         'PMT_PMTB_IN': self.data_scan.PMT_PMTB_IN,
                         'PMT_PMTC_IN': self.data_scan.PMT_PMTC_IN,
                         'PMT_PMTD_IN': self.data_scan.PMT_PMTD_IN,
                         'PMT_PMTA_OUT': self.data_scan.PMT_PMTA_OUT,
                         'PMT_PMTB_OUT': self.data_scan.PMT_PMTB_OUT,
                         'PMT_PMTC_OUT': self.data_scan.PMT_PMTC_OUT,
                         'PMT_PMTD_OUT': self.data_scan.PMT_PMTD_OUT,
                         'PS_Fs': self.data_scan.PS_Fs,
                         'PS_Factors': self.data_scan.PS_Factors,
                         'PS_TimesStart': self.data_scan.PS_TimesStart,
                         'PS_PSA_IN': self.data_scan.PS_PSA_IN,
                         'PS_PSB_IN': self.data_scan.PS_PSB_IN,
                         'PS_PSA_OUT': self.data_scan.PS_PSA_OUT,
                         'PS_PSB_OUT': self.data_scan.PS_PSB_OUT},
                         do_compression = True)

            #elapsed = time.time() - t
            #print(elapsed)
            self.update_status_label('IDLE', 'green')

            QtCore.QCoreApplication.processEvents()

            # Check for Loop exit condition
            if self.buttons_pannel.acquisition_mode_single.isChecked():
                break


    def update_status_label(self,text,colour):
        self.buttons_pannel.acquisition_launch_status.setText(text)
        self.buttons_pannel.acquisition_launch_status.setStyleSheet('QLabel {background-color:'+colour+'; font: bold 14px; text-align: center;}')
        self.buttons_pannel.acquisition_launch_status.repaint()

    def load_data_from_dataset(self,item):
        # self.LogDialog.add('Loading scan data...', 'info')
        full_file_path = self.configuration.app_datapath + '/' + item.text().split('   ')[1] + '.mat'
        self.data_scan.load_data_v2(full_file_path)
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








