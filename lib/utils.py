import os
import glob
import sys
import numpy as np

import scipy.signal as signal
from detect_peaks import detect_peaks
from scipy.interpolate import interp1d
from numpy import NaN, Inf, arange, isscalar, asarray, array
import matplotlib.pyplot as plt

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("..")

    return os.path.join(base_path, relative_path)

def mat_list_from_folder_sorted(mat_folder):

    mat_files = glob.glob(mat_folder + '/*.mat')
    mat_files.sort(key=os.path.getmtime)

    return mat_files

def butter_lowpass(cutoff, fs, order=5):
    """
    Matlab butter style filter design
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    """
    Low pass filtering of data using butter filter
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    """
    Matlab butter style filter design
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butter_highpass_filter(data, cutoff, fs, order=5):
    """
    Low pass filtering of data using butter filter
    """
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y


def resample(data_B, data_A):
    """
    Resample data_B ([timeB][dataB]) wrt data_A time ([timeA][dataB])
    and return resampled_data_B([timeA][resampleddataB]))
    """
    data_SB_interp = interp1d(data_B[0], data_B[1], bounds_error=False, fill_value=0)
    data_B_R = np.ones((2, data_A[0].size))
    data_B_R[1] = data_SB_interp(data_A[0])
    data_B_R[0] = np.copy(data_A[0])

    return data_B_R

def peakdet(v, delta, x=None):
    """
    Peak detection algorithm based on pseudo-prominence criteria

    Converted from MATLAB script at http://billauer.co.il/peakdet.html

    Returns two arrays

    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.

    Credits : Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    This function is released to the public domain; Any use is allowed.
    """
    maxtab = []
    mintab = []

    if x is None:
        x = arange(len(v))

    v = asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN

    lookformax = True

    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx - delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)

# Base for All (Emulation of TBT mode) Low pass filters profile
def process_profile0(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, FilterFreq, SamplingFreq, order=1)

    Amplit_p = Amplit[::Downsample]
    Time_p = Time[::Downsample]

    return [Time_p, Amplit_p]

# For PS
def process_profile_PS(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    # Peak detection (If many bunches peaks may correspond randomly to any bunch)
    High = 10e6

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, High, SamplingFreq, order=1)

    mpd = np.int(1.78e-6 * SamplingFreq)

    indexes = detect_peaks(Amplit,mpd=mpd)

    Amplit_p = Amplit[indexes]
    Time_p = Time[indexes]

    Averaging_Window = 20
    Amplit_p = np.convolve(Amplit_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')
    Time_p = np.convolve(Time_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')

    return [Time_p, Amplit_p]


def process_profile_PS2(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    # Bunch By Bunch integrals with 4 Bunches on PS
    High = 15e6

    Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, High, SamplingFreq, order=1)

    mpd = np.int(2e-6 * SamplingFreq)
    indexes = detect_peaks(Amplit, mpd=mpd)

    IntegralAround = np.int(1.13e-6 * SamplingFreq)
    indexes = indexes[10:len(indexes)-10]

    #plt.plot(Time,Amplit)
    #plt.plot(Time[indexes-IntegralAround],Amplit[indexes-IntegralAround],'.b')
    #plt.plot(Time[indexes+IntegralAround],Amplit[indexes+IntegralAround],'.r')
    #plt.show()

    Amplit_p=[]
    for i in indexes:
        Amplit_p.append(np.sum(Amplit[i-IntegralAround:i+IntegralAround]))

    #Amplit_p = np.asarray(Amplit_p)
    Time_p = Time[indexes]

    Averaging_Window = 5
    Amplit_p = np.convolve(Amplit_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')
    Time_p = np.convolve(Time_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')

    return [Time_p, Amplit_p]



# For PSB
def process_profile_PSB(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):

    High = 80e6
    Low  = 1e6

    Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
    Amplit = butter_bandpass_filter(data=Amplit, lowcut=Low, highcut=High, fs=SamplingFreq, order=5)

    Amplit[Amplit<0] = 0
    Amplit = butter_lowpass_filter(Amplit, FilterFreq, SamplingFreq, order=1)

    Amplit_p = Amplit[::Downsample]
    Time_p = Time[::Downsample]

    Offset = 100
    Amplit_p = Amplit_p[Offset:]
    Time_p = Time_p[Offset:]

    return [Time_p, Amplit_p]


# For SPS
def process_profile_SPS(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):

    High = 80e6
    Low = 1e6

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)
    Amplit = butter_bandpass_filter(data=Amplit,lowcut=Low, highcut=High, fs=SamplingFreq, order=2)

    Amplit[Amplit<0] = 0

    mpd = np.int(22.5e-6 * SamplingFreq)

    indexes = detect_peaks(Amplit, mpd=mpd)

    #intSamples = np.int(12.5e-9 * SamplingFreq)
    #Amplit_p=[]
    #for index in indexes:
    #    Amplit_p.append(np.sum(Amplit[index -intSamples :index + intSamples]))

    Amplit_p = Amplit[indexes]

    Time_p = Time[indexes]

    return [Time_p, Amplit_p]

def process_profile(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):

    Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, FilterFreq, SamplingFreq, order=1)

    #Amplit_p = Amplit
    #Time_p = Time

    Amplit_p = Amplit[::Downsample]
    Time_p = Time[::Downsample]

    return [Time_p, Amplit_p]

def process_profile_TbT(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    High = 80e6

    Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, High, SamplingFreq, order=1)

    mpd = np.int(1.76e-6 * SamplingFreq)

    Idx_slice = np.arange(0,len(Amplit)- mpd,mpd)

    Amplit_p = []
    Time_p = []

    for i in range(0,len(Idx_slice)-1):
        Amplit_p.append(np.sum(Amplit[Idx_slice[i]:Idx_slice[i+1]]))
        Time_p.append(Time[Idx_slice[i]])

    return [np.asarray(Time_p), np.asarray(Amplit_p)]



def do_projection(Fork_Length, Rotation_Offset, Fork_Phase, Angular_Position):

    Projection = Rotation_Offset - Fork_Length * np.cos(np.pi - Angular_Position + Fork_Phase)

    return Projection
