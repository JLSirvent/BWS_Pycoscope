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


from __future__ import unicode_literals
import configparser
import os
import utils
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QLineEdit, QHBoxLayout, QComboBox, QPushButton, QButtonGroup, QRadioButton, QListWidget, QProgressBar, QCheckBox


class QButtonsSet(QWidget):

    def __init__(self, parent=None):
        '''
        QWidget containing some calibration info
        :param parent:
        '''

        super(QButtonsSet, self).__init__(parent=None)

        # self.main_widget = QWidget(self)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Declaration of components

        self.scope_config_box = QGroupBox('Scopes Config.')
        self.scope_connect_btn = QPushButton('Connect')
        self.scope_connect_status = QLabel('OFF')
        self.scope_connect_status.setAlignment(QtCore.Qt.AlignCenter)
        self.scope_connect_status.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')
        self.scope_connect_btn.setStyleSheet('QPushButton {font: bold 12px;}')

        self.cycle_selector_box = QGroupBox('Scanner Trigger')
        self.cycle_selector_LTIM_ONOFF = QPushButton('ON/OFF')
        self.cycle_selector_LTIM_ONOFF_State = QLabel('OFF')
        self.cycle_selector_LTIM_ONOFF_State.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')
        self.cycle_selector_combo =  QComboBox()
        self.cycle_selector_dly_lbl = QLabel('Acq. Delay (ms):')
        self.cycle_selector_dly_txt = QLineEdit()
        self.cycle_selector_curr_dly = QLabel('Current Dly:')
        self.cycle_selector_curr_dly.setStyleSheet('QLabel {font: bold 11px; text-align: centre;}')
        self.cycle_selector_last_ts = QLabel('Last CycleStamp:')
        self.cycle_selector_last_ts.setStyleSheet('QLabel {font: bold 11px; text-align: centre;}')


        self.acquisition_launch_box = QGroupBox('Acquisition')
        self.acquisition_mode_box =  QGroupBox('Acquisition Mode')
        self.acquisition_mode_continuous = QRadioButton('Continuous')
        self.acquisition_mode_single = QRadioButton('Single')
        self.acquisition_mode_single.setChecked(True)
        self.acquisition_mode_btn_grp = QButtonGroup()
        self.acquisition_mode_btn_grp.addButton(self.acquisition_mode_continuous)
        self.acquisition_mode_btn_grp.addButton(self.acquisition_mode_single)
        self.acquisition_launch_button = QPushButton('Launch Acquisition!')
        self.acquisition_launch_button.setStyleSheet('QPushButton {font: bold 14px;}')
        self.acquisition_launch_status = QLabel('IDLE')
        self.acquisition_launch_status.setAlignment(QtCore.Qt.AlignCenter)
        self.acquisition_launch_status.setStyleSheet('QLabel {background-color: green; font: bold 14px; text-align: center;}')

        self.updater_box = QGroupBox('Updater')
        self.updater_profile = QCheckBox('Profile')
        self.updater_raw = QCheckBox('Raw')
        self.updater_motion = QCheckBox('Motion')
        self.updater_rds = QCheckBox('RDS')

        self.dataset_box = QGroupBox('Available Dataset')
        self.dataset_list = QListWidget()

        # Components layout construction

        # Connect Buttons Layout
        self.scopes_connect_layout = QHBoxLayout()
        self.scopes_connect_layout.addWidget(self.scope_connect_btn)
        self.scopes_connect_layout.addWidget(self.scope_connect_status)
        self.scope_config_box.setLayout(self.scopes_connect_layout)

        # Cycle Selector
        self.cycle_selector_box_layout_0 = QHBoxLayout()
        self.cycle_selector_box_layout_0.addWidget(self.cycle_selector_LTIM_ONOFF)
        self.cycle_selector_box_layout_0.addWidget(self.cycle_selector_LTIM_ONOFF_State)
        self.cycle_selector_box_layout_1 = QHBoxLayout()
        self.cycle_selector_box_layout_1.addWidget(self.cycle_selector_dly_lbl)
        self.cycle_selector_box_layout_1.addWidget(self.cycle_selector_dly_txt)
        self.cycle_selector_box_layout = QVBoxLayout()
        self.cycle_selector_box_layout.addLayout(self.cycle_selector_box_layout_0)
        self.cycle_selector_box_layout.addWidget(self.cycle_selector_combo)
        self.cycle_selector_box_layout.addLayout(self.cycle_selector_box_layout_1)
        self.cycle_selector_box_layout.addWidget(self.cycle_selector_curr_dly)
        self.cycle_selector_box_layout.addWidget(self.cycle_selector_last_ts)
        self.cycle_selector_box.setLayout(self.cycle_selector_box_layout)

        # General Scope Config Layout

        # Acquisition Mode
        self.acquisition_mode_box_layout = QHBoxLayout(self)
        self.acquisition_mode_box_layout.addWidget(self.acquisition_mode_continuous)
        self.acquisition_mode_box_layout.addWidget(self.acquisition_mode_single)
        self.acquisition_mode_box.setLayout(self.acquisition_mode_box_layout)

        self.acquisition_launch_btn_layout = QHBoxLayout()
        self.acquisition_launch_btn_layout.addWidget(self.acquisition_launch_button)
        self.acquisition_launch_btn_layout.addWidget(self.acquisition_launch_status)

        self.acquisition_launch_box_layout = QVBoxLayout(self)
        self.acquisition_launch_box_layout.addWidget(self.acquisition_mode_box)
        self.acquisition_launch_box_layout.addLayout(self.acquisition_launch_btn_layout)
        self.acquisition_launch_box.setLayout(self.acquisition_launch_box_layout)

        # Updater
        self.updater_box_layout = QHBoxLayout(self)
        self.updater_box_layout.addWidget(self.updater_profile)
        self.updater_box_layout.addWidget(self.updater_raw)
        self.updater_box_layout.addWidget(self.updater_motion)
        self.updater_box_layout.addWidget(self.updater_rds)
        self.updater_box.setLayout(self.updater_box_layout)

        # FileList
        self.dataset_box_layout = QVBoxLayout(self)
        self.dataset_box_layout.addWidget(self.dataset_list)
        self.dataset_box.setLayout(self.dataset_box_layout)

        # Whole Window Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scope_config_box)
        main_layout.addWidget(self.cycle_selector_box)
        main_layout.addWidget(self.acquisition_launch_box)
        main_layout.addWidget(self.updater_box)
        main_layout.addWidget(self.dataset_box)
        self.setLayout(main_layout)
        #self.setFixedWidth(250)

        # Some actions

    def update_file_list(self,path):
        self.dataset_list.clear()
        files = utils.mat_list_from_folder_sorted(path)
        #self.dataset_list.addItems(files)
        Counter = 1
        for singlefile in files:
            FileSplit = singlefile.split('\\')
            self.dataset_list.addItem('#' + str(Counter) + '   ' + FileSplit[-1].split('.mat')[0])
            Counter = Counter + 1

    def set_defaults_at_startup(self,config):


        if config.system == 'PSB':
            self.cycle_selector_combo.addItems(['PSB.USER.ZERO', 'PSB.USER.AD', 'PSB.USER.EAST1', 'PSB.USER.EAST2',
                                                'PSB.USER.LHC1A', 'PSB.USER.LHC1B', 'PSB.USER.LHC2A', 'PSB.USER.LHC2B',
                                                'PSB.USER.LHC3', 'PSB.USER.LHC4', 'PSB.USER.LHCINDIV', 'PSB.USER.LHCPROBE',
                                                'PSB.USER.MD1', 'PSB.USER.MD2', 'PSB.USER.MD3', 'PSB.USER.MD4',
                                                'PSB.USER.MD5', 'PSB.USER.MD6', 'PSB.USER.NORMGPS', 'PSB.USER.NORMHRS',
                                                'PSB.USER.SFTPRO1', 'PSB.USER.SFTPRO2', 'PSB.USER.STAGISO', 'PSB.USER.TOF'])
        if config.system == 'PS':
            self.cycle_selector_combo.addItems(['Select Cycle'])
        if config.system == 'SPS':
            self.cycle_selector_combo.addItems(['SPS.USER.ZERO','SPS.USER.AWAKE1', 'SPS.USER.AWAKE2', 'SPS.USER.HIRADMT1',
                                                'SPS.USER.HIRADMT2', 'SPS.USER.LHC1', 'SPS.USER.LHC2', 'SPS.USER.LHC25NS',
                                                'SPS.USER.LHC3', 'SPS.USER.LHC4', 'SPS.USER.LHC50NS', 'SPS.USER.LHCINDIV',
                                                'SPS.USER.LHCION1', 'SPS.USER.LHCION2', 'SPS.USER.LHCION3', 'SPS.USER.LHCION4',
                                                'SPS.USER.LHCMD1', 'SPS.USER.LHCMD2', 'SPS.USER.LHCMD3', 'SPS.USER.LHCMD4',
                                                'SPS.USER.LHCPILOT', 'SPS.USER.MD1', 'SPS.USER.MD2', 'SPS.USER.MD3',
                                                'SPS.USER.MD4', 'SPS.USER.SFTION1', 'SPS.USER.SFTION2', 'SPS.USER.SFTION3',
                                                'SPS.USER.SFTPRO1', 'SPS.USER.SFTPRO2', 'SPS.USER.SFTPRO3'])
