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

# Only Low Pass Filter
def process_profile0(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, FilterFreq, SamplingFreq, order=1)

    Amplit = Amplit[10000:]
    Time = Time[10000:]

    Amplit_p = Amplit[::Downsample]
    Time_p = Time[::Downsample]

    return [Time_p, Amplit_p]


# Low Pass Filter and Peak Detection
def process_profile_PS(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    High = 10e6

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, High, SamplingFreq, order=1)

    mpd = np.int(1.78e-6 * SamplingFreq)

    indexes = detect_peaks(Amplit,mpd=mpd)

    Amplit_p = Amplit[indexes]
    Time_p = Time[indexes]

    return [Time_p, Amplit_p]

# Low Pass Filter, Peak Detection and Baseline Recovery Auto mdp
def process_profile_PS_auto(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    Low = 20e6

    Amplit_p = []
    Time_p = []

    Amplit = butter_lowpass_filter(Amplit, Low, SamplingFreq, order=1)

    if len(np.where(Amplit>80)[0])>1000: # Only process if signal higher than certain value

        Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
        Th = np.max(Amplit) / 2

        mask1 = (Amplit[:-1] < Th) & (Amplit[1:] > Th)
        Idx = np.flatnonzero(mask1) + 1
        Offset = np.int(len(Idx) / 3)
        Idx = Idx[Offset:-Offset]  # We take only central third

        mpd = np.min(np.diff(Idx))
        IntegralAround = np.int(mpd / 2)

        indexes = detect_peaks(Amplit, mpd=mpd)
        indexes = indexes[10:len(indexes) - 10]

        for i in indexes:
            Baseline_tmp = Amplit[i - IntegralAround]
            if Baseline_tmp < Amplit[i]:
                Amplit_p.append(np.sum(Amplit[i - IntegralAround:i + IntegralAround] - Baseline_tmp))
                Time_p.append(Time[i])

        Time_p = np.asarray(Time_p)
        Amplit_p = np.asarray(Amplit_p)

        Averaging_Window = 5
        Amplit_p = np.convolve(Amplit_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')
        Time_p = np.convolve(Time_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')

    else:
        Time_p = TimeStart + 1e3 * (np.linspace(0,Amplit.size,100)/SamplingFreq)
        Amplit_p = np.zeros(100)

    #plt.plot(Time_p,Amplit_p)
    #plt.show()

    return [Time_p, Amplit_p]


# Low Pass Filter, Peak Detection and Baseline Recovery
def process_profile_PS20(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    High = 10e6

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, High, SamplingFreq, order=1)

    Interval = 1.78e-6
    mpd = np.int(Interval * SamplingFreq)

    indexes = detect_peaks(Amplit,mpd=mpd)
    Diff =  np.int((Interval/2) * SamplingFreq)

    Amplit_p = Amplit[indexes] #- Amplit[indexes-Diff]
    Time_p = Time[indexes]

    return [Time_p, Amplit_p]

def process_profile_PS2(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    # Bunch By Bunch integrals with 4 Bunches on PS
    High = 15e6

    Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
    Amplit = butter_lowpass_filter(Amplit, High, SamplingFreq, order=1)


    mpd = np.int(1e-6 * SamplingFreq)
    indexes = detect_peaks(Amplit, mpd=mpd)

    #IntegralAround = np.int(1.13e-6 * SamplingFreq)
    IntegralAround =  np.int(300e-9*SamplingFreq) # Integrals of 200ns
    indexes = indexes[10:len(indexes)-10]

    #plt.plot(Time,Amplit)
    #plt.plot(Time[indexes-IntegralAround],Amplit[indexes-IntegralAround],'.b')
    #plt.plot(Time[indexes+IntegralAround],Amplit[indexes+IntegralAround],'.r')
    #plt.show()

    Amplit_p=[]
    Baseline = []
    for i in indexes:
        Amplit_p.append(np.sum(Amplit[i-IntegralAround:i+IntegralAround]))
        Baseline.append(np.sum(Amplit[i-(mpd/2):i-(mpd/2)+IntegralAround]))

    Amplit_p = np.asarray(Amplit_p) - np.asarray(Baseline)
    #Amplit_p = np.asarray(Amplit_p)
    Time_p = Time[indexes]

    #Averaging_Window = 5
    #Amplit_p = np.convolve(Amplit_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')
    #Time_p = np.convolve(Time_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')

    return [Time_p, Amplit_p]

# Band Pass and Peak Detection
def process_profile_PS3(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    High = 10e6
    Low =2.5e6

    Time = TimeStart + 1e3 * (np.arange(0, Amplit.size, 1) / SamplingFreq)
    #plt.plot(Time,Amplit)
    Amplit = butter_bandpass_filter(Amplit,Low, High, SamplingFreq, order=1)
    #plt.plot(Time,Amplit)

    # Trimm the vectors around centre
    #TimeAround = np.int(2e3/SamplingFreq)
    #IndexCentre = np.where(Amplit == np.max(Amplit))
    #Time = Time[IndexCentre-TimeAround:IndexCentre+TimeAround]
    #Amplit = Amplit[IndexCentre-TimeAround:IndexCentre+TimeAround]

    mpd = np.int(2e-6 * SamplingFreq)
    indexes = detect_peaks(Amplit, mpd=mpd)

    #IntegralAround = np.int(1.13e-6 * SamplingFreq)
    #IntegralAround =  np.int(100e-9*SamplingFreq)  Integrals of 200ns
    #indexes = indexes[10:len(indexes)-10]

    #plt.plot(Time[indexes],Amplit[indexes],'.r')
    #plt.show()

    Amplit_p = Amplit[indexes]
    Time_p = Time[indexes]

    #Averaging_Window = 5
    #Amplit_p = np.convolve(Amplit_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')
    #Time_p = np.convolve(Time_p, np.ones((Averaging_Window,)) / Averaging_Window, mode='valid')

    return [Time_p, Amplit_p]

# Trimm the data, Band Pass and Peak Detection
def process_profile_PS4(Amplit, SamplingFreq, TimeStart, FilterFreq, Downsample):
    High = 10e6
    Low = 2e6

    Samples = Amplit.size

    Time =TimeStart + 1e3 * (np.arange(0, Samples, 1) / SamplingFreq)
    Amplit =butter_bandpass_filter(Amplit,Low, High, SamplingFreq, order=1)

    # Trimm the vectors around centre
    TimeAround = 4e-3*SamplingFreq
    SamplesLeft = np.int(TimeAround)
    SamplesRight= SamplesLeft

    IndexCentre = np.where(Amplit == np.max(Amplit))[0][0]

    if IndexCentre + TimeAround > Samples:
        SamplesRight = Samples - IndexCentre - 1

    if IndexCentre - TimeAround <0:
        SamplesLeft = IndexCentre - 1

    Time = Time[IndexCentre-SamplesLeft:IndexCentre+SamplesRight]
    Amplit = Amplit[IndexCentre-SamplesLeft:IndexCentre+SamplesRight]

    mpd = np.int(2e-6 * SamplingFreq)
    indexes = detect_peaks(Amplit, mpd=mpd)

    Amplit_p = Amplit[indexes]
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
    Low = 40e6

    Time = TimeStart + 1e3*(np.arange(0,Amplit.size,1) / SamplingFreq)

    # Trimm the vectors around centre
    Samples = Amplit.size
    TimeAround = 1e-3 * SamplingFreq
    TimeAround = np.int(TimeAround)
    IndexCentre = np.where(Amplit == np.max(Amplit))[0][0]
    if IndexCentre + TimeAround > Samples:
        TimeAround = Samples - IndexCentre - 1

    if IndexCentre - TimeAround < 0:
        TimeAround = IndexCentre - 1

    Time = Time[IndexCentre - TimeAround:IndexCentre + TimeAround]
    Amplit = Amplit[IndexCentre - TimeAround:IndexCentre + TimeAround]
    # Finish Trimming profiles

    Amplit = butter_bandpass_filter(data=Amplit,lowcut=Low, highcut=High, fs=SamplingFreq, order=2)
    Amplit[Amplit<0] = 0

    mpd = np.int(22.5e-6 * SamplingFreq)
    #mpd = np.int(25e-9 * SamplingFreq)

    indexes = detect_peaks(Amplit, mpd=mpd)

    #intSamples = np.int(12.5e-9 * SamplingFreq)
    #Amplit_p=[]
    #for index in indexes:
    #    Amplit_p.append(np.sum(Amplit[index -intSamples :index + intSamples]))

    Amplit_p = Amplit[indexes]

    Time_p = Time[indexes]

    return [Time_p, Amplit_p]


def do_projection(Fork_Length, Rotation_Offset, Angle_Correction, Angular_Position):

    Projection = Rotation_Offset - Fork_Length * np.cos(np.pi - (Angular_Position + Angle_Correction))

    return Projection

def do_projection_poly(fit_poly, Angular_Position):
    fit_func = np.poly1d(fit_poly)
    Projection = fit_func(Angular_Position)

    return Projection

def detect_index_edges(Signal_Y, EdgeDetected = 'Rising'):

    min = np.min(Signal_Y)
    max = np.max(Signal_Y)
    Thresshold = max-min/2

    prev_sample = Signal_Y[0]
    Index_Edges = []

    if EdgeDetected == 'Rising':
        for i in range(1, len(Signal_Y)):
            curr_sample = Signal_Y[i]
            if prev_sample < Thresshold and curr_sample > Thresshold:
                Index_Edges.append(i)
            prev_sample = curr_sample

    if EdgeDetected == 'Falling':
        for i in range(1, len(Signal_Y)):
            curr_sample = Signal_Y[i]
            if prev_sample > Thresshold and curr_sample < Thresshold:
                Index_Edges.append(i)
            prev_sample = curr_sample

    if EdgeDetected == 'Both':
        for i in range(1,len(Signal_Y)):
            curr_sample = Signal_Y[i]
            if prev_sample < Thresshold and curr_sample > Thresshold:
                Index_Edges.append(i)
            if prev_sample > Thresshold and curr_sample < Thresshold:
                Index_Edges.append(i)
            prev_sample = curr_sample
    return Index_Edges


