from __future__ import unicode_literals

import time
import datetime
import numpy as np
import scipy.io as sio

from ctypes import *
from PyQt5 import QtCore
import matplotlib.pyplot as plt


class DataCollection(QtCore.QThread):

    notifyState = QtCore.pyqtSignal(str)
    fileReady = QtCore.pyqtSignal(str)

    def __init__(self, configuration, data_scan, pmt_picoscope, ps_picoscope, buttons_pannel, parent=None):

        self.configuration = configuration
        self.buttons_pannel = buttons_pannel
        self.ps_picoscope = ps_picoscope
        self.pmt_picoscope =pmt_picoscope
        self.data_scan = data_scan

        super(DataCollection, self).__init__(parent)

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
                state_i.coupling = self.ps_picoscope.m.Couplings.dc50
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

            # Trigger configuration of both scopes
            triggerChannel = self.ps_picoscope.m.TriggerChannels.Aux
            direction = self.ps_picoscope.m.ThresholdDirections.rising
            thresholdVoltage = 0.5
            Wait = 2000

            status_trigger = self.ps_picoscope.set_simple_trigger(enabled=True, source=triggerChannel, threshold=thresholdVoltage, direction=direction, waitfor=Wait)
            status_trigger = self.pmt_picoscope.set_simple_trigger(enabled=True, source=triggerChannel, threshold=thresholdVoltage, direction=direction, waitfor=Wait)


            # Arming Scopes for acquisition when trigger is generated OPS
            self.pmt_picoscope._collect_cb_type = self.pmt_picoscope._block_ready()
            self.pmt_picoscope._collect_cb_func = self.pmt_picoscope._collect_cb_type(self.pmt_picoscope._collect_cb)
            status = self.pmt_picoscope._run_block(pretrig=0, posttrig=MaxSamples_PMT, timebase=Timebase_PMT, oversample=0, ref_time=None,
                                                  segment=0, ref_cb=self.pmt_picoscope._collect_cb_func, ref_cb_param=None)

            # Arming Scopes for acquisition when trigger is generated PMT
            self.ps_picoscope._collect_cb_type = self.ps_picoscope._block_ready()
            self.ps_picoscope._collect_cb_func = self.ps_picoscope._collect_cb_type(self.ps_picoscope._collect_cb)
            status = self.ps_picoscope._run_block(pretrig=0, posttrig=MaxSamples_OPS, timebase=Timebase_OPS, oversample=0, ref_time=None,
                                                  segment=0, ref_cb=self.ps_picoscope._collect_cb_func, ref_cb_param=None)

            # Wait for trigger
            self.notifyState.emit('Trig...')
            self.pmt_picoscope._collect_event.wait()
            self.ps_picoscope._collect_event.wait()

            self.pmt_picoscope._collect_event.clear()
            self.ps_picoscope._collect_event.clear()

            # Start timer after trigger is received
            t = time.time()

            self.notifyState.emit('Rec...')
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
                                                        mode=self.ps_picoscope.m.RatioModes.raw,
                                                        segment=0,
                                                        ref_overflow=byref(overvoltaged))

            self.data_scan.PS_PSA_IN = data_ops[0]['max'][0:Samples_In_OPS]
            self.data_scan.PS_PSB_IN = data_ops[1]['max'][0:Samples_In_OPS]

            #plt.plot(np.asarray(self.data_scan.PS_PSA_IN))
            #plt.show()

            # OPS Out
            status_read = self.ps_picoscope._get_values(start=Index_Start_Out_OPS,
                                                        ref_samples=byref(c_uint32(Samples_Out_OPS)),
                                                        ratio=1,
                                                        mode=self.ps_picoscope.m.RatioModes.raw,
                                                        segment=0,
                                                        ref_overflow=byref(overvoltaged))

            self.data_scan.PS_PSA_OUT = data_ops[0]['max'][0:Samples_Out_OPS]
            self.data_scan.PS_PSB_OUT = data_ops[1]['max'][0:Samples_Out_OPS]


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
            self.data_scan.PMT_PMTA_IN = data_pmt[0]['max'][0:Samples_In_PMT]
            self.data_scan.PMT_PMTB_IN = data_pmt[1]['max'][0:Samples_In_PMT]
            self.data_scan.PMT_PMTC_IN = data_pmt[2]['max'][0:Samples_In_PMT]
            self.data_scan.PMT_PMTD_IN = data_pmt[3]['max'][0:Samples_In_PMT]


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

            # Print timer value to check how long data recovery and storage need
             # Note: With data compression TRUE time ~ 6.5seg, without data compresion time ~ 0.5seg
            elapsed = time.time() - t
            print('Acquisisitoin elapsed time: ' + str(elapsed) + 'sec.')

            self.notifyState.emit('IDLE')
            self.fileReady.emit(filename)

            # Check for Loop exit condition
            if self.buttons_pannel.acquisition_mode_single.isChecked():
                break

    def updateinfodata(self):
        try:
            data = sio.loadmat(self.configuration.info_datapath, struct_as_record=False, squeeze_me=True)
            GenStruct = data['InfoData']
            self.data_scan.InfoData_Filter_PRO = GenStruct.Filter_PRO
            self.data_scan.InfoData_HV = GenStruct.HV_PMT
            self.data_scan.InfoData_AcqDelay = GenStruct.AcqDelay
            self.data_scan.InfoData_CycleName = GenStruct.cycleName
            self.data_scan.InfoData_CycleStamp = GenStruct.cycleStamp
        except:
            print('Error updating InfoData')