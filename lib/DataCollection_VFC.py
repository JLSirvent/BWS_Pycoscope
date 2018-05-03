from __future__ import unicode_literals

import time
import datetime
import numpy as np
import scipy.io as sio
import FESAControlsUpdater
import copy

from ctypes import *
from PyQt5 import QtCore
import matplotlib.pyplot as plt

import sys
import socket


class DataCollection_VFC(QtCore.QThread):

    notifyState = QtCore.pyqtSignal(str)
    fileReady = QtCore.pyqtSignal(str)

    def __init__(self, configuration, data_scan, data_scan_processed, pmt_picoscope, ps_picoscope, tab_buttons_pannel, plotting_tabs, parent=None):

        self.configuration = configuration
        self.tab_buttons_pannel = tab_buttons_pannel
        self.ps_picoscope = ps_picoscope
        self.pmt_picoscope =pmt_picoscope
        self.data_scan = data_scan
        self.plotting_tabs = plotting_tabs
        self.data_scan_processed = data_scan_processed

        super(DataCollection_VFC, self).__init__(parent)

    def run(self):
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

            InRange_PMT = [float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_in_start_txt.text()),
                           float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_in_end_txt.text())]


            OutRange_PMT = [float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_out_start_txt.text()),
                            float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_pmt_out_end_txt.text())]


            # Info Collection OPS:

            InRange_OPS = [float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_start_txt.text()),
                           float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_in_end_txt.text())]

            OutRange_OPS = [float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_start_txt.text()),
                            float(self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_ops_out_end_txt.text())]


            # Wait for trigger
            self.notifyState.emit('Trig...')
                # Enable LTIM Output
            try:
                FESAControlsUpdater.SendFESAcommands(self.tab_buttons_pannel, action='LTIM_ON')
            except:
                print('Cannot Switch-ON LTIM!')

            # Disable LTIM Output
            try:
                FESAControlsUpdater.SendFESAcommands(self.tab_buttons_pannel, action='LTIM_OFF')
            except:
                print('Cannot Switch-OFF LTIM!')

            self.notifyState.emit('Rec...')

            t = time.time()
            # Recover info into bufffers: PMT
            self.data_scan.PMT_Factors = [1,1,1,1]
            self.data_scan.PMT_Fs = 650e6
            self.data_scan.PMT_TimesStart = [InRange_PMT[0],OutRange_PMT[0]]

            # Recover PMT IN
            self.data_scan.PMT_PMTA_IN = self.RecoverData(type=0, board=0, channel=0, timeStart_ms=InRange_PMT[0],
                                                          timeEnd_ms=InRange_PMT[1], decimate=1, unfreeze=0)
            self.data_scan.PMT_PMTB_IN = self.RecoverData(type=0, board=0, channel=1, timeStart_ms=InRange_PMT[0],
                                                          timeEnd_ms=InRange_PMT[1], decimate=1, unfreeze=0)
            self.data_scan.PMT_PMTC_IN = self.RecoverData(type=0, board=1, channel=0, timeStart_ms=InRange_PMT[0],
                                                          timeEnd_ms=InRange_PMT[1], decimate=1, unfreeze=0)
            self.data_scan.PMT_PMTD_IN = self.RecoverData(type=0, board=1, channel=1, timeStart_ms=InRange_PMT[0],
                                                          timeEnd_ms=InRange_PMT[1], decimate=1, unfreeze=0)
            # Recover PMT out
            self.data_scan.PMT_PMTA_OUT = self.RecoverData(type=0, board=0, channel=0, timeStart_ms=OutRange_PMT[0],
                                                          timeEnd_ms=OutRange_PMT[1], decimate=1, unfreeze=0)
            self.data_scan.PMT_PMTB_OUT = self.RecoverData(type=0, board=0, channel=1, timeStart_ms=OutRange_PMT[0],
                                                          timeEnd_ms=OutRange_PMT[1], decimate=1, unfreeze=0)
            self.data_scan.PMT_PMTC_OUT = self.RecoverData(type=0, board=1, channel=0, timeStart_ms=OutRange_PMT[0],
                                                          timeEnd_ms=OutRange_PMT[1], decimate=1, unfreeze=0)
            self.data_scan.PMT_PMTD_OUT = self.RecoverData(type=0, board=1, channel=1, timeStart_ms=OutRange_PMT[0],
                                                          timeEnd_ms=OutRange_PMT[1], decimate=1, unfreeze=0)

            # Recover info into bufffers: OPS
            self.data_scan.PS_Factors = [1,1]
            self.data_scan.PS_Fs = 40e6
            self.data_scan.PS_TimesStart = [InRange_OPS[0],OutRange_OPS[0]]

            # Recover OPS IN

            self.data_scan.PS_PSA_IN = self.RecoverData(type=0, board=0, channel=0, timeStart_ms=InRange_OPS[0],
                                                          timeEnd_ms=InRange_OPS[1], decimate=17, unfreeze=0)
            self.data_scan.PS_PSB_IN = self.RecoverData(type=0, board=0, channel=1, timeStart_ms=InRange_OPS[0],
                                                          timeEnd_ms=InRange_OPS[1], decimate=17, unfreeze=0)

            # OPS Out
            self.data_scan.PS_PSA_OUT = self.RecoverData(type=0, board=0, channel=0, timeStart_ms=OutRange_OPS[0],
                                                          timeEnd_ms=OutRange_OPS[1], decimate=17, unfreeze=0)
            self.data_scan.PS_PSB_OUT = self.RecoverData(type=0, board=0, channel=1, timeStart_ms=OutRange_OPS[0],
                                                          timeEnd_ms=OutRange_OPS[1], decimate=17, unfreeze=1)

            # Last recovery unfreezes vfc buffers

            # SAVE DATA IN MAT FORMAT
            # TimeStamping on file name
            self.updateinfodata()

            self.notifyState.emit('Saving...')
            st = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H-%M-%S')
            filename = self.configuration.app_datapath + '/' + st + '.mat'

            sio.savemat(filename,
                        {'InfoData_Filter_PRO': self.data_scan.InfoData_Filter_PRO,
                         'InfoData_HV': self.data_scan.InfoData_HV,
                         'InfoData_AcqDelay': self.data_scan.InfoData_AcqDelay,
                         'InfoData_CycleName': self.data_scan.InfoData_CycleName,
                         'InfoData_CycleStamp': self.data_scan.InfoData_CycleStamp,
                         'InfoData_TimeStamp': self.data_scan.InfoData_TimeStamp,
                         'PMT_Fs': self.data_scan.PMT_Fs,
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
            # Note: With data compression TRUE time ~ 6.5seg, without data compresion time ~ 0.5seg

            self.fileReady.emit(filename)

            # Plotting stuff:
            if self.tab_buttons_pannel.buttons_pannel.updater_raw.isChecked() | self.tab_buttons_pannel.buttons_pannel.updater_motion.isChecked() | self.tab_buttons_pannel.buttons_pannel.updater_profile.isChecked():
                self.notifyState.emit('Process..')
                self.data_scan_processed.process_data(self.data_scan, self.configuration)

                try:
                    title = self.data_scan.InfoData_CycleStamp + ' ' + self.data_scan.InfoData_CycleName + ' AcqDly: ' + str(
                        self.data_scan.InfoData_AcqDelay) + 'ms'
                except:
                    title = ''

                self.notifyState.emit('Plotting')
                if self.tab_buttons_pannel.buttons_pannel.updater_raw.isChecked():
                    self.plotting_tabs.tab_raw_data.actualise(self.data_scan, self.data_scan_processed, self.configuration)

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

            # Print timer value to check how long data recovery,  storage and plotting (if selected) need
            elapsed = time.time() - t
            print('Acquisisitoin elapsed time: ' + str(elapsed) + 'sec.')

            self.notifyState.emit('IDLE')
            # Check for Loop exit condition
            if self.tab_buttons_pannel.buttons_pannel.acquisition_mode_single.isChecked():
                break

    def updateinfodata(self):
        try:

            path1 = 'H:/user/j/jsirvent/Work/MD_Scripts/PSB/Auto_Script/test_g.mat'
            path2 = 'H:/user/j/jsirvent/Work/MD_Scripts/PSB/Auto_Script/test_ts.mat'

            data1 = sio.loadmat(path1, struct_as_record=False, squeeze_me=True)
            data2 = sio.loadmat(path2, struct_as_record=False, squeeze_me=True)

            self.data_scan.InfoData_Filter_PRO = data1['FW_POSITION_GET']
            self.data_scan.InfoData_HV = data1['HV_VOLTAGE_GET']
            self.data_scan.InfoData_AcqDelay = data1['LTIM_ACQDELAY_GET']
            self.data_scan.InfoData_CycleName = data2['LTIM_CYCLESTAMP']
            self.data_scan.InfoData_TimeStamp = data2['LTIM_TIMESTAMP']
            self.data_scan.InfoData_CycleStamp = data2['LTIM_CYCLENAME']

        except:
            print('Error updating InfoData')

    # Function to retrieve data from Server application running on FEC cfv-865-bwsdev
    def RecoverData(self, type, board, channel, timeStart_ms, timeEnd_ms, decimate, unfreeze):
        fs = 650e6
        total_pages = 2048
        registers_per_page = 65536

        samples_per_page = 2 * registers_per_page
        bytes_per_register = 4
        MyCommand = np.arange(8, dtype=np.uint8)

        PageEnd = total_pages - int(round(1e-3 * timeStart_ms / (samples_per_page / fs)))
        PageStart = total_pages - int(round(1e-3 * timeEnd_ms / (samples_per_page / fs)))

        Pages = np.uint16(PageEnd - PageStart)
        PageStart = np.uint16(PageStart)

        if type == 1:
            registers_per_page = 8162

        print(
        'Reading memory \nPageStart: {}, PageEnd:{}, TotalPages:{}'.format(PageStart, PageEnd, PageEnd - PageStart))
        MyCommand[7] = unfreeze
        MyCommand[6] = type
        MyCommand[5] = board
        MyCommand[4] = channel
        MyCommand[3] = (PageStart >> 8)
        MyCommand[2] = PageStart
        MyCommand[1] = (Pages >> 8)
        MyCommand[0] = Pages

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('cfv-865-bwsdev', 1025)
        print >> sys.stderr, 'connecting to %s port %s' % server_address
        sock.connect(server_address)

        # Mas buffersize set to a single page
        buffsize = registers_per_page * bytes_per_register

        try:

            # Send data
            print >> sys.stderr, 'sending "%s"' % MyCommand
            sock.sendall(MyCommand)

            # # Look for the response
            amount_received = 0
            amount_expected = bytes_per_register * registers_per_page * Pages

            print('Receiving...')
            data_all = []
            while amount_received < amount_expected:
                data_b = bytearray()
                data_s = sock.recv(buffsize)
                data_b.extend(data_s)
                amount_received += len(data_s)
                data_all.extend(data_b)

            print('Formatting...')
            data_all_format = []
            start_time = time.time()
            if type == 0:
                if decimate == 1:
                    for i in range(0, amount_received, 4):
                        data_all_format.append((data_all[i + 1] << 8) | data_all[i])
                        data_all_format.append((data_all[i + 3] << 8) | data_all[i + 2])
                else:
                    for i in range(0, amount_received, decimate * 4):
                        data_all_format.append((data_all[i + 1] << 8) | data_all[i])

                data_all_format = np.int16(data_all_format)

            else:

                for i in range(0, amount_received, 8):
                    data_all_format.append(
                        (data_all[i + 3] << 24) | (data_all[i + 2] << 16) | (data_all[i + 1] << 8) | (data_all[i]))

            print("---- Formatting.. %s seconds ----" % (time.time() - start_time))
        finally:
            print >> sys.stderr, 'closing socket'
            sock.close()

        return data_all_format