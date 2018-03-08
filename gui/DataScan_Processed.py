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

import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import ops_processing, utils

class DataScan_Processed:

    def __init__(self):
        '''

        '''

        # Data Structure and Initialization:
        # ----------------------------------

       # PMT
        self.PMT_IN = [np.ones(50), np.ones(50), np.ones(50), np.ones(50)]
        self.PMT_OUT = [np.ones(50), np.ones(50), np.ones(50), np.ones(50)]

        self.PS_POSA_IN_Proj = [np.ones(50), np.ones(50)]
        self.PS_POSA_OUT_Proj = [np.ones(50), np.ones(50)]

       # Position Sensors
        self.PS_POSA_IN = [np.ones(50),np.ones(50)]
        self.PS_POSA_IN_P = np.ones(50)

        self.PS_POSB_IN = [np.ones(50),np.ones(50)]
        self.PS_POSB_IN_P = np.ones(50)

        self.PS_POSA_OUT = [np.ones(50),np.ones(50)]
        self.PS_POSA_OUT_P = np.ones(50)

        self.PS_POSB_OUT = [np.ones(50),np.ones(50)]
        self.PS_POSB_OUT_P = np.ones(50)


    def process_data(self,data_scan,configuration):

        try:
            P = ops_processing.process_position(data_scan.PS_PSA_IN, configuration, data_scan.PS_Fs,
                                                1e-3*data_scan.PS_TimesStart[0], return_processing=True)
            self.PS_POSA_IN_P = P[0:10]
            self.PS_POSA_IN = P[10]
        except:
            print('Error processing PS_PSA_IN')

        try:
            P = ops_processing.process_position(data_scan.PS_PSB_IN, configuration, data_scan.PS_Fs,
                                                1e-3 * data_scan.PS_TimesStart[0], return_processing=True)
            self.PS_POSB_IN_P = P[0:10]
            self.PS_POSB_IN = P[10]
        except:
            print('Error processing PS_PSB_IN')

        try:
            P = ops_processing.process_position(data_scan.PS_PSA_OUT, configuration, data_scan.PS_Fs,
                                                1e-3 *data_scan.PS_TimesStart[1], return_processing=True)
            self.PS_POSA_OUT_P = P[0:10]
            self.PS_POSA_OUT = P[10]
        except:
            print('Error processing PS_PSA_OUT')

        try:
            P = ops_processing.process_position(data_scan.PS_PSB_OUT, configuration, data_scan.PS_Fs,
                                                1e-3 *data_scan.PS_TimesStart[1], return_processing=True)
            self.PS_POSB_OUT_P = P[0:10]
            self.PS_POSB_OUT = P[10]
        except:
            print('Error processing PS_PSB_OUT')


        for i in range(0,2):

            if i ==0:
                PMTA = data_scan.PMT_PMTA_IN
                PMTB = data_scan.PMT_PMTB_IN
                PMTC = data_scan.PMT_PMTC_IN
                PMTD = data_scan.PMT_PMTD_IN
                TimeStart = data_scan.PMT_TimesStart[0]
            else:
                PMTA = data_scan.PMT_PMTA_OUT
                PMTB = data_scan.PMT_PMTB_OUT
                PMTC = data_scan.PMT_PMTC_OUT
                PMTD = data_scan.PMT_PMTD_OUT
                TimeStart = data_scan.PMT_TimesStart[1]

            for c in range(0,4):

                if c == 0:
                    PMT = PMTA
                if c == 1:
                    PMT = PMTB
                if c == 2:
                    PMT = PMTC
                if c == 3:
                    PMT = PMTD

                try:
                    Procesed_Profile = utils.process_profile(PMT, 1.0*data_scan.PMT_Fs,
                                                                        1.0*TimeStart,
                                                                        configuration.pmt_filterfreq_profile,
                                                                        configuration.pmt_downsample_profile)
                    if i == 0:
                        self.PMT_IN[c] = Procesed_Profile
                    if i == 1:
                        self.PMT_OUT[c] = Procesed_Profile
                except:
                    print('Error Processing CH' + str(c + 1))

        try:
            self.PS_POSA_IN_Proj = utils.resample(self.PS_POSA_IN,self.PMT_IN[1])
            self.PS_POSA_OUT_Proj = utils.resample(self.PS_POSA_OUT,self.PMT_OUT[1])
        except:
            print('Error Interpolating')