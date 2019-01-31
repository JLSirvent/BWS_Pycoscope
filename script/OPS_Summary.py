import sys
sys.path.append('../gui')
sys.path.append('../lib')


import numpy as np
import scipy.io as sio
import ops_processing, utils
from scipy.stats import chisquare,chi2
import Configuration, DataScan, DataScan_Processed

from datetime import datetime

from matplotlib import cm as cmx
from matplotlib import pyplot as plt
from matplotlib import colors as colors
import matplotlib.dates as mdates

from scipy.optimize import curve_fit

def process_ops_and_save(configuration, file_list):
    angular_position_SA_IN = []
    angular_position_SB_IN = []
    #speed_SA_IN = []
    #speed_SB_IN = []
    #eccentricity_IN = []
    time_SA_IN = []
    time_SB_IN = []

    angular_position_SA_OUT = []
    angular_position_SB_OUT = []
    #speed_SA_OUT = []
    #speed_SB_OUT = []
    #eccentricity_OUT = []
    time_SA_OUT = []
    time_SB_OUT = []

    InfoData_CycleStamp = []
    InfoData_TimeStamp = []

    data_scan = DataScan.DataScan()
    cnt = 0
    total_files= len(file_list)
    for single_file in file_list:
        try:
            print("Completed:{}%".format(100*cnt/total_files))

            data_scan.load_data_v2(single_file)

            InfoData_CycleStamp.append(data_scan.InfoData_CycleStamp)
            InfoData_TimeStamp.append(data_scan.InfoData_CycleStamp)

            for s in range(0, 2):
                if s == 0:
                    PS_SA = data_scan.PS_PSA_IN
                    PS_SB = data_scan.PS_PSB_IN
                else:
                    PS_SA = data_scan.PS_PSA_OUT
                    PS_SB = data_scan.PS_PSB_OUT

                # Calculation of Position
                P_A = ops_processing.process_position(PS_SA, configuration, data_scan.PS_Fs,
                                                      1e-3 * data_scan.PS_TimesStart[s], return_processing=False)
                P_B = ops_processing.process_position(PS_SB, configuration, data_scan.PS_Fs,
                                                      1e-3 * data_scan.PS_TimesStart[s], return_processing=False)

                if s == 0:
                    angular_position_SA_IN.append(P_A[1])
                    angular_position_SB_IN.append(P_B[1])
                    time_SA_IN.append(P_A[0])
                    time_SB_IN.append(P_B[0])
                else:
                    angular_position_SA_OUT.append(P_A[1])
                    angular_position_SB_OUT.append(P_B[1])
                    time_SA_OUT.append(P_A[0])
                    time_SB_OUT.append(P_B[0])

        except:
            print('Error on: ' + single_file)

        cnt = cnt + 1

        #if cnt == 10:
        #    break

    sio.savemat(configuration.app_datapath + '/Processed_IN.mat',
                {'InfoData_CycleStamp': InfoData_CycleStamp,
                 'InfoData_TimeStamp': InfoData_TimeStamp,
                 'angular_position_SA': angular_position_SA_IN,
                 'angular_position_SB': angular_position_SB_IN,
                 'time_SA': time_SA_IN,
                 'time_SB': time_SB_IN},
                do_compression=True)

    sio.savemat(configuration.app_datapath + '/Processed_OUT.mat',
                {'InfoData_CycleStamp': InfoData_CycleStamp,
                 'InfoData_TimeStamp': InfoData_TimeStamp,
                 'angular_position_SA': angular_position_SA_OUT,
                 'angular_position_SB': angular_position_SB_OUT,
                 'time_SA': time_SA_OUT,
                 'time_SB': time_SB_OUT},
                do_compression=True)

def process_amplitudes_and_save(configuration, file_list):

    def gauss(x, *p):
        a, b, c, d = p
        y = a * np.exp(-np.power((x - b), 2.) / (2. * c ** 2.)) + d
        return y

    InfoData_CycleStamp=[]
    InfoData_TimeStamp=[]
    InfoData_Filter_PRO=[]
    InfoData_HV=[]
    InfoData_CycleName = []
    InfoData_AcqDelay = []

    Positions_A_IN_X = []
    Positions_B_IN_X = []
    Positions_A_OUT_X = []
    Positions_B_OUT_X = []

    Positions_A_IN_Y = []
    Positions_B_IN_Y = []
    Positions_A_OUT_Y = []
    Positions_B_OUT_Y = []

    Profiles_IN_A = []
    Profiles_IN_B = []
    Profiles_IN_C = []
    Profiles_IN_D = []

    Profiles_OUT_A = []
    Profiles_OUT_B = []
    Profiles_OUT_C = []
    Profiles_OUT_D = []

    Positions_IN_A = []
    Positions_OUT_A = []
    Positions_IN_B = []
    Positions_OUT_B = []
    Positions_IN_C = []
    Positions_OUT_C = []
    Positions_IN_D = []
    Positions_OUT_D = []

    Imax_IN=[]
    Imax_OUT=[]
    Qtot_IN= []
    Qtot_OUT = []

    Sigmas_IN=[]
    Sigmas_OUT =[]
    Centres_IN = []
    Centres_OUT = []
    AmplitG_IN = []
    AmplitG_OUT = []

    GOF_Rsquared_IN= []
    GOF_RMSE_IN= []
    GOF_X2_IN= []

    GOF_Rsquared_OUT= []
    GOF_RMSE_OUT= []
    GOF_X2_OUT = []

    data_scan = DataScan.DataScan()
    data_scan_processed = DataScan_Processed.DataScan_Processed()

    cnt = 0
    total_files= len(file_list)

    plt.ion()
    fig = plt.figure()
    ax = []
    ax.append(fig.add_subplot(241))
    ax.append(fig.add_subplot(242))
    ax.append(fig.add_subplot(243))
    ax.append(fig.add_subplot(244))
    ax.append(fig.add_subplot(245))
    ax.append(fig.add_subplot(246))
    ax.append(fig.add_subplot(247))
    ax.append(fig.add_subplot(248))

    for single_file in file_list:
        # try:
        print("Completed:{}%".format(100*cnt/total_files)+ " File: " + single_file.split('\\')[-1])

        data_scan.load_data_v2(single_file)

        data_scan_processed.process_data(data_scan, configuration)

        # Concatenate InfoData
        InfoData_CycleStamp.append(single_file.split('\\')[-1])
        #InfoData_CycleStamp.append(data_scan.InfoData_CycleStamp)
        InfoData_TimeStamp.append(data_scan.InfoData_TimeStamp)
        InfoData_Filter_PRO.append(data_scan.InfoData_Filter_PRO)
        InfoData_HV.append(data_scan.InfoData_HV)
        InfoData_CycleName.append(data_scan.InfoData_CycleName)
        InfoData_AcqDelay.append(data_scan.InfoData_AcqDelay)

        # Get position Data
        Positions_A_IN_X.append(data_scan_processed.PS_POSA_IN[0])
        Positions_B_IN_X.append(data_scan_processed.PS_POSB_IN[0])
        Positions_A_OUT_X.append(data_scan_processed.PS_POSA_OUT[0])
        Positions_B_OUT_X.append(data_scan_processed.PS_POSB_OUT[0])

        Positions_A_IN_Y.append(data_scan_processed.PS_POSA_IN[1])
        Positions_B_IN_Y.append(data_scan_processed.PS_POSB_IN[1])
        Positions_A_OUT_Y.append(data_scan_processed.PS_POSA_OUT[1])
        Positions_B_OUT_Y.append(data_scan_processed.PS_POSB_OUT[1])

        # Get Profiles Data
        Profiles_IN_A.append(np.array(100*data_scan_processed.PMT_IN[0][1]))
        Profiles_IN_B.append(np.array(100*data_scan_processed.PMT_IN[1][1]))
        Profiles_IN_C.append(np.array(100*data_scan_processed.PMT_IN[2][1]))
        Profiles_IN_D.append(np.array(100*data_scan_processed.PMT_IN[3][1]))

        Profiles_OUT_A.append(np.array(100*data_scan_processed.PMT_OUT[0][1]))
        Profiles_OUT_B.append(np.array(100*data_scan_processed.PMT_OUT[1][1]))
        Profiles_OUT_C.append(np.array(100*data_scan_processed.PMT_OUT[2][1]))
        Profiles_OUT_D.append(np.array(100*data_scan_processed.PMT_OUT[3][1]))
        #
        Positions_IN_A.append(np.array(data_scan_processed.PS_POSA_IN_Proj[0][1]))
        Positions_OUT_A.append(np.array(data_scan_processed.PS_POSA_OUT_Proj[0][1]))

        Positions_IN_B.append(np.array(data_scan_processed.PS_POSA_IN_Proj[1][1]))
        Positions_OUT_B.append(np.array(data_scan_processed.PS_POSA_OUT_Proj[1][1]))

        Positions_IN_C.append(np.array(data_scan_processed.PS_POSA_IN_Proj[2][1]))
        Positions_OUT_C.append(np.array(data_scan_processed.PS_POSA_OUT_Proj[2][1]))

        Positions_IN_D.append(np.array(data_scan_processed.PS_POSA_IN_Proj[3][1]))
        Positions_OUT_D.append(np.array(data_scan_processed.PS_POSA_OUT_Proj[3][1]))

        # Process Profiles Data
        Imax_IN.append(data_scan_processed.PMT_IN_Imax[0:4])
        Imax_OUT.append(data_scan_processed.PMT_OUT_Imax[0:4])
        Qtot_IN.append(data_scan_processed.PMT_IN_Qtot[0:4])
        Qtot_OUT.append(data_scan_processed.PMT_OUT_Qtot[0:4])

        #plt.suptitle(data_scan.InfoData_CycleStamp + '\n' + data_scan.InfoData_CycleName + ' F: ' + str(data_scan.InfoData_Filter_PRO) + ' HV: ' + str(np.round(data_scan.InfoData_HV)) +' AcqDly: ' + str(data_scan.InfoData_AcqDelay) + 'ms')

        for s in range(0, 2):

            Sigmas = np.ones(4) * 0
            Centres = np.ones(4) * 100
            AmplitG = np.ones(4) * 0
            GOF_Rsquared = np.ones(4) *0
            GOF_RMSE = np.ones(4) *0
            GOF_X2 = np.ones(4) *0

            if s == 0:
                PMT_Data = data_scan_processed.PMT_IN
                PMT_Pos = data_scan_processed.PS_POSA_IN_Proj
            else:
                PMT_Data = data_scan_processed.PMT_OUT
                PMT_Pos = data_scan_processed.PS_POSA_OUT_Proj

            for c in range(0,4):
                try:
                    _y = np.asarray(PMT_Data[c][1])
                    _x = np.asarray(PMT_Pos[c][1])

                # Evaluate the Fit the data and calculate GOF trough Rsquared
                    # Starting points
                    a = 0.5 #np.max(_y) - np.min(_y)
                    mean = _x[np.where(_y == np.max(_y))[0]]
                    sigma = 2
                    o = np.min(_y)

                    # First Fit
                    popt, pcov = curve_fit(gauss, _x, _y, p0=[a, mean, sigma, o])

                    # Trimm for simetric beam profiles
                    Around = 6.5 * np.abs(popt[2])
                    s_Left = Around
                    s_Right = Around

                    if popt[1]+Around > np.max(_x):
                        s_Right = abs(np.max(_x) - popt[1])

                    if popt[1]-Around < np.min(_x):
                        s_Left = np.abs(np.min(_x) + popt[1])

                    Indexes = np.where((_x>popt[1]-s_Left) & (_x<popt[1]+s_Right))
                    _y = _y[Indexes]
                    _x = _x[Indexes]

                    # Second Fit  and determine GOF
                    popt, pcov = curve_fit(gauss, _x, _y, p0=[a, mean, sigma, o])
                    fit_y = gauss(_x,*popt)

                    # Goodness of FIT
                    ss_res = np.sum((_y - fit_y) ** 2)
                    ss_tot = np.sum((_y - np.mean(_y)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot)

                    # Normalized data for all channels
                    _ynorm = _y * np.max(_y) ** -1
                    fit_ynorm = fit_y * np.max(_y) ** -1
                    baseline = np.min(fit_ynorm)

                    rmse = 10000 * (_ynorm.size) ** -1 * np.sum((_ynorm - fit_ynorm) ** 2)
                    X_2 = chisquare(f_obs=_ynorm - baseline + 0.1, f_exp=fit_ynorm - baseline + 0.1)

                    Sigmas[c] = np.abs(popt[2])
                    Centres[c] = popt[1]
                    AmplitG[c] = popt[0] - popt[3]
                    GOF_Rsquared[c] = r_squared
                    GOF_RMSE[c] = rmse
                    GOF_X2[c] = X_2[0]

                    axp = ax[c + s*4]
                    axp.clear()
                    axp.set_title('Profile CH' + str(c))
                    axp.set_xlabel('Position [mm]')
                    axp.set_ylabel('Amplitude [a.u]')
                    axp.grid()
                    axp.plot(_x,_y, 'b')
                    axp.plot(_x,fit_y,'r', label = 'Sigma: {:.2f}'.format(Sigmas[c]) + 'mm\nCentre: {:.1f}'.format(Centres[c])+ '\nGOF_X2:{:.2f}'.format(GOF_X2[c]))
                    axp.legend(loc='upper right')
                    fig.canvas.draw()
                    plt.pause(0.01)

                except:
                    print('Error fitting CH' + str(c))

            if s == 0:
                Sigmas_IN.append(Sigmas)
                Centres_IN.append(Centres)
                AmplitG_IN.append(AmplitG)
                GOF_Rsquared_IN.append(GOF_Rsquared)
                GOF_RMSE_IN.append(GOF_RMSE)
                GOF_X2_IN.append(GOF_X2)
            else:
                Sigmas_OUT.append(Sigmas)
                Centres_OUT.append(Centres)
                AmplitG_OUT.append(AmplitG)
                GOF_Rsquared_OUT.append(GOF_Rsquared)
                GOF_RMSE_OUT.append(GOF_RMSE)
                GOF_X2_OUT.append(GOF_X2)

        cnt = cnt + 1
        #if cnt == 10:
        #   break

    sio.savemat(configuration.app_datapath + '/Processed/Summary_Processed.mat',
                {'InfoData_CycleStamp': InfoData_CycleStamp,
                 'InfoData_TimeStamp': InfoData_TimeStamp,
                 'InfoData_Filter_PRO': InfoData_Filter_PRO,
                 'InfoData_HV': InfoData_HV,
                 'InfoData_CycleName': InfoData_CycleName,
                 'InfoData_AcqDelay': InfoData_AcqDelay,
                 'Profiles_IN_A': [[Positions_IN_A],[Profiles_IN_A]],
                 'Profiles_IN_B': [[Positions_IN_B],[Profiles_IN_B]],
                 'Profiles_IN_C': [[Positions_IN_C],[Profiles_IN_C]],
                 'Profiles_IN_D': [[Positions_IN_D],[Profiles_IN_D]],
                 'Profiles_OUT_A': [[Positions_OUT_A],[Profiles_OUT_A]],
                 'Profiles_OUT_B': [[Positions_OUT_B],[Profiles_OUT_B]],
                 'Profiles_OUT_C': [[Positions_OUT_C],[Profiles_OUT_C]],
                 'Profiles_OUT_D': [[Positions_OUT_D],[Profiles_OUT_D]],
                 'Positions_A_IN' : [[Positions_A_IN_X],[Positions_A_IN_Y]],
                 'Positions_B_IN' : [[Positions_B_IN_X],[Positions_B_IN_Y]],
                 'Positions_A_OUT': [[Positions_A_OUT_X],[Positions_A_OUT_Y]],
                 'Positions_B_OUT': [[Positions_B_OUT_X],[Positions_B_OUT_Y]],
                 'Sigmas_IN': Sigmas_IN,
                 'Sigmas_OUT': Sigmas_OUT,
                 'Centres_IN':Centres_IN,
                 'Centres_OUT': Centres_OUT,
                 'AmplitG_IN': AmplitG_IN,
                 'AmplitG_OUT': AmplitG_OUT,
                 'Qtot_IN': Qtot_IN,
                 'Qtot_OUT': Qtot_OUT,
                 'Imax_IN': Imax_IN,
                 'Imax_OUT': Imax_OUT,
                 'GOF_X2_IN': GOF_X2_IN,
                 'GOF_X2_OUT': GOF_X2_OUT,
                 'GOF_RMSE_IN': GOF_RMSE_IN,
                 'GOF_RMSE_OUT': GOF_RMSE_OUT,
                 'GOF_Rsquared_IN':GOF_Rsquared_IN,
                 'GOF_Rsquared_OUT': GOF_Rsquared_OUT
                 },
                  do_compression = True)

def process_only_meas_cond(configuration,file_list):

    InfoData_CycleStamp = []
    InfoData_TimeStamp = []
    InfoData_Filter_PRO = []
    InfoData_HV = []
    InfoData_CycleName = []
    InfoData_AcqDelay = []
    AmplitG_IN = []

    data_scan = DataScan.DataScan()

    cnt = 0
    total_files= len(file_list)

    for single_file in file_list:
        try:
            AmplitG = np.ones(4) * 0

            data_scan.load_data_v2(single_file)
            AmplitG[0] = np.min(1e3 * data_scan.PMT_PMTA_IN * data_scan.PMT_Factors[0])
            AmplitG[1] = np.min(1e3 * data_scan.PMT_PMTB_IN * data_scan.PMT_Factors[1])
            AmplitG[2] = np.min(1e3 * data_scan.PMT_PMTC_IN * data_scan.PMT_Factors[2])
            AmplitG[3] = np.min(1e3 * data_scan.PMT_PMTD_IN * data_scan.PMT_Factors[3])

            print("Completed:{}%".format(100*cnt/total_files)+ " File: " + single_file.split('\\')[-1])
            cnt = cnt + 1
            # Concatenate InfoData
            InfoData_CycleStamp.append(data_scan.InfoData_CycleStamp)
            InfoData_TimeStamp.append(data_scan.InfoData_TimeStamp)
            InfoData_Filter_PRO.append(data_scan.InfoData_Filter_PRO)
            InfoData_HV.append(data_scan.InfoData_HV)
            InfoData_CycleName.append(data_scan.InfoData_CycleName)
            InfoData_AcqDelay.append(data_scan.InfoData_AcqDelay)
            AmplitG_IN.append(AmplitG)
        except:
            print("Error!")

    sio.savemat(configuration.app_datapath + '/Processed/Summary_Processed_MeasCond.mat',
                {'InfoData_CycleStamp': InfoData_CycleStamp,
                 'InfoData_TimeStamp': InfoData_TimeStamp,
                 'InfoData_Filter_PRO': InfoData_Filter_PRO,
                 'InfoData_HV': InfoData_HV,
                 'InfoData_CycleName': InfoData_CycleName,
                 'InfoData_AcqDelay': InfoData_AcqDelay,
                 'AmplitG_IN': AmplitG_IN
                 },
                 do_compression=True)

def plot_only_meas_cond(configuration):
    filename = configuration.app_datapath + '/Processed/Summary_Processed_MeasCond.mat'
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    superplot = plt.figure(figsize=[15,9])

    ax_HV = superplot.add_subplot(511)
    ax_Filt = superplot.add_subplot(512)
    ax_Ctime = superplot.add_subplot(513)
    ax_User = superplot.add_subplot(514)
    ax_Amplit = superplot.add_subplot(515)

    ax_HV.plot(data['InfoData_HV'])
    ax_HV.grid(True, color='#DBDBDB', alpha=0.4)

    ax_Filt.plot(data['InfoData_Filter_PRO'])
    ax_Filt.grid(True, color='#DBDBDB', alpha=0.4)

    ax_Ctime.plot(data['InfoData_AcqDelay'])
    ax_Ctime.grid(True, color='#DBDBDB', alpha=0.4)

    #ax_User.plot(data['InfoData_CycleStamp'])
    #ax_User.grid(True, color='#DBDBDB', alpha=0.4)

    ax_Amplit.plot(data['AmplitG_IN'])
    ax_Amplit.grid(True, color='#DBDBDB', alpha=0.4)

    plt.show()

def plot_report(configuration):

    filename = configuration.app_datapath + '/Processed/Summary_Processed.mat'
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    superplot_ctime=plt.figure(figsize=[15,9])
    ctime_ax1=superplot_ctime.add_subplot(211)
    ctime_ax2=superplot_ctime.add_subplot(212,sharex = ctime_ax1)

    superplot_iq = plt.figure(figsize = [15,9])
    iq_ax1=superplot_iq.add_subplot(211)
    iq_ax2=superplot_iq.add_subplot(212,sharex=iq_ax1)

    superplot_cond =  plt.figure(figsize = [15,9])
    c_ax1 = superplot_cond.add_subplot(311)
    c_ax2 = superplot_cond.add_subplot(312, sharex=c_ax1)
    c_ax3 = superplot_cond.add_subplot(313, sharex=c_ax1)

    superplot = plt.figure(figsize = [15,9])
    ax0 = superplot.add_subplot(311)
    ax2 = superplot.add_subplot(312,sharex=ax0)
    ax1 = superplot.add_subplot(313,sharex=ax0)

    superplot_Q_Sigma = plt.figure(figsize = [15,9])
    axq = superplot_Q_Sigma.add_subplot(111)
    axq.grid()
    # FilterData
    CycleStamp=data['InfoData_CycleName']
    print(CycleStamp[:])
    for s in range(0,2):
        if s==0:
            scan = 'IN'
            Col = ['ob', 'og', '-og', 'oy']
        else:
            scan = 'OUT'
            Col = ['or', 'oy', '--sg', 'sy']

        GOF = data['GOF_X2_'+scan]
        Sigmas = data['Sigmas_'+scan]
        Centres= data['Centres_'+scan]
        Imax = data['Imax_'+scan]
        QTot = data['Qtot_'+scan]
        AcqDly = data['InfoData_AcqDelay']
        HV = data['InfoData_HV']
        Amplit= data['AmplitG_'+scan]
        TStamp =data['InfoData_CycleName']

        Tmp=[]
        for i in range(0,len(TStamp)):
            try:
                Tmp.append(datetime.strptime(TStamp[i],'%Y.%m.%d.%H.%M.%S.%f'))
            except:
                print('Error Tstamp')
                Tmp.append(datetime.strptime(TStamp[i-1],'%Y.%m.%d.%H.%M.%S.%f'))

        Tstamp_f=mdates.date2num(Tmp)

        if scan == 'OUT':
            AcqDly = AcqDly + 200

        c_ax1.plot(HV)
        c_ax1.set_title('PMT High Voltage')
        c_ax1.set_ylabel('Voltage [v]')
        c_ax1.set_xlabel('Scan number')
        c_ax1.grid()

        try:
            c_ax2.plot(CycleStamp)
            c_ax2.set_title('Cycle Name')
            c_ax2.set_ylabel('Name')
            c_ax2.set_xlabel('Scan number')
            c_ax2.grid()
        except:
            pass

        c_ax3.plot(AcqDly)
        c_ax3.set_title('Cycle Time')
        c_ax3.set_ylabel('Time [ms]')
        c_ax3.set_xlabel('Scan number')
        c_ax3.grid()

        # With Filter
        # Limit= 600 #5.5
        # Cycle = 'CPS.USER.LHC1'
        # HV_lim_min = 1000
        # HV_lim_max = 0
        #
        # Idx = []
        # Idx.append(np.where((HV[:]>HV_lim_max) & (HV[:]<HV_lim_min) & (CycleStamp[:] == Cycle) & (Amplit[:, 0] < Limit)))
        # Idx.append(np.where((HV[:]>HV_lim_max) & (HV[:]<HV_lim_min) & (CycleStamp[:] == Cycle) & (Amplit[:, 0] >= Limit) & (Amplit[:, 1] < Limit)))
        # Idx.append(np.where((HV[:]>HV_lim_max) & (HV[:]<HV_lim_min) & (CycleStamp[:] == Cycle) & (Amplit[:, 1] >= Limit) & (Amplit[:, 2] < Limit)))
        # Idx.append(np.where((HV[:]>HV_lim_max) & (HV[:]<HV_lim_min) & (CycleStamp[:] == Cycle) & (Amplit[:, 2] >= Limit) & (Amplit[:, 3] < Limit)))

        # Without Filter
        Idx = []
        Idx.append(np.arange(0, Amplit[:,0].size))
        Idx.append(np.arange(0, Amplit[:,0].size))
        Idx.append(np.arange(0, Amplit[:,0].size))
        Idx.append(np.arange(0, Amplit[:,0].size))

        for c in range(0,2):

            #ax1.plot_date(Tstamp_f[Idx[c]],1e3*np.abs(Sigmas[Idx[c],c]),Col[c], markersize = 3, label = 'CH '+ str(c))
            #ax2.plot_date(Tstamp_f[Idx[c]],1e3*Centres[Idx[c],c],Col[c], markersize = 3, label = 'CH '+ str(c))
            ax0.plot(GOF[Idx[c],c],Col[c], markersize=3, label='CH ' + str(c))
            ax1.plot(1e3 * np.abs(Sigmas[Idx[c], c]), Col[c], markersize=3, label='CH ' + str(c))
            ax2.plot(1e3 * Centres[Idx[c], c], Col[c], markersize=3, label='CH ' + str(c))

            axq.plot(QTot[Idx[c],c],1e3 * np.abs(Sigmas[Idx[c], c]),Col[c],markersize = 3)

            iq_ax1.plot(Imax[:,c],Col[c],markersize = 3, label = 'CH '+ str(c))
            iq_ax2.plot(Amplit[:,c],Col[c],markersize = 3, label = 'CH '+ str(c))

        #Interval = np.arange(183,195)
        #Ch = 1
        #print('Mean: ' +str(np.mean(Centres[Interval,Ch])) + 'Err: ' +str(1e3*np.std(Centres[Interval,Ch])))

        # For plot Ctime vs Sigma
        for c in range(0,1):
            ctime_ax1.plot(AcqDly[np.asarray(Idx[c])],Sigmas[Idx[c],c],Col[c], markersize = 3, label = 'CH '+ str(c))
            ctime_ax2.plot(AcqDly[np.asarray(Idx[c])],Centres[Idx[c],c],Col[c], markersize = 3, label = 'CH '+ str(c))


    ctime_ax1.grid()
    ctime_ax2.grid()
    ctime_ax1.set_title('Ctime Vs Beam Size')
    ctime_ax1.set_ylabel('Sigma [mm]')
    ctime_ax1.set_xlabel('Ctime[ms]')
    ctime_ax2.set_title('Ctime Vs Beam Centre')
    ctime_ax2.set_ylabel('Centre [mm]')
    ctime_ax2.set_xlabel('Ctime[ms]')
    #ctime_ax1.set_ylim(0,4)
    #ctime_ax1.set_xlim(200,1650)

    ax0.grid()
    ax0.set_title('GOF')
    ax0.set_ylabel('RMSE')
    #ax0.set_xlabel('Scan Number')
    #ax0.set_ylim(0.98, 1.01)

    ax1.grid()
    ax1.set_title('Beam Size')
    ax1.set_ylabel('Sigma [um]')
    ax1.set_xlabel('Scan number')
    ax1.set_ylim(1000,5500)
    #ax1.legend()

    ax2.grid()
    ax2.set_title('Beam Centroid')
    ax2.set_ylabel('Centroid [um]')
    #ax2.set_xlabel('Scan number')
    ax2.set_ylim(-4000,4000)
    #ax2.legend()

    iq_ax1.grid()
    iq_ax1.set_title('Imax')
    iq_ax1.set_ylabel('Current [uA]')
    iq_ax1.set_xlabel('Scan number')
    #iq_ax1.set_ylim(0,5)
    iq_ax1.legend()

    iq_ax2.grid()
    iq_ax2.set_title('Qtot')
    iq_ax2.set_ylabel('Charge [nC]')
    iq_ax2.set_xlabel('Scan number')
    #iq_ax2.set_ylim(0,5)
    iq_ax2.legend()

    plt.show()

def plot_report_position(Configuration, projected = False):

    superplot_hist = plt.figure(figsize=[15,9])
    ax_in = superplot_hist.add_subplot(211)
    ax_in.grid()
    ax_in.set_title('Time at beam chamber crossing IN')
    ax_in.set_ylabel('Time [ms]')
    ax_out = superplot_hist.add_subplot(212)
    ax_out.set_title('Time at beam chamber crossing out')
    ax_out.set_ylabel('Time [ms]')
    ax_out.set_xlabel('Scan Number')
    ax_out.grid()

    superplot = plt.figure(figsize = [15,9])

    pos_in = superplot.add_subplot(321)
    pos_out = superplot.add_subplot(322)

    pos_in.grid()
    pos_in.set_ylabel('Position')
    pos_in.set_title('IN SCAN')

    pos_out.grid()
    pos_out.set_ylabel('Position')
    pos_out.set_title('OUT SCAN')

    speed_in = superplot.add_subplot(323,sharex=pos_in)
    speed_out = superplot.add_subplot(324, sharex=pos_out)

    speed_in.grid()
    speed_in.set_ylabel('Speed')
    speed_in.set_xlabel('Time [ms]')

    speed_out.grid()
    speed_out.set_ylabel('Speed')
    speed_out.set_xlabel('Time [ms]')

    eccentricity_in= superplot.add_subplot(325)
    eccentricity_out = superplot.add_subplot(326)

    eccentricity_in.grid()
    eccentricity_in.set_xlabel('Position')
    eccentricity_in.set_ylabel('Error')

    eccentricity_out.grid()
    eccentricity_out.set_xlabel('Position')
    eccentricity_out.set_ylabel('Error')

    filename = configuration.app_datapath + '/Processed/Summary_Processed.mat'
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)

    Positions_A_IN_X = data['Positions_A_IN'][0]
    Positions_A_IN_Y = data['Positions_A_IN'][1]
    Positions_A_OUT_X = data['Positions_A_OUT'][0]
    Positions_A_OUT_Y = data['Positions_A_OUT'][1]

    Positions_B_IN_X = data['Positions_B_IN'][0]
    Positions_B_IN_Y = data['Positions_B_IN'][1]
    Positions_B_OUT_X = data['Positions_B_OUT'][0]
    Positions_B_OUT_Y = data['Positions_B_OUT'][1]

    Scans  = len(Positions_A_IN_X)

    Time_at_zero_IN = []
    Time_at_zero_OUT= []

    for i in range(100,150):#range(0,Scans):

        if projected == True:
            Positions_A_IN_Y[i] = utils.do_projection(configuration.calib_fork_length,
                                                   configuration.calib_rotation_offset,
                                                   configuration.calib_fork_phase, Positions_A_IN_Y[i])
            try:
                Idx = np.where(Positions_A_IN_Y[i] < 0)[0][0]
                Time_at_zero_IN.append(Positions_A_IN_X[i][Idx])
            except:
                pass
                #Time_at_zero_IN.append(0)

            Positions_B_IN_Y[i] = utils.do_projection(configuration.calib_fork_length,
                                                   configuration.calib_rotation_offset,
                                                   configuration.calib_fork_phase, Positions_B_IN_Y[i])
            Positions_A_OUT_Y[i] = utils.do_projection(configuration.calib_fork_length,
                                                   configuration.calib_rotation_offset,
                                                   configuration.calib_fork_phase, Positions_A_OUT_Y[i])
            try:
                Idx = np.where(Positions_A_OUT_Y[i] < 0)[0][0]
                Time_at_zero_OUT.append(Positions_A_OUT_X[i][Idx])
            except:
                pass
                #Time_at_zero_OUT.append(0)

            Positions_B_OUT_Y[i] = utils.do_projection(configuration.calib_fork_length,
                                                   configuration.calib_rotation_offset,
                                                   configuration.calib_fork_phase, Positions_B_OUT_Y[i])

        pos_in.plot(Positions_A_IN_X[i],Positions_A_IN_Y[i])
        pos_out.plot(Positions_A_OUT_X[i],Positions_A_OUT_Y[i])

        N = 10
        try:
            speed_SA_IN = np.convolve(np.divide(np.diff(Positions_A_IN_Y[i]), np.diff(Positions_A_IN_X[i])), np.ones((N,)) / N, mode='valid')
            speed_SB_IN = np.convolve(np.divide(np.diff(Positions_B_IN_Y[i]), np.diff(Positions_B_IN_X[i])), np.ones((N,)) / N, mode='valid')
            speed_SA_OUT = np.convolve(np.divide(np.diff(Positions_A_OUT_Y[i]), np.diff(Positions_A_OUT_X[i])), np.ones((N,)) / N, mode='valid')
            speed_SB_OUT = np.convolve(np.divide(np.diff(Positions_B_OUT_Y[i]), np.diff(Positions_B_OUT_X[i])), np.ones((N,)) / N, mode='valid')

            # Calculation of Eccentricity
            P_B_R = utils.resample([Positions_B_IN_X[i], Positions_B_IN_Y[i]],
                                   [Positions_A_IN_X[i], Positions_A_IN_Y[i]])
            ceccentricity_IN = 1e6 * np.subtract(Positions_A_IN_Y[i], P_B_R[1]) / 2

            P_B_R = utils.resample([Positions_B_OUT_X[i], Positions_B_OUT_Y[i]],
                                   [Positions_A_OUT_X[i], Positions_A_OUT_Y[i]])
            ceccentricity_OUT = 1e6 * np.subtract(Positions_A_OUT_Y[i], P_B_R[1]) / 2

            speed_in.plot(Positions_A_IN_X[i][0:speed_SA_IN.size],speed_SA_IN)
            speed_out.plot(Positions_A_OUT_X[i][0:speed_SA_OUT.size],speed_SA_OUT)

            eccentricity_in.plot(Positions_A_IN_Y[i], ceccentricity_IN)
            eccentricity_out.plot(Positions_A_OUT_Y[i], ceccentricity_OUT)

        except:
            pass

    #print(Time_at_zero_IN)

    #Idx = np.asarray(np.where((Time_at_zero_IN > 20) & ((Time_at_zero_IN > 23))))
    ax_in.plot(Time_at_zero_IN,'.b')
    ax_out.plot(Time_at_zero_OUT,'.b')

    #ax_in.hist(np.asarray(Time_at_zero_IN))
    #ax_out.hist(np.asarray(Time_at_zero_OUT))


    #Positions_A_OUT_X[i][0:speed_SA_OUT.size]
    plt.show()

def plot_position_summary(configuration, projected = False):

    superplot = plt.figure(figsize = [15,9])

    pos_in = superplot.add_subplot(321)
    pos_out = superplot.add_subplot(322)

    speed_in = superplot.add_subplot(323,sharex=pos_in)
    speed_out = superplot.add_subplot(324, sharex=pos_out)

    eccentricity_in= superplot.add_subplot(325)
    eccentricity_out = superplot.add_subplot(326)

    rdsplot= plt.figure(figsize = [15,9])

    rds_in = rdsplot.add_subplot(211)
    rds_out = rdsplot.add_subplot(212)

    driftplot=plt.figure(figsize = [15,9])
    drift_in = driftplot.add_subplot(121)
    drift_out = driftplot.add_subplot(122)

    for i in range(0,2):

        Position_Zero = []
        counter = 0
        for d in range(0,1):

            if d == 0:
                #foldername = 'G:\Projects\BWS_Calibrations\Tunnel_Tests/2018_06_07_PS_PXBWSRB011_CR000001_Acquisition_Tests_Without_Beam\Processed'
                foldername = configuration.app_datapath
            if d == 1:
                foldername = 'G:\Projects\BWS_Calibrations\Tunnel_Tests/2018_06_08_PS_PXBWSRB011_CR000001_Acquisition_Tests_With_Beam_LHCINDIV\Processed'
            if d == 2:
                foldername = 'G:\Projects\BWS_Calibrations\Tunnel_Tests/2018_06_11_PS_PXBWSRB011_CR000001_Acquisition_Tests_With_Beam_LHCINDIV_LHCPROBE_TOF\Processed'
            if d == 3:
                foldername = 'G:\Projects\BWS_Calibrations\Tunnel_Tests/2018_06_13_PS_PXBWSRB011_CR000001_Acquisition_Tests_With_Beam_LHC25_BCMS\Processed'

            if i == 0:
                filename = foldername + '/Processed_IN.mat'
                ax_pos = pos_in
                ax_speed = speed_in
                ax_eccentricity = eccentricity_in
                ax_rds = rds_in
                ax_drift=drift_in
                s_title = 'IN'
            else:
                filename = foldername + '/Processed_OUT.mat'
                ax_pos = pos_out
                ax_speed = speed_out
                ax_eccentricity = eccentricity_out
                ax_rds = rds_out
                ax_drift=drift_out
                s_title = 'OUT'

            fontsize = 10

            if projected == True:
                ax_pos.set_ylabel('Positon [mm]', fontsize=fontsize)
                ax_speed.set_ylabel('Speed [m/s]', fontsize=fontsize)
                ax_eccentricity.set_ylabel('Eccentricity [um]', fontsize=fontsize)
                ax_eccentricity.set_xlabel('Position[mm]', fontsize=fontsize)
                ax_drift.set_ylabel('Position at time [mm]')
                #ax_eccentricity.set_ylim(-200, 200)

            else:
                ax_pos.set_ylabel('Positon [rad]', fontsize=fontsize)
                ax_speed.set_ylabel('Speed [rad/s]', fontsize=fontsize)
                ax_eccentricity.set_ylabel('Eccentricity [urad]', fontsize=fontsize)
                ax_eccentricity.set_xlabel('Position[rad]', fontsize=fontsize)
                ax_drift.set_ylabel('Position at time [rad]')
                ax_eccentricity.set_ylim(-600, 200)

            ax_pos.set_xlabel('Time[ms]', fontsize=fontsize)
            ax_pos.set_title('Positions '+ s_title, fontsize=fontsize)
            ax_pos.grid(True, color = '#DBDBDB', alpha = 0.4)

            ax_speed.set_xlabel('Time[ms]', fontsize=fontsize)
            ax_speed.set_title('Speeds '+ s_title, fontsize=fontsize)
            ax_speed.grid(True, color = '#DBDBDB', alpha = 0.4)

            ax_eccentricity.set_title('Eccentricities '+ s_title, fontsize=fontsize)
            ax_eccentricity.grid(True, color = '#DBDBDB', alpha = 0.4)

            ax_rds.set_xlabel('Time[ms]', fontsize=fontsize)
            ax_rds.set_ylabel('RDS [a.u]', fontsize=fontsize)
            ax_rds.set_title('Relative Distance Signature ' + s_title, fontsize=fontsize)
            ax_rds.grid(True, color = '#DBDBDB', alpha = 0.4)
            ax_rds.axhspan(configuration.ops_relative_distance_correction_prameters[1], configuration.ops_relative_distance_correction_prameters[0], color='black', alpha=0.1)
            ax_rds.axhspan(configuration.ops_relative_distance_correction_prameters[2], configuration.ops_relative_distance_correction_prameters[1], color='red', alpha=0.1)

            ax_drift.set_xlabel('Scan Number')
            ax_drift.set_title('Disk drift ' + s_title, fontsize=fontsize)
            ax_drift.grid(True, color = '#DBDBDB', alpha = 0.4)

            data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
            angular_position_SA = data['angular_position_SA']
            angular_position_SB = data['angular_position_SB']
            time_SA = data['time_SA']
            time_SB = data['time_SB']

            #speed_SA = data['speed_SA']
            #speed_SB = data['speed_SB']
            #eccentricity = data['angular_position_SA']

            scans = len(angular_position_SA)
            values = range(700)
            jet = cm = plt.get_cmap('jet')
            cNorm = colors.Normalize(vmin=0, vmax=values[-1])
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            N = 30


            for s in range(0,scans):
                #try:
                if i == 1:
                    angular_position_SA[s] = np.pi/2 - angular_position_SA[s]
                    angular_position_SB[s] = np.pi/2 - angular_position_SB[s]
                    #eccentricity[s] = -eccentricity[s]

                if projected == True:
                    angular_position_SA[s] = utils.do_projection(configuration.calib_fork_length,
                                                              configuration.calib_rotation_offset,
                                                              configuration.calib_fork_phase, angular_position_SA[s])

                    angular_position_SB[s] = utils.do_projection(configuration.calib_fork_length,
                                                              configuration.calib_rotation_offset,
                                                              configuration.calib_fork_phase, angular_position_SB[s])


                speed_SA = 1e-3*np.divide(np.diff(angular_position_SA[s]), np.diff(time_SA[s]))

                if projected == True:
                    if i ==0:
                        speed_SA = -speed_SA
                else:
                    speed_SA = 1e3*speed_SA
                    if i ==1:
                        speed_SA = -speed_SA

                # Calculation of Eccentricity
                P_B_R = utils.resample([time_SB[s],angular_position_SB[s]], [time_SA[s],angular_position_SA[s]])
                eccentricity = np.subtract(angular_position_SA[s], P_B_R[1]) / 2

                colorVal = scalarMap.to_rgba(values[counter])
                speed = np.convolve(speed_SA, np.ones((N,)) / N, mode='valid')
                counter = counter + 1

                ax_pos.plot(time_SA[s],angular_position_SA[s], color=colorVal, linewidth=0.8)
                ax_speed.plot(time_SA[s][0:speed.size], 1e3*speed, color=colorVal, linewidth=0.8)

                if projected == False:
                    eccentricity= 1e6*eccentricity
                else:
                    eccentricity= 1e3*eccentricity

                ax_eccentricity.plot(angular_position_SA[s],eccentricity, color=colorVal, linewidth=0.8)

                #RDS
                # offset = 100
                # DistancesA = np.diff(time_SA[s][offset:time_SA[s].size - 1 - offset])
                # DistancesB = np.diff(time_SB[s][offset:time_SB[s].size - 1 - offset])
                #
                # RDS_A = []
                # RDS_B = []
                #
                # previous_periods = 4
                #
                # SSL_A = 0
                # DSL_A = 0
                # TSL_A = 0
                # SSL_B = 0
                # DSL_B = 0
                # TSL_B = 0
                #
                # if i==0:
                #     MaxlLengthA = len(np.where(np.asarray(time_SA[s])<40)[0])
                #     MaxlLengthB = len(np.where(np.asarray(time_SB[s])<40)[0])
                #
                # else:
                #     MaxlLengthA = len(np.where(np.asarray(time_SA[s])<400)[0])
                #     MaxlLengthB = len(np.where(np.asarray(time_SA[s])<400)[0])
                #
                #
                # for c in np.arange(previous_periods,MaxlLengthA):
                #     Value = DistancesA[c] / np.mean(DistancesA[c - previous_periods:c - 1])
                #     RDS_A.append(Value)
                #
                #     if (Value > configuration.ops_relative_distance_correction_prameters[0]) and (Value < configuration.ops_relative_distance_correction_prameters[1]):
                #         SSL_A = SSL_A + 1
                #     if (Value > configuration.ops_relative_distance_correction_prameters[1]) and (Value < configuration.ops_relative_distance_correction_prameters[2]):
                #         DSL_A = DSL_A + 1
                #     if (Value > configuration.ops_relative_distance_correction_prameters[2]):
                #         TSL_A = TSL_A + 1
                #
                # for c in np.arange(previous_periods,MaxlLengthB):
                #     Value = DistancesB[c] / np.mean(DistancesB[c - previous_periods:c - 1])
                #     RDS_B.append(Value)
                #     if (Value > configuration.ops_relative_distance_correction_prameters[0]) and (
                #         Value < configuration.ops_relative_distance_correction_prameters[1]):
                #         SSL_B = SSL_B + 1
                #     if (Value > configuration.ops_relative_distance_correction_prameters[1]) and (
                #         Value < configuration.ops_relative_distance_correction_prameters[2]):
                #         DSL_B = DSL_B + 1
                #     if (Value > configuration.ops_relative_distance_correction_prameters[2]):
                #         TSL_B = TSL_B + 1
                #
                # #RDS_A = np.divide(DistancesA[1:DistancesA.size], DistancesA[0:DistancesA.size - 1])
                # #RDS_B = np.divide(DistancesB[1:DistancesB.size], DistancesB[0:DistancesB.size - 1])
                #
                # ax_rds.plot(time_SA[s][0:len(RDS_A)], RDS_A, '.', color='blue', label = 'Sensor A - Total:' + str(MaxlLengthA) + ' SSL:' + str(SSL_A) + ' DSL:' + str(DSL_A) + ' TSL:' + str(TSL_A))
                # ax_rds.plot(time_SB[s][0:len(RDS_B)], RDS_B, '.', color='red', label = 'Sensor B - Total:' + str(MaxlLengthB) + ' SSL:' + str(SSL_B) + ' DSL:' + str(DSL_B) + ' TSL:' + str(TSL_B))
                #     #ax_rds.legend()
                # #except:
                # #    pass


                # Disk Drift

                TimeIn = 29.6
                TimeOut = 374.8

                if i==0:
                    TimeZero = TimeIn
                else:
                    TimeZero = TimeOut

                Index = np.where(time_SA[s]>TimeZero)[0][0]
                Position_Zero.append(angular_position_SA[s][Index])

        ax_drift.plot(Position_Zero,'ob')

                #if s == 6:
                #break

    superplot.tight_layout()
    plt.show()

# MAIN PROGRAM STARTS HERE:
# Configuration and Data objects
configuration = Configuration.Configuration()
configuration.app_datapath = 'G:/Projects/BWS_Calibrations/Tunnel_Tests/2018_10_17_PS_PXBWSRB011_CR000001_MD_TOF'

# Make file list from folder content (sorted)
file_list = utils.mat_list_from_folder_sorted(configuration.app_datapath)

# Extract only Measurement Conditions
#process_only_meas_cond(configuration, file_list)
#plot_only_meas_cond(configuration)

# Process position data and save on files
#process_ops_and_save(configuration, file_list)

# Process PMT profiles and save on files
process_amplitudes_and_save(configuration, file_list)
#plot_report(configuration)

# Plot data analysis
#plot_report_position(configuration, projected = True)
