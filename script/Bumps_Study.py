import sys
sys.path.append('../gui')
sys.path.append('../lib')

import csv
import numpy as np
import scipy.io as sio
import ops_processing, utils
import Configuration, DataScan, DataScan_Processed

from datetime import datetime, timedelta

from matplotlib import cm as cmx
from matplotlib import pyplot as plt
from matplotlib import colors as colors
import matplotlib.dates as mdates

from scipy.optimize import curve_fit

def Bump_Study(Configuration):

    superfig = plt.figure(figsize=[15,9])
    ax1=superfig.add_subplot(121)
    ax2=superfig.add_subplot(122)

    filename = configuration.app_datapath + '/Processed/Summary_Processed.mat'
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    TimeStamps = data['InfoData_CycleName']

    TimeStamps_datetime=[]
    for Stamp in TimeStamps:
        TimeStamps_datetime.append(datetime.strptime(Stamp,'%Y.%m.%d.%H.%M.%S.%f'))

    Centres_IN = data['Centres_IN']
    Sigmas_IN = data['Sigmas_IN']

    TStampsCSV_datetime=[]
    TStampsCSV=[]
    IntensityCSV = []
    ProgBumpCSV =[]
    BumpCSV = []


    filenameCSV = configuration.app_datapath + '/Processed/Bumps.csv'
    with open(filenameCSV) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                TStampsCSV_datetime.append(datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f') - timedelta(hours=2) )
                TStampsCSV.append(row[0])
                IntensityCSV.append(float(row[1]))
                ProgBumpCSV.append(row[2])
                BumpCSV.append(float(row[3]))
                line_count += 1


    # Search correspondences
    Centres_corr_IN = []
    Sigmas_corr_IN = []
    for stampcsv in TStampsCSV_datetime:
        difference = []
        for stamp in TimeStamps_datetime:
            diff = stamp - stampcsv
            diffsec = diff.days*24*3600 + diff.seconds
            difference.append(diffsec)
        difference=np.asarray(difference)
        Idx = np.where(difference>0)[0][0]-2
        print(Idx)
        Centres_corr_IN.append(Centres_IN[Idx][0])
        Sigmas_corr_IN.append(abs(Sigmas_IN[Idx][0]))

    # A bit of cleaning
    Centres_corr_IN=np.asarray(Centres_corr_IN)
    BumpCSV = np.asarray(BumpCSV)
    ProgBumpCSV =np.asarray(ProgBumpCSV)

    Idx = np.where(Centres_corr_IN < 6)
    Centres_corr_IN = Centres_corr_IN[Idx]
    BumpCSV = BumpCSV[Idx]
    ProgBumpCSV = ProgBumpCSV[Idx]

    fit = np.polyfit(BumpCSV,Centres_corr_IN,1)
    fit_fn = np.poly1d(fit)

    ax1.plot(BumpCSV,Centres_corr_IN,'ob',label='Data Points')
    ax1.plot(BumpCSV,fit_fn(BumpCSV),'r',label='Linear fit: y = ' + '{:.2f}'.format(fit[0]) + 'x ' + '{:.2f}'.format(fit[1]))
    ax1.set_ylabel('LIU-BWS Centroid [mm]')
    ax1.set_xlabel('BPM 54 Centroid [mm]')
    ax1.set_title('BWS Beam Centroids VS BPM')
    ax1.legend()
    ax1.grid()

    Residuals = Centres_corr_IN-fit_fn(BumpCSV)

    ax2.plot(BumpCSV,1e3*Residuals,'ob')
    ax2.set_ylabel('Fit Residuals [um]')
    ax2.set_xlabel('BCT Intensity')
    ax2.set_title('Fit Residuals')
    ax2.set_ylim(-125,125)
    ax2.grid()

    superfig.suptitle('2018_10_15_PS_PXBWSRB011_CR000001_MD_BCMS_Bumps')
    plt.show()



# MAIN PROGRAM STARTS HERE:
# Configuration and Data objects
configuration = Configuration.Configuration()
configuration.app_datapath = 'G:/Projects/BWS_Calibrations/Tunnel_Tests/2018_10_15_PS_PXBWSRB011_CR000001_MD_BCMS_Bumps'

# Make file list from folder content (sorted)
file_list = utils.mat_list_from_folder_sorted(configuration.app_datapath)

Bump_Study(configuration)