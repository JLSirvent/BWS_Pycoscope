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

class DataScan:

    def __init__(self):
        '''

        '''

        # Data Structure and Initialization:
        # ----------------------------------

        # InfoData
        self.InfoData_Filter_PRO = 0
        self.InfoData_AcqDelay = 0
        self.InfoData_TimeStamp = ' '
        self.InfoData_CycleStamp = ' '
        self.InfoData_CycleName = ''

        # Photo-Multipliers
        self.PMT_PMTA_IN = np.ones(50)
        self.PMT_PMTB_IN = np.ones(50)
        self.PMT_PMTC_IN = np.ones(50)
        self.PMT_PMTD_IN = np.ones(50)
        self.PMT_TimeBound_IN = np.ones(2)

        self.PMT_PMTA_OUT = np.ones(50)
        self.PMT_PMTB_OUT = np.ones(50)
        self.PMT_PMTC_OUT = np.ones(50)
        self.PMT_PMTD_OUT = np.ones(50)
        self.PMT_TimeBound_OUT = np.ones(2)

        self.PMT_Fs = 0
        self.PMT_maxADCCount = 0

        # Position Sensors
        self.PS_PSA_IN = np.ones(50)
        self.PS_PSB_IN = np.ones(50)
        self.PS_TimeBound_IN = np.ones(2)

        self.PS_PSA_OUT = np.ones(50)
        self.PS_PSB_OUT = np.ones(50)
        self.PS_TimeBound_OUT = np.ones(2)

        self.PMT_Time_IN = np.ones(50)
        self.PMT_Time_OUT = np.ones(50)

        self.PS_Time_IN = np.ones(50)
        self.PS_Time_OUT = np.ones(50)

        self.PS_Fs = 0
        self.PS_maxADCCount = 0

    def load_data(self, path):
        print(path)
        data = sio.loadmat(path, struct_as_record = False, squeeze_me=True)
        GenStruct = data['MeasData']

        # InfoData
        try:
            self.InfoData_Filter_PRO = GenStruct.InfoData.Filter_PRO
        except:
            print('Error InfoData_Filter_PRO')
        try:
            self.InfoData_AcqDelay = GenStruct.InfoData.AcqDelay
        except:
            print('Error InfoData_AcqDelay')
        try:
            self.InfoData_TimeStamp = GenStruct.InfoData.timeStamp
        except:
            print('Error InfoData_TimeStamp')
        try:
            self.InfoData_CycleStamp = GenStruct.InfoData.cycleStamp
        except:
            print('Error InfoData_CycleStamp')
        try:
            self.InfoData_CycleName = GenStruct.InfoData.cycleName
        except:
            print('Error InfoData_CycleName')

        # PMT
        try:
            self.PMT_PMTA_IN = GenStruct.PMT.PMTA_IN
        except:
            print('Error PMT_PMTA_IN')

        try:
            self.PMT_PMTB_IN = GenStruct.PMT.PMTB_IN
        except:
            print('Error PMT_PMTB_IN')

        try:
            self.PMT_PMTC_IN = GenStruct.PMT.PMTC_IN
        except:
            print('Error PMT_PMTC_IN')

        try:
            self.PMT_PMTD_IN = GenStruct.PMT.PMTD_IN
        except:
            print('Error PMT_PMTD_IN')

        self.PMT_TimeBound_IN = GenStruct.PMT.TimeBound_IN

        try:
            self.PMT_PMTA_OUT = GenStruct.PMT.PMTA_OUT
        except:
            print('Error PMT_PMTA_OUT')
        try:
            self.PMT_PMTB_OUT = GenStruct.PMT.PMTB_OUT
        except:
            print('Error PMT_PMTB_OUT')
        try:
            self.PMT_PMTC_OUT = GenStruct.PMT.PMTC_OUT
        except:
            print('Error PMT_PMTC_OUT')
        try:
            self.PMT_PMTD_OUT = GenStruct.PMT.PMTD_OUT
        except:
            print('Error PMT_PMTD_OUT')

        self.PMT_TimeBound_OUT = GenStruct.PMT.TimeBound_OUT

        self.PMT_Fs = GenStruct.PMT.Fs
        self.PMT_maxADCCount = GenStruct.PMT.maxADCCount

        # Position Sensors
        self.PS_PSA_IN = GenStruct.PS.PSA_IN
        self.PS_PSB_IN = GenStruct.PS.PSB_IN
        self.PS_TimeBound_IN = GenStruct.PS.TimeBound_IN

        self.PS_PSA_OUT = GenStruct.PS.PSA_OUT
        self.PS_PSB_OUT = GenStruct.PS.PSB_OUT
        self.PS_TimeBound_OUT = GenStruct.PS.TimeBound_OUT

        self.PS_Fs = GenStruct.PS.Fs
        self.PS_maxADCCount = GenStruct.PS.maxADCCount

        # Calculation of Time Vectors (in ms)
        lengthPMTIN = np.max([len(self.PMT_PMTA_IN),len(self.PMT_PMTB_IN),len(self.PMT_PMTC_IN),len(self.PMT_PMTD_IN)])
        lengthPMTOUT = np.max([len(self.PMT_PMTA_OUT),len(self.PMT_PMTB_OUT),len(self.PMT_PMTC_OUT),len(self.PMT_PMTD_OUT)])

        self.PMT_Time_IN =  1e3*(self.PMT_TimeBound_IN[0] + np.asarray(range(0, lengthPMTIN)))/self.PMT_Fs
        self.PMT_Time_OUT = 1e3*(self.PMT_TimeBound_OUT[0] + np.asarray(range(0, lengthPMTOUT)))/self.PMT_Fs

        self.PS_Time_IN =  1e3*(self.PS_TimeBound_IN[0] + np.asarray(range(0, len(self.PS_PSA_IN))))/self.PS_Fs
        self.PS_Time_OUT = 1e3*(self.PS_TimeBound_OUT[0] + np.asarray(range(0, len(self.PS_PSA_OUT))))/self.PS_Fs

