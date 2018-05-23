from __future__ import unicode_literals

import time
import datetime
import numpy as np
import os
import scipy.io as sio

from ctypes import *
from PyQt5 import QtCore
import matplotlib.pyplot as plt


class FESAControlsUpdater(QtCore.QThread):

    notifyState = QtCore.pyqtSignal(str)
    fileReady = QtCore.pyqtSignal(str)

    def __init__(self, tab_buttons_pannel, path, parent=None):

        self.tab_buttons_pannel = tab_buttons_pannel
        self.path0 = path
        super(FESAControlsUpdater, self).__init__(parent)

    def run(self):

        while True:
            time.sleep(0.5)
            path = self.path0 + '/test_g.mat'
            path2 = self.path0 + '/test_ts.mat'

            try:
                data = sio.loadmat(path, struct_as_record=False, squeeze_me=True)

                # HV Controls

                if data['HV_ENABLE_GET'] == 1:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ONOFF_State.setText('ON')
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ONOFF_State.setStyleSheet(
                        'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                else:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ONOFF_State.setText('OFF')
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ONOFF_State.setStyleSheet(
                        'QLabel {background-color: red; font: bold 14px; text-align: center;}')

                self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_MeasV_edit.setText('Voltage: ' + '{0:.1f}'.format(data['HV_VOLTAGE_GET']) + 'V')
                self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_MeasI_edit.setText('Current: ' + '{0:.1f}'.format(1e6*data['HV_CURRENT_GET']) + 'uA')

                # FW Controls
                if data['FW_ENABLE_GET'] == 1:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_ONOFF_State.setText('ON')
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_ONOFF_State.setStyleSheet(
                        'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                else:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_ONOFF_State.setText('OFF')
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_ONOFF_State.setStyleSheet(
                        'QLabel {background-color: red; font: bold 14px; text-align: center;}')

                if data['FW_MOTOR_STAT'] == 1:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Motor.setStyleSheet(
                        'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                else:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Motor.setStyleSheet(
                        'QLabel {background-color: red; font: bold 14px; text-align: center;}')

                if data['FW_SWITCH_PLUS'] == 1:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Plus.setStyleSheet(
                        'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                else:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Plus.setStyleSheet(
                        'QLabel {background-color: red; font: bold 14px; text-align: center;}')

                if data['FW_SWITCH_MINUS'] == 1:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Minus.setStyleSheet(
                        'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                else:
                    self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Minus.setStyleSheet(
                        'QLabel {background-color: red; font: bold 14px; text-align: center;}')

                self.tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Position_lbl.setText('Current Pos.: ' + str((data['FW_POSITION_GET'])))

                # LTIM Controls:
                if data['LTIM_ENABLE_GET'] == 1:
                    self.tab_buttons_pannel.buttons_pannel.cycle_selector_LTIM_ONOFF_State.setText('ON')
                    self.tab_buttons_pannel.buttons_pannel.cycle_selector_LTIM_ONOFF_State.setStyleSheet(
                        'QLabel {background-color: green; font: bold 14px; text-align: center;}')
                else:
                    self.tab_buttons_pannel.buttons_pannel.cycle_selector_LTIM_ONOFF_State.setText('OFF')
                    self.tab_buttons_pannel.buttons_pannel.cycle_selector_LTIM_ONOFF_State.setStyleSheet(
                        'QLabel {background-color: red; font: bold 14px; text-align: center;}')

                self.tab_buttons_pannel.buttons_pannel.cycle_selector_curr_dly.setText('Current Dly:' + str(data['LTIM_ACQDELAY_GET']))
            except:
                print('Info file #1 reading error on AFS')

            try:
                data2 = sio.loadmat(path2, struct_as_record=False, squeeze_me=True)
                self.tab_buttons_pannel.buttons_pannel.cycle_selector_last_ts.setText(
                    'Last CycleStamp:\n' + str(data2['LTIM_CYCLESTAMP']))
            except:
                print('Info file #2 reading error on AFS')


def SendFESAcommands(tab_buttons_pannel, path, action=''):

    path = '/test_s.mat'
    data = sio.loadmat(path, struct_as_record=False, squeeze_me=True)

    if action == 'HV_ONOFF':
        if tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ONOFF_State.text() == 'OFF':
            data['HV_ENABLE_SET'] = 1
        else:
            data['HV_ENABLE_SET'] = 0

    try:
        data['HV_VOLTAGE_SET'] = int(float(tab_buttons_pannel.buttons_pannel_config.acquisition_config_HV_ControlV_txt.text()))
    except:
        data['HV_VOLTAGE_SET'] = 0

    if action == 'FW_ONOFF':
        if tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_ONOFF_State.text() == 'OFF':
            data['FW_ENABLE_SET'] = 1
        else:
            data['FW_ENABLE_SET'] = 0

    if action == 'FW_DoHome':
        data['FW_HOME_SET'] = 1

    data['FW_POSITION_SET'] = tab_buttons_pannel.buttons_pannel_config.acquisition_config_FW_Position_set.currentIndex()

    if action == 'LTIM_ONOFF':
        if tab_buttons_pannel.buttons_pannel.cycle_selector_LTIM_ONOFF_State.text() == 'OFF':
            data['LTIM_ENABLE_SET'] = 1
        else:
            data['LTIM_ENABLE_SET'] = 0

    data['LTIM_CYCLENAME'] = tab_buttons_pannel.buttons_pannel.cycle_selector_combo.currentText()

    try:
        data['LTIM_ACQDELAY_SET'] = int(float(tab_buttons_pannel.buttons_pannel.cycle_selector_dly_txt.text()))
    except:
        data['LTIM_ACQDELAY_SET'] = 0

    if action == 'LTIM_ON':
        data['LTIM_ENABLE_SET'] = 1

    if action == 'LTIM_OFF':
        data['LTIM_ENABLE_SET'] = 0

    sio.savemat(path, data, do_compression=True)

