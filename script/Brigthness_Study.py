import csv
import numpy as np
import scipy.io as sio
from matplotlib import pyplot as plt
from datetime import datetime, timedelta

def Fit_operational():
    #Prepare Figures
    superfig = plt.figure(figsize=[15,9])
    ax_1=superfig.add_subplot(121)
    ax_2=superfig.add_subplot(122)

    filename = 'G:/Projects/BWS_Calibrations/Tunnel_Tests/2018_10_24_PS_PXBWSRB011_CR000001_MD_BCMS_Brightness/Processed/Timber/PR.BWS65H.mat'
    dataOP =  sio.loadmat(filename, struct_as_record=False, squeeze_me=True)

    offset = 3
    Samples =  len(dataOP['TimberDataScan'][:,0])

    TimeStamps = dataOP['TimberDataScan'][offset:Samples,0]
    Prof_IN_Y = dataOP['TimberDataScan'][offset:Samples,4]
    Prof_IN_X = dataOP['TimberDataScan'][offset:Samples,6]
    Prof_OUT_Y = dataOP['TimberDataScan'][offset:Samples,5]
    Prof_OUT_X = dataOP['TimberDataScan'][offset:Samples,7]

    TimeStamps_datatime = []
    for stamp in TimeStamps:
        TimeStamps_datatime.append(datetime.strptime(stamp, '%Y-%m-%d %H:%M:%S.%f'))

    #LIU Stuff
    filenameLIU = 'G:/Projects/BWS_Calibrations/Tunnel_Tests/2018_10_24_PS_PXBWSRB011_CR000001_MD_BCMS_Brightness/Processed/Summary_Processed.mat'
    dataLIU =   sio.loadmat(filenameLIU, struct_as_record=False, squeeze_me=True)
    # Preparing LIU TimeStamps
    TimeStampsLIU_datetime = []
    for stamp in dataLIU['InfoData_CycleName']:
        TimeStampsLIU_datetime.append(datetime.strptime(stamp, '%Y.%m.%d.%H.%M.%S.%f'))
    cnt = 0
    From = 100
    Amount = 5
    for idxLIU, stampLIU in enumerate(TimeStampsLIU_datetime):
        for idxOP, stampOP in enumerate(TimeStamps_datatime):
            if stampLIU == stampOP:
                if (cnt > From) & (cnt <From+Amount):
                    # Smooth Operational profiles
                    Averaging_Window = 5
                    Prof_IN_Y[idxOP] = np.convolve(Prof_IN_Y[idxOP], np.ones((Averaging_Window,)) / Averaging_Window,
                                            mode='valid')
                    Prof_IN_X[idxOP] = np.convolve(Prof_IN_X[idxOP], np.ones((Averaging_Window,)) / Averaging_Window,
                                            mode='valid')
                    ax_1.plot(dataLIU['Profiles_IN_B'][0][idxLIU],dataLIU['Profiles_IN_B'][1][idxLIU],label=dataLIU['InfoData_CycleName'][idxLIU])
                    ax_2.plot(1e-3*Prof_IN_X[idxOP],Prof_IN_Y[idxOP],label=TimeStamps[idxOP])
                cnt = cnt + 1


    Scan = 20
    #plt.plot(1e-3*Prof_IN_X[Scan],Prof_IN_Y[Scan])
    #plt.title(TimeStamps[Scan])
    ax_1.grid()
    ax_1.set_title('BWS54H (LIU-BWS)')
    ax_1.set_xlim(-30,30)
    ax_1.legend()
    ax_2.grid()
    ax_2.set_title('BWS65H (Operational)')
    ax_2.set_xlim(-30,30)
    ax_2.legend()
    plt.show()

def Brigthness_study():

    # Prepare the plots
    superfig = plt.figure(figsize=[15,9])
    ax_IN=superfig.add_subplot(121)
    ax_OUT=superfig.add_subplot(122)

    superfig2 = plt.figure(figsize=[15,9])
    ax_INT=superfig2.add_subplot(111)


    # Filenames declaration
    filenameLIU = 'G:/Projects/BWS_Calibrations/Tunnel_Tests/2018_10_24_PS_PXBWSRB011_CR000001_MD_BCMS_Brightness/Processed/Summary_Processed.mat'
    filenameINT = 'G:/Projects/BWS_Calibrations/Tunnel_Tests/2018_10_24_PS_PXBWSRB011_CR000001_MD_BCMS_Brightness/Processed/PR_DCAFTINJ_1_INTENSITY.csv'

    # Load LIU Processed data
    dataLIU =   sio.loadmat(filenameLIU, struct_as_record=False, squeeze_me=True)

    # Load CSV data with Intensity and Tstamps
    TimeStampsCSV_TimeData = []
    IntensityCSV =[]
    with open(filenameINT) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            TimeStampsCSV_TimeData.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f'))
            IntensityCSV.append(float(row[1]))

    # Preparing LIU TimeStamps
    TimeStampsLIU_TimeData = []
    for stamp in dataLIU['InfoData_CycleName']:
        TimeStampsLIU_TimeData.append(datetime.strptime(stamp,'%Y.%m.%d.%H.%M.%S.%f'))

    # Search for TimeStamps correspondences and log Intensity per shot
    Intensity_Cycle_LIU = []

    for stamp in TimeStampsLIU_TimeData:
        cnt = 0
        for stamp_csv in TimeStampsCSV_TimeData:
            if stamp_csv == stamp:
                Intensity_Cycle_LIU.append(IntensityCSV[cnt+1])
                break
            cnt = cnt + 1

    Intensity_Cycle_LIU=np.asarray(Intensity_Cycle_LIU)

    Channel = 0

    Ctime = dataLIU['InfoData_AcqDelay']
    Sigma_IN = abs(1e3*dataLIU['Sigmas_IN'][:,Channel])
    Sigma_OUT = abs(1e3*dataLIU['Sigmas_OUT'][:,Channel])
    Centres_IN = 1e3*dataLIU['Centres_IN'][:,Channel]
    Centres_OUT = 1e3*dataLIU['Centres_OUT'][:,Channel]

    # Cleanup Data: Remove bad scans and those done at Ctime != 185
    Idx_IN =np.where((Centres_IN > -1600) & (Centres_IN < -585) & (Sigma_IN > 1000) & (Sigma_IN < 5000) & (Ctime == 139))
        # There are a couple of nasty points in the out so ... take only those with Sigma_OUT > 3240
    Idx_OUT = np.where((Centres_OUT > -1600) & (Centres_OUT < -585)& (Sigma_OUT > 3240) & (Sigma_OUT < 5000) &(Ctime == 139))

    # Linear Fitting Data
    fit_in = np.polyfit(Intensity_Cycle_LIU[Idx_IN], Sigma_IN[Idx_IN], 2)
    fit_in_fn = np.poly1d(fit_in)
    Res_in = Sigma_IN[Idx_IN]-fit_in_fn(Intensity_Cycle_LIU[Idx_IN])

    fit_out = np.polyfit(Intensity_Cycle_LIU[Idx_OUT], Sigma_OUT[Idx_OUT],2)
    fit_out_fn = np.poly1d(fit_out)
    Res_out = Sigma_OUT[Idx_OUT]-fit_out_fn(Intensity_Cycle_LIU[Idx_OUT])

    Fit_x = np.arange(35,90)

    ax_IN.plot(Intensity_Cycle_LIU[Idx_IN],Sigma_IN[Idx_IN],'ob',alpha=0.3,label='Data Points [{:.0f} points]'.format(len(Sigma_IN[Idx_IN])))
    ax_IN.plot(Fit_x,fit_in_fn(Fit_x),'r',  linewidth=3, label= 'Fit: y={:.2f}x^2'.format(fit_in[0]) + '+{:.2f}x'.format(fit_in[1]) + '+{:.1f}'.format(fit_in[2]) + '\n Residuals Stdev.: {:.1f}um'.format(np.std(Res_in)))
    ax_IN.grid()
    ax_IN.legend()
    ax_IN.set_title('LIU-BWS 54H Intensity VS Beam Sigma (IN Scan)')
    ax_IN.set_ylabel('Beam Sigma [um]')
    ax_IN.set_xlabel('Beam Intensity [1e10 Charges]')
    ax_IN.set_ylim(2500,5000)
    ax_IN.set_xlim(35,90)

    ax_OUT.plot(Intensity_Cycle_LIU[Idx_OUT],Sigma_OUT[Idx_OUT],'ob', alpha=0.3, label='Data Points [{:.0f} points]'.format(len(Sigma_IN[Idx_OUT])))
    ax_OUT.plot(Fit_x,fit_out_fn(Fit_x),'r', linewidth=3, label= 'Fit: y={:.2f}x'.format(fit_out[0]) +  '+{:.2f}x'.format(fit_out[1])  + '+{:.1f}'.format(fit_out[2]) + '\n Residuals Stdev.: {:.1f}um'.format(np.std(Res_out)))
    ax_OUT.grid()
    ax_OUT.legend()
    ax_OUT.set_title('LIU-BWS 54H Intensity VS Beam Sigma (OUT Scan)')
    ax_OUT.set_ylabel('Beam Sigma [um]')
    ax_OUT.set_xlabel('Beam Intensity [1e10 Charges]')
    ax_OUT.set_xlim(35,90)
    ax_OUT.set_ylim(2500,5000)

    ax_INT.plot(Intensity_Cycle_LIU,'ob',alpha=0.3)
    ax_INT.grid()
    ax_INT.set_title('Beam Intensity Cycle After scan (PR_DCAFTINJ_1_INTENSITY) ')
    ax_INT.set_xlabel('Scan Number')
    ax_INT.set_ylabel('Beam Intensity [1e10 Charges]')

    plt.show()

# MAIN PROGRAM STARTS HERE:
#Brigthness_study()
Fit_operational()