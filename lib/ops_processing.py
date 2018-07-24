#   --------------------------------------------------------------------------
# Copyright (c) <2017> <Lionel Garcia>
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


import os
import time
import numpy as np
import configparser
import scipy.io as sio
import PyQt5.QtCore as QtCore
import matplotlib.pyplot as plt

import utils

from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

def process_position(data, configuration, sampling_frequency, StartTime, showplot=False, filename=None, return_processing=False,
                     camelback_threshold_on=True):
    """
    Processing of the angular position based on the raw data of the OPS
    Credits : Jose Luis Sirvent (BE-BI-PM, CERN)
    """
    if configuration != None:
        # Recuperation of processing parameters:
                                                                        #config = configparser.RawConfigParser()
                                                                        #config.read(parameter_file)
        SlitsperTurn = configuration.ops_slits_per_turn                 #eval(config.get('OPS processing parameters', 'slits_per_turn'))
        rdcp = configuration.ops_relative_distance_correction_prameters #eval(config.get('OPS processing parameters', 'relative_distance_correction_prameters'))
        prominence = configuration.ops_prominence                       #eval(config.get('OPS processing parameters', 'prominence'))
        camelback_threshold = configuration.ops_camelback_threshold     #eval(config.get('OPS processing parameters', 'camelback_threshold'))
        OPS_processing_filter_freq = configuration.ops_low_pass_filter_freq #eval(config.get('OPS processing parameters', 'OPS_processing_filter_freq'))
        centroids = configuration.ops_centroids

        References_Timming = [configuration.def_ops_in_ref, configuration.def_ops_out_ref] #eval(config.get('OPS processing parameters', 'References_Timming'))
        AngularIncrement = 2 * np.pi / SlitsperTurn

        threshold_reference = np.amax(data) - camelback_threshold * np.mean(data)

        if camelback_threshold_on is True:
            data[np.where(data > threshold_reference)] = threshold_reference

        max_data = np.amax(data)
        min_data = np.amin(data)

        data = utils.butter_lowpass_filter(data, OPS_processing_filter_freq, sampling_frequency, order=5)

        data = data - min_data
        data = data / max_data

        maxtab, mintab = utils.peakdet(data, prominence)

        false = np.where(mintab[:, 1] > np.mean(maxtab[:, 1]))
        mintab = np.delete(mintab, false, 0)

        locs_up = np.array(maxtab)[:, 0]
        pck_up = np.array(maxtab)[:, 1]

        locs_dwn = np.array(mintab)[:, 0]
        pck_dwn = np.array(mintab)[:, 1]

        LengthMin = np.minimum(pck_up.size, pck_dwn.size)


        # Crosing psotion evaluation
        Crosingpos = np.ones((2, LengthMin))
        Crosingpos[1][:] = np.arange(1, LengthMin + 1)

        if centroids == True:
            # ==========================================================================
            # Position processing based on centroids
            # ==========================================================================
            Crosingpos[0][:] = locs_dwn[0:LengthMin]
            A = np.ones(LengthMin)
        else:
            # ==========================================================================
            # Position processing based on crossing points: Rising edges only
            # ==========================================================================
            IndexDwn = 0
            IndexUp = 0
            A = []

            # Position calculation loop:
            for i in range(0, LengthMin - 1):

                # Ensure crossing point in rising edge (locs_dwn < locs_up)
                while locs_dwn[IndexDwn] >= locs_up[IndexUp]:
                    IndexUp += 1

                while locs_dwn[IndexDwn + 1] < locs_up[IndexUp]:
                    IndexDwn += 1

                # Calculate thresshold for current window: Mean point
                Threshold = (data[int(locs_dwn[IndexDwn])] + data[int(locs_up[IndexUp])]) / 2
                # Find time on crossing point:
                b = int(locs_dwn[IndexDwn]) + np.where(data[int(locs_dwn[IndexDwn]):int(locs_up[IndexUp])] >= Threshold)[0][0]
                idx_n = np.where(data[int(locs_dwn[IndexDwn]):int(locs_up[IndexUp])] < Threshold)[0]
                idx_n = idx_n[::-1][0]
                a = int(locs_dwn[IndexDwn]) + idx_n

                Crosingpos[0, i] = (Threshold - data[int(a)]) * (b - a) / (data[int(b)] - data[int(a)]) + a

                # if showplot is True or showplot is 1:
                A = np.append(A, Threshold)

                # Move to next window:
                IndexDwn = IndexDwn + 1
                IndexUp = IndexUp + 1

        # ==========================================================================
        # Position loss compensation
        # ==========================================================================
        # Un-corrected position and time
        Data_Time = Crosingpos[0][:] * 1 / sampling_frequency
        Data_Pos = Crosingpos[1][:] * AngularIncrement
        # Relative-distances method for slit-loss compensation:
        Distances = np.diff(Crosingpos[0][0:Crosingpos.size - 1])

        # Method 2: Considering average of several previous periods
        previous_periods = 4
        cnt = 0
        DistancesAVG = []

        for i in range(previous_periods,len(Distances)):
            DistancesAVG.append(np.mean(Distances[i-previous_periods:i]))

        RelDistr = np.divide(Distances[previous_periods:len(Distances)], DistancesAVG)

        # Method 1: Only consider previous transition
        #RelDistr = np.divide(Distances[1:Distances.size], Distances[0:Distances.size - 1])

        # Search of compensation points:
        PointsCompensation = np.where(RelDistr >= rdcp[0])[0]

        for b in np.arange(0, PointsCompensation.size):

            if RelDistr[PointsCompensation[b]] >= rdcp[2]:
                # These are the references (metallic disk) or 3 slit loses
                Data_Pos[(PointsCompensation[b] + 1 + previous_periods):Data_Pos.size] = Data_Pos[(
                    PointsCompensation[b] + 1 + previous_periods):Data_Pos.size] + 3 * AngularIncrement

            elif RelDistr[PointsCompensation[b]] >= rdcp[1]:
                # These are 2 slit loses
                Data_Pos[(PointsCompensation[b] + 1 + previous_periods):Data_Pos.size] = Data_Pos[(
                    PointsCompensation[b] + 1 + previous_periods):Data_Pos.size] + 2 * AngularIncrement

            elif RelDistr[PointsCompensation[b]] >= rdcp[0]:
                # These are 1 slit losses
                Data_Pos[(PointsCompensation[b] + 1 + previous_periods):Data_Pos.size] = Data_Pos[(
                    PointsCompensation[b] + 1 + previous_periods):Data_Pos.size] + 1 * AngularIncrement

        # ==========================================================================
        # Alignment to First reference and Storage
        # ==========================================================================

        if StartTime > References_Timming[0] / 1000:
            Rtiming = References_Timming[1]
        else:
            Rtiming = References_Timming[0]

        Offset = np.where(Data_Time[0:Data_Time.size - 1] + StartTime > (Rtiming / 1000))[0][0]

        try:
            _IndexRef1 = Offset + np.where(RelDistr[Offset:LengthMin - Offset] > rdcp[1])[0]
            IndexRef1 = _IndexRef1[0]
            Data_Pos = Data_Pos - Data_Pos[IndexRef1]
        except:
            IndexRef1 = 0
            print('Disk Reference not found!')


        Data = np.ndarray((2, Data_Pos.size - 1))
        Data[0] = 1e3*(Data_Time[0:Data_Time.size - 1] + StartTime)
        Data[1] = Data_Pos[0:Data_Pos.size - 1]

        # ==========================================================================
        # Plotting script
        # ==========================================================================
        # if showplot is True or showplot is 1:
        #     fig = plt.figure(figsize=(11, 5))
        #     ax1 = fig.add_subplot(111)
        #     mplt.make_it_nice(ax1)
        #     plt.axhspan(0, threshold_reference / max_data, color='black', alpha=0.1)
        #     plt.axvspan(1e3 * StartTime + 1e3 * (data.size * 1 / 4) / sampling_frequency,
        #                 1e3 * StartTime + 1e3 * (data.size * 3 / 4) / sampling_frequency, color='black', alpha=0.1)
        #     plt.plot(1e3 * StartTime + 1e3 * np.arange(0, data.size) * 1 / sampling_frequency, data, linewidth=0.5)
        #     plt.plot(1e3 * StartTime + 1e3 * locs_up * 1 / sampling_frequency, pck_up, '.', MarkerSize=1.5)
        #     plt.plot(1e3 * StartTime + 1e3 * locs_dwn * 1 / sampling_frequency, pck_dwn, '.', MarkerSize=1.5)
        #     plt.plot(1e3 * StartTime + 1e3 * Crosingpos[0][0:A.size] * 1 / sampling_frequency, A, linewidth=0.5)
        #     ax1.set_title('Optical position sensor processing', loc='left')
        #     ax1.set_xlabel('Time (um)')
        #     ax1.set_ylabel('Normalized amplitude of signal (A.U.)')
        #     plt.show(block=False)
        # # plt.plot(1e3*StartTime+1e3*IndexRef1*1/sampling_frequency + StartTime, data[IndexRef1], 'x')
        # #        plt.plot(1e3*StartTime+1e3*np.arange(1,Distances.size)*1/sampling_frequency + StartTime, RelDistr, '.')

        if return_processing is True:
            return [0, 0,
                    1e3 * StartTime + 1e3 * locs_up * 1 / sampling_frequency, pck_up,
                    1e3 * StartTime + 1e3 * locs_dwn * 1 / sampling_frequency, pck_dwn,
                    1e3 * StartTime + 1e3 * Crosingpos[0][0:A.size] * 1 / sampling_frequency, A,
                    threshold_reference / max_data,
                    1e3 * StartTime + 1e3 * Crosingpos[0][IndexRef1] * (1 / sampling_frequency),
                    Data]

        else:
            return Data