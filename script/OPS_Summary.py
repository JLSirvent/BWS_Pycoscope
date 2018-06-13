import sys
sys.path.append('../gui')
sys.path.append('../lib')
import numpy as np
import scipy.io as sio
import ops_processing, utils
import Configuration, DataScan, DataScan_Processed

from matplotlib import cm as cmx
from matplotlib import pyplot as plt
from matplotlib import colors as colors

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

    InfoData_CycleStamp=[]
    InfoData_TimeStamp=[]
    InfoData_Filter_PRO=[]
    InfoData_HV=[]
    InfoData_CycleName = []
    InfoData_AcqDelay = []

    Amplitudes_IN = [np.ones(3),np.ones(100)]
    Amplitudes_OUT =[np.ones(3),np.ones(100)]
    Times_IN = [np.ones(3),np.ones(100)]
    Times_OUT =[np.ones(3),np.ones(100)]

    data_scan = DataScan.DataScan()
    cnt = 0
    total_files= len(file_list)

    for single_file in file_list:
        try:
            print("Completed:{}%".format(100*cnt/total_files))

            data_scan.load_data_v2(single_file)

            # Concatenate InfoData
            InfoData_CycleStamp.append(data_scan.InfoData_CycleStamp)
            InfoData_TimeStamp.append(data_scan.InfoData_TimeStamp)
            InfoData_Filter_PRO.append(data_scan.InfoData_Filter_PRO)
            InfoData_HV.append(data_scan.InfoData_HV)
            InfoData_CycleName.append(data_scan.InfoData_CycleName)
            InfoData_AcqDelay.append(data_scan.InfoData_AcqDelay)
            InfoData_MaxInt.append()
            InfoData_TotalQ.append()


        except:
            print('Error!')

    sio.savemat(configuration.app_datapath + '/Amplit_Processed_IN.mat',
                {'InfoData_CycleStamp': InfoData_CycleStamp,
                 'InfoData_TimeStamp': InfoData_TimeStamp,
                 'InfoData_Filter_PRO': InfoData_Filter_PRO,
                 'InfoData_HV': InfoData_HV,
                 'InfoData_CycleName': InfoData_CycleName,
                 'InfoData_AcqDelay': InfoData_AcqDelay,
                 'Amplitudes': Amplitudes_IN,
                 'Times': Times_IN},
                do_compression=True)

    sio.savemat(configuration.app_datapath + '/Amplit_Processed_OUT.mat',
                {'InfoData_CycleStamp': InfoData_CycleStamp,
                 'InfoData_TimeStamp': InfoData_TimeStamp,
                 'InfoData_Filter_PRO': InfoData_Filter_PRO,
                 'InfoData_HV': InfoData_HV,
                 'InfoData_CycleName': InfoData_CycleName,
                 'InfoData_AcqDelay': InfoData_AcqDelay,
                 'Amplitudes': Amplitudes_OUT,
                 'Times': Times_OUT},
                do_compression=True)

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
        if i == 0:
            filename = configuration.app_datapath + '/Processed_IN.mat'
            ax_pos = pos_in
            ax_speed = speed_in
            ax_eccentricity = eccentricity_in
            ax_rds = rds_in
            ax_drift=drift_in
            s_title = 'IN'
        else:
            filename = configuration.app_datapath + '/Processed_OUT.mat'
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
        values = range(scans + 1)
        jet = cm = plt.get_cmap('jet')
        cNorm = colors.Normalize(vmin=0, vmax=values[-1])
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
        N = 30

        Position_Zero=[]
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

            colorVal = scalarMap.to_rgba(values[s])
            speed = np.convolve(speed_SA, np.ones((N,)) / N, mode='valid')

            ax_pos.plot(time_SA[s],angular_position_SA[s], color=colorVal, linewidth=0.8)
            ax_speed.plot(time_SA[s][0:speed.size], 1e3*speed, color=colorVal, linewidth=0.8)

            if projected == False:
                eccentricity= 1e6*eccentricity
            else:
                eccentricity= 1e3*eccentricity

            ax_eccentricity.plot(angular_position_SA[s],eccentricity, color=colorVal, linewidth=0.8)

            #RDS
            offset = 100
            DistancesA = np.diff(time_SA[s][offset:time_SA[s].size - 1 - offset])
            DistancesB = np.diff(time_SB[s][offset:time_SB[s].size - 1 - offset])

            RDS_A = []
            RDS_B = []
            previous_periods = 4

            SSL_A = 0
            DSL_A = 0
            TSL_A = 0
            SSL_B = 0
            DSL_B = 0
            TSL_B = 0

            if i==0:
                MaxlLengthA = len(np.where(np.asarray(time_SA[s])<40)[0])
                MaxlLengthB = len(np.where(np.asarray(time_SB[s])<40)[0])

            else:
                MaxlLengthA = len(np.where(np.asarray(time_SA[s])<400)[0])
                MaxlLengthB = len(np.where(np.asarray(time_SA[s])<400)[0])


            for c in np.arange(previous_periods,MaxlLengthA):
                Value = DistancesA[c] / np.mean(DistancesA[c - previous_periods:c - 1])
                RDS_A.append(Value)

                if (Value > configuration.ops_relative_distance_correction_prameters[0]) and (Value < configuration.ops_relative_distance_correction_prameters[1]):
                    SSL_A = SSL_A + 1
                if (Value > configuration.ops_relative_distance_correction_prameters[1]) and (Value < configuration.ops_relative_distance_correction_prameters[2]):
                    DSL_A = DSL_A + 1
                if (Value > configuration.ops_relative_distance_correction_prameters[2]):
                    TSL_A = TSL_A + 1

            for c in np.arange(previous_periods,MaxlLengthB):
                Value = DistancesB[c] / np.mean(DistancesB[c - previous_periods:c - 1])
                RDS_B.append(Value)
                if (Value > configuration.ops_relative_distance_correction_prameters[0]) and (
                    Value < configuration.ops_relative_distance_correction_prameters[1]):
                    SSL_B = SSL_B + 1
                if (Value > configuration.ops_relative_distance_correction_prameters[1]) and (
                    Value < configuration.ops_relative_distance_correction_prameters[2]):
                    DSL_B = DSL_B + 1
                if (Value > configuration.ops_relative_distance_correction_prameters[2]):
                    TSL_B = TSL_B + 1

            #RDS_A = np.divide(DistancesA[1:DistancesA.size], DistancesA[0:DistancesA.size - 1])
            #RDS_B = np.divide(DistancesB[1:DistancesB.size], DistancesB[0:DistancesB.size - 1])

            ax_rds.plot(time_SA[s][0:len(RDS_A)], RDS_A, '.', color='blue', label = 'Sensor A - Total:' + str(MaxlLengthA) + ' SSL:' + str(SSL_A) + ' DSL:' + str(DSL_A) + ' TSL:' + str(TSL_A))
            ax_rds.plot(time_SB[s][0:len(RDS_B)], RDS_B, '.', color='red', label = 'Sensor B - Total:' + str(MaxlLengthB) + ' SSL:' + str(SSL_B) + ' DSL:' + str(DSL_B) + ' TSL:' + str(TSL_B))
                #ax_rds.legend()
            #except:
            #    pass
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

# Make file list from folder content (sorted)
file_list = utils.mat_list_from_folder_sorted(configuration.app_datapath)

# Process position data and save on files
process_ops_and_save(configuration, file_list)

# Plot data analysis
plot_position_summary(configuration, projected = True)
