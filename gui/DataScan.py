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
        self.InfoData_HV = 0
        self.InfoData_TimeStamp = ' '
        self.InfoData_CycleStamp = ' '
        self.InfoData_CycleName = ' '

        # Photo-Multipliers
        self.PMT_Fs = 0
        self.PMT_TimesStart = np.ones(2)
        self.PMT_Factors = np.ones(4)

        self.PMT_PMTA_IN = np.ones(50)
        self.PMT_PMTB_IN = np.ones(50)
        self.PMT_PMTC_IN = np.ones(50)
        self.PMT_PMTD_IN = np.ones(50)

        self.PMT_PMTA_OUT = np.ones(50)
        self.PMT_PMTB_OUT = np.ones(50)
        self.PMT_PMTC_OUT = np.ones(50)
        self.PMT_PMTD_OUT = np.ones(50)

        self.PMT_TimeBound_OUT = np.ones(2)
        self.PMT_TimeBound_IN = np.ones(2)
        self.PMT_maxADCCount = 0

        self.PMT_Time_IN = np.ones(50)
        self.PMT_Time_OUT = np.ones(50)

        # Position Sensors
        self.PS_Fs = 0
        self.PS_Factors = np.ones(2)
        self.PS_TimesStart = np.ones(2)

        self.PS_PSA_IN = np.ones(50)
        self.PS_PSB_IN = np.ones(50)

        self.PS_PSA_OUT = np.ones(50)
        self.PS_PSB_OUT = np.ones(50)

        self.PS_TimeBound_IN = np.ones(2)
        self.PS_TimeBound_OUT = np.ones(2)
        self.PS_maxADCCount = 0

        self.PS_Time_IN = np.ones(50)
        self.PS_Time_OUT = np.ones(50)

    def load_data_v2(self,path):
        data = sio.loadmat(path, struct_as_record=False, squeeze_me=True)

        # InfoData
        self.InfoData_Filter_PRO = data['InfoData_Filter_PRO']
        self.InfoData_AcqDelay = data['InfoData_AcqDelay']
        self.InfoData_HV = data['InfoData_HV']
        self.InfoData_CycleStamp = data['InfoData_CycleStamp']
        self.InfoData_CycleName = data['InfoData_CycleName']

        # Photo-Multipliers
        self.PMT_Fs = data['PMT_Fs']
        self.PMT_TimesStart = data['PMT_TimesStart']
        self.PMT_Factors = data['PMT_Factors']

        self.PMT_PMTA_IN = data['PMT_PMTA_IN']
        self.PMT_PMTB_IN = data['PMT_PMTB_IN']
        self.PMT_PMTC_IN = data['PMT_PMTC_IN']
        self.PMT_PMTD_IN = data['PMT_PMTD_IN']

        self.PMT_PMTA_OUT = data['PMT_PMTA_OUT']
        self.PMT_PMTB_OUT = data['PMT_PMTB_OUT']
        self.PMT_PMTC_OUT = data['PMT_PMTC_OUT']
        self.PMT_PMTD_OUT = data['PMT_PMTD_OUT']

        # Position Sensors
        self.PS_Fs = data['PS_Fs']
        self.PS_Factors = data['PS_Factors']
        self.PS_TimesStart = data['PS_TimesStart']

        self.PS_PSA_IN = data['PS_PSA_IN']
        self.PS_PSB_IN = data['PS_PSB_IN']

        self.PS_PSA_OUT = data['PS_PSA_OUT']
        self.PS_PSB_OUT = data['PS_PSB_OUT']

    def load_data(self, path):
        print(path)
        data = sio.loadmat(path, struct_as_record = False, squeeze_me=True)
        GenStruct = data['MeasData']

        try:
            self.InfoData_Filter_PRO = data['InfoData_Filter_PRO']
            self.InfoData_AcqDelay = data['InfoData_AcqDelay']
            self.InfoData_HV = data['InfoData_HV']
            self.InfoData_CycleStamp = data['InfoData_CycleStamp']
            self.InfoData_CycleName = data['InfoData_CycleName']
        except:
            self.InfoData_Filter_PRO = 0
            self.InfoData_AcqDelay = 0
            self.InfoData_HV = 0
            self.InfoData_TimeStamp = ' '
            self.InfoData_CycleStamp = ' '
            self.InfoData_CycleName = ' '

        # PhotoMultipliers
        self.PMT_PMTA_IN = GenStruct.PMT.PMTA_IN * -1.0
        self.PMT_PMTA_OUT = GenStruct.PMT.PMTA_OUT * -1.0

        try:
            self.PMT_PMTB_IN = GenStruct.PMT.PMTB_IN * -1.0
            self.PMT_PMTB_OUT = GenStruct.PMT.PMTB_OUT * -1.0
        except:
            pass
        try:
            self.PMT_PMTC_IN = GenStruct.PMT.PMTC_IN * -1.0
            self.PMT_PMTC_OUT = GenStruct.PMT.PMTC_OUT * -1.0
        except:
            pass
        try:
            self.PMT_PMTD_IN = GenStruct.PMT.PMTD_IN * -1.0
            self.PMT_PMTD_OUT = GenStruct.PMT.PMTD_OUT * -1.0
        except:
            pass

        self.PMT_TimesStart[0] = 1e3 * (1.0*GenStruct.PMT.TimeBound_IN[0]) / GenStruct.PMT.Fs
        self.PMT_TimesStart[1] = 1e3 * (1.0*GenStruct.PMT.TimeBound_OUT[0]) / GenStruct.PMT.Fs

        self.PMT_Fs = GenStruct.PMT.Fs

        # Position Sensors
        self.PS_PSA_IN = GenStruct.PS.PSA_IN
        self.PS_PSB_IN = GenStruct.PS.PSB_IN

        self.PS_PSA_OUT = GenStruct.PS.PSA_OUT
        self.PS_PSB_OUT = GenStruct.PS.PSB_OUT

        self.PS_TimesStart[0] = 1e3 * (1.0 * GenStruct.PS.TimeBound_IN[0]) / GenStruct.PS.Fs
        self.PS_TimesStart[1] = 1e3 * (1.0 * GenStruct.PS.TimeBound_OUT[0]) / GenStruct.PS.Fs

        self.PS_Fs = GenStruct.PS.Fs

        self.PS_Factors = [1, 1]
        self.PMT_Factors = [1, 1, 1, 1]



