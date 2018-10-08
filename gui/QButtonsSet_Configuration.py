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
import FESAControlsUpdater
import scipy.io as sio
import numpy as np

class QButtonsSet_Configuration(QWidget):

    def __init__(self, parent=None):
        '''
        QWidget containing some calibration info
        :param parent:
        '''

        super(QButtonsSet_Configuration, self).__init__(parent=None)

        # self.main_widget = QWidget(self)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Declaration of components

        self.scope_config_box = QGroupBox('Scopes Config.')

        self.scope_config_box_pmt = QGroupBox('PMTs')
        self.scope_config_box_pmt_ch1_lbl = QLabel('CH1')
        self.scope_config_box_pmt_ch1 = QComboBox()
        self.add_ranges(self.scope_config_box_pmt_ch1)
        self.scope_config_box_pmt_ch2_lbl = QLabel('CH2')
        self.scope_config_box_pmt_ch2 = QComboBox()
        self.add_ranges(self.scope_config_box_pmt_ch2)
        self.scope_config_box_pmt_ch3_lbl = QLabel('CH3')
        self.scope_config_box_pmt_ch3 = QComboBox()
        self.add_ranges(self.scope_config_box_pmt_ch3)
        self.scope_config_box_pmt_ch4_lbl = QLabel('CH4')
        self.scope_config_box_pmt_ch4 = QComboBox()
        self.add_ranges(self.scope_config_box_pmt_ch4)

        self.scope_config_box_ops = QGroupBox('Position Sensors')
        self.scope_config_box_ops_ch1_lbl = QLabel('CH1')
        self.scope_config_box_ops_ch1 = QComboBox()
        self.add_ranges(self.scope_config_box_ops_ch1)
        self.scope_config_box_ops_ch2_lbl = QLabel('CH2')
        self.scope_config_box_ops_ch2 = QComboBox()
        self.add_ranges(self.scope_config_box_ops_ch2)

        self.acquisition_config_box = QGroupBox('Acquisiton Timming Config. (ms)')
        self.acquisition_config_box_pmt = QGroupBox('Timming')

        self.acquisition_config_pmt_in_start_lbl = QLabel('Start')
        self.acquisition_config_pmt_in_start_txt = QLineEdit()
        self.acquisition_config_pmt_in_end_lbl = QLabel('End')
        self.acquisition_config_pmt_in_end_txt = QLineEdit()
        self.acquisition_config_pmt_out_start_lbl = QLabel('Start')
        self.acquisition_config_pmt_out_start_txt = QLineEdit()
        self.acquisition_config_pmt_out_end_lbl = QLabel('End')
        self.acquisition_config_pmt_out_end_txt = QLineEdit()

        self.acquisition_config_box_ops =  QGroupBox('Timming')
        self.acquisition_config_ops_in_start_lbl= QLabel('Start')
        self.acquisition_config_ops_in_start_txt = QLineEdit()
        self.acquisition_config_ops_in_end_lbl= QLabel('End')
        self.acquisition_config_ops_in_end_txt = QLineEdit()
        self.acquisition_config_ops_in_ref_lbl= QLabel('Ref')
        self.acquisition_config_ops_in_ref_txt = QLineEdit()
        self.acquisition_config_ops_out_start_lbl= QLabel('Start')
        self.acquisition_config_ops_out_start_txt = QLineEdit()
        self.acquisition_config_ops_out_end_lbl= QLabel('End')
        self.acquisition_config_ops_out_end_txt = QLineEdit()
        self.acquisition_config_ops_out_ref_lbl= QLabel('Ref')
        self.acquisition_config_ops_out_ref_txt = QLineEdit()

        self.acquisition_config_HV_box =  QGroupBox('High Voltage')
        self.acquisition_config_HV_ONOFF = QPushButton('ON/OFF')
        self.acquisition_config_HV_ControlV_lbl = QLabel('Control Voltage: ')
        self.acquisition_config_HV_ONOFF_State = QLabel('OFF')
        self.acquisition_config_HV_ONOFF_State.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')
        self.acquisition_config_HV_ControlV_txt = QLineEdit()
        self.acquisition_config_HV_MeasV_edit = QLabel('Voltage: 0 V')
        self.acquisition_config_HV_MeasV_edit.setStyleSheet('QLabel {font: bold 11px; text-align: centre;}')
        self.acquisition_config_HV_MeasI_edit = QLabel('Current: 0 uA')
        self.acquisition_config_HV_MeasI_edit.setStyleSheet('QLabel {font: bold 11px; text-align: centre;}')

        self.acquisition_config_FW_box = QGroupBox('Filter Wheel')
        self.acquisition_config_FW_DoHome = QPushButton('Do Home')
        self.acquisition_config_FW_ONOFF = QPushButton('ON/OFF')
        self.acquisition_config_FW_ONOFF_State = QLabel('OFF')
        self.acquisition_config_FW_ONOFF_State.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')
        self.acquisition_config_FW_Position_lbl = QLabel('Current Pos.: ')
        self.acquisition_config_FW_Position_lbl.setStyleSheet('QLabel {font: bold 11px; text-align: centre;}')
        self.acquisition_config_FW_Position_set = QComboBox()

        #   ZMX+
        #self.acquisition_config_FW_Position_set.addItems(['P0: Closed', 'P1: Closed', 'P2: 0.2 %', 'P3: 0.5 %', 'P4: 2 %', 'P5: 5 %', 'P6: 20 %', 'P7: Open'])

        #   MIDI
        self.acquisition_config_FW_Position_set.addItems(['P0: Open', 'P1: 20 %', 'P2: 5 %', 'P3: 2 %', 'P4: 0.5 %', 'P5: 0.2 %', 'P6: Closed %', 'P7: Closed'])

        self.acquisition_config_FW_Motor = QLabel('Motor')
        self.acquisition_config_FW_Plus = QLabel('+')
        self.acquisition_config_FW_Minus = QLabel('-')
        self.acquisition_config_FW_Motor.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')
        self.acquisition_config_FW_Plus.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')
        self.acquisition_config_FW_Minus.setStyleSheet('QLabel {background-color: red; font: bold 14px; text-align: center;}')

        self.acquisition_config_Det_box = QGroupBox('Detector Config.')


        # Components layout construction
        # DETECTOR SYSTEM CONFIGURATION
        # Filter Wheel Layout
        self.acquisition_config_FW_box_layout = QVBoxLayout()
        self.acquisition_config_FW_box_layout.addWidget(self.acquisition_config_FW_DoHome)
        self.acquisition_config_FW_box_layout2 = QHBoxLayout()
        self.acquisition_config_FW_box_layout2.addWidget(self.acquisition_config_FW_ONOFF)
        self.acquisition_config_FW_box_layout2.addWidget(self.acquisition_config_FW_ONOFF_State)
        self.acquisition_config_FW_box_layout3 = QHBoxLayout()
        self.acquisition_config_FW_box_layout3.addWidget( self.acquisition_config_FW_Position_set)
        self.acquisition_config_FW_box_layout3.addWidget(self.acquisition_config_FW_Position_lbl)
        self.acquisition_config_FW_box_layout4 = QHBoxLayout()
        self.acquisition_config_FW_box_layout4.addWidget(self.acquisition_config_FW_Motor)
        self.acquisition_config_FW_box_layout4.addWidget(self.acquisition_config_FW_Plus)
        self.acquisition_config_FW_box_layout4.addWidget(self.acquisition_config_FW_Minus)
        self.acquisition_config_FW_box_layout.addLayout(self.acquisition_config_FW_box_layout2)
        self.acquisition_config_FW_box_layout.addLayout(self.acquisition_config_FW_box_layout3)
        self.acquisition_config_FW_box_layout.addLayout(self.acquisition_config_FW_box_layout4)
        self.acquisition_config_FW_box.setLayout(self.acquisition_config_FW_box_layout)

        # High Voltage Layout
        self.acquisition_config_HV_box_layout = QVBoxLayout()
        self.acquisition_config_HV_box_layout1 = QHBoxLayout()
        self.acquisition_config_HV_box_layout1.addWidget(self.acquisition_config_HV_ONOFF)
        self.acquisition_config_HV_box_layout1.addWidget(self.acquisition_config_HV_ONOFF_State)

        self.acquisition_config_HV_box_layout2 = QHBoxLayout()
        self.acquisition_config_HV_box_layout2.addWidget(self.acquisition_config_HV_ControlV_lbl)
        self.acquisition_config_HV_box_layout2.addWidget(self.acquisition_config_HV_ControlV_txt)

        self.acquisition_config_HV_box_layout3 = QHBoxLayout()
        self.acquisition_config_HV_box_layout3.addWidget(self.acquisition_config_HV_MeasV_edit)
        self.acquisition_config_HV_box_layout3.addWidget( self.acquisition_config_HV_MeasI_edit)

        self.acquisition_config_HV_box_layout.addLayout(self.acquisition_config_HV_box_layout1)
        self.acquisition_config_HV_box_layout.addLayout(self.acquisition_config_HV_box_layout2)
        self.acquisition_config_HV_box_layout.addLayout(self.acquisition_config_HV_box_layout3)
        self.acquisition_config_HV_box.setLayout(self.acquisition_config_HV_box_layout)



        # General Layout
        self.acquisition_config_Det_box_layout = QVBoxLayout()
        #self.acquisition_config_Det_box_layout.addWidget(self.acquisition_config_FW_box)
        self.acquisition_config_Det_box_layout.addWidget(self.acquisition_config_HV_box)
        self.acquisition_config_Det_box.setLayout(self.acquisition_config_Det_box_layout)

        # ACQUISITION TIMMING CONFIGURATION

        # Acquisition PMT
        self.acquisition_config_box_pmt_layout = QVBoxLayout(self)
        self.acquisition_config_box_pmt_layout1 = QHBoxLayout(self)
        self.acquisition_config_box_pmt_layout1.addWidget(self.acquisition_config_pmt_in_start_lbl)
        self.acquisition_config_box_pmt_layout1.addWidget(self.acquisition_config_pmt_in_start_txt)
        self.acquisition_config_box_pmt_layout1.addWidget(self.acquisition_config_pmt_in_end_lbl)
        self.acquisition_config_box_pmt_layout1.addWidget(self.acquisition_config_pmt_in_end_txt)
        self.acquisition_config_box_pmt_layout2 = QHBoxLayout(self)
        self.acquisition_config_box_pmt_layout2.addWidget(self.acquisition_config_pmt_out_start_lbl)
        self.acquisition_config_box_pmt_layout2.addWidget(self.acquisition_config_pmt_out_start_txt)
        self.acquisition_config_box_pmt_layout2.addWidget(self.acquisition_config_pmt_out_end_lbl)
        self.acquisition_config_box_pmt_layout2.addWidget(self.acquisition_config_pmt_out_end_txt)
        self.acquisition_config_box_pmt_layout.addLayout(self.acquisition_config_box_pmt_layout1)
        self.acquisition_config_box_pmt_layout.addLayout(self.acquisition_config_box_pmt_layout2)
        self.acquisition_config_box_pmt.setLayout(self.acquisition_config_box_pmt_layout)

        # Acquisition OPS
        self.acquisition_config_box_ops_layout = QVBoxLayout(self)
        self.acquisition_config_box_ops_layout1 = QHBoxLayout(self)
        self.acquisition_config_box_ops_layout1.addWidget(self.acquisition_config_ops_in_start_lbl)
        self.acquisition_config_box_ops_layout1.addWidget(self.acquisition_config_ops_in_start_txt)
        self.acquisition_config_box_ops_layout1.addWidget(self.acquisition_config_ops_in_end_lbl)
        self.acquisition_config_box_ops_layout1.addWidget(self.acquisition_config_ops_in_end_txt)
        self.acquisition_config_box_ops_layout1.addWidget(self.acquisition_config_ops_in_ref_lbl)
        self.acquisition_config_box_ops_layout1.addWidget(self.acquisition_config_ops_in_ref_txt)
        self.acquisition_config_box_ops_layout2 = QHBoxLayout(self)
        self.acquisition_config_box_ops_layout2.addWidget(self.acquisition_config_ops_out_start_lbl)
        self.acquisition_config_box_ops_layout2.addWidget(self.acquisition_config_ops_out_start_txt)
        self.acquisition_config_box_ops_layout2.addWidget(self.acquisition_config_ops_out_end_lbl)
        self.acquisition_config_box_ops_layout2.addWidget(self.acquisition_config_ops_out_end_txt)
        self.acquisition_config_box_ops_layout2.addWidget(self.acquisition_config_ops_out_ref_lbl)
        self.acquisition_config_box_ops_layout2.addWidget(self.acquisition_config_ops_out_ref_txt)
        self.acquisition_config_box_ops_layout.addLayout(self.acquisition_config_box_ops_layout1)
        self.acquisition_config_box_ops_layout.addLayout(self.acquisition_config_box_ops_layout2)
        self.acquisition_config_box_ops.setLayout(self.acquisition_config_box_ops_layout)


        # SCOPE CONFIGURATION

        # Scope config PMTs Layout
        self.scope_config_box_pmt_layout = QVBoxLayout(self)
        self.scope_config_box_pmt_layout1 = QHBoxLayout(self)
        self.scope_config_box_pmt_layout1.addWidget(self.scope_config_box_pmt_ch1_lbl)
        self.scope_config_box_pmt_layout1.addWidget(self.scope_config_box_pmt_ch2_lbl)
        self.scope_config_box_pmt_layout1.addWidget(self.scope_config_box_pmt_ch3_lbl)
        self.scope_config_box_pmt_layout1.addWidget(self.scope_config_box_pmt_ch4_lbl)

        self.scope_config_box_pmt_layout2 = QHBoxLayout(self)
        self.scope_config_box_pmt_layout2.addWidget(self.scope_config_box_pmt_ch1)
        self.scope_config_box_pmt_layout2.addWidget(self.scope_config_box_pmt_ch2)
        self.scope_config_box_pmt_layout2.addWidget(self.scope_config_box_pmt_ch3)
        self.scope_config_box_pmt_layout2.addWidget(self.scope_config_box_pmt_ch4)
        self.scope_config_box_pmt_layout.addLayout(self.scope_config_box_pmt_layout1)
        self.scope_config_box_pmt_layout.addLayout(self.scope_config_box_pmt_layout2)
        self.scope_config_box_pmt_layout.addWidget(self.acquisition_config_box_pmt)
        self.scope_config_box_pmt.setLayout(self.scope_config_box_pmt_layout)

        # Scope Config OPS Layout
        self.scope_config_box_ops_layout1 = QHBoxLayout()
        self.scope_config_box_ops_layout1.addWidget(self.scope_config_box_ops_ch1_lbl)
        self.scope_config_box_ops_layout1.addWidget(self.scope_config_box_ops_ch1)
        self.scope_config_box_ops_layout1.addWidget(self.scope_config_box_ops_ch2_lbl)
        self.scope_config_box_ops_layout1.addWidget(self.scope_config_box_ops_ch2)

        self.scope_config_box_ops_layout = QVBoxLayout(self)
        self.scope_config_box_ops_layout.addLayout(self.scope_config_box_ops_layout1)
        self.scope_config_box_ops_layout.addWidget(self.acquisition_config_box_ops)
        self.scope_config_box_ops.setLayout(self.scope_config_box_ops_layout)

        # General Scope Config Layout
        self.scope_config_box_layout = QVBoxLayout(self)
        self.scope_config_box_layout.addStretch(1)
        self.scope_config_box_layout.addWidget(self.scope_config_box_pmt)
        self.scope_config_box_layout.addWidget(self.scope_config_box_ops)
        self.scope_config_box.setLayout(self.scope_config_box_layout)

        # Whole Window Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.acquisition_config_Det_box)
        main_layout.addWidget(self.scope_config_box)
        self.setLayout(main_layout)
        #self.setFixedWidth(250)

    def add_ranges(self,ItemToLoad):
        ItemToLoad.addItems(['OFF', '50 mv', '100 mv', '200 mv', '500 mv', '1 v', '2 v'])

    def set_defaults_at_startup(self,config):
        self.acquisition_config_pmt_in_start_txt.setText(str(config.def_pmt_in_start))
        self.acquisition_config_pmt_in_end_txt.setText(str(config.def_pmt_in_end))
        self.acquisition_config_pmt_out_start_txt.setText(str(config.def_pmt_out_start))
        self.acquisition_config_pmt_out_end_txt.setText(str(config.def_pmt_out_end))

        self.acquisition_config_ops_in_start_txt.setText(str(config.def_ops_in_start))
        self.acquisition_config_ops_in_end_txt.setText(str(config.def_ops_in_end))
        self.acquisition_config_ops_in_ref_txt.setText(str(config.def_ops_in_ref))
        self.acquisition_config_ops_out_start_txt.setText(str(config.def_ops_out_start))
        self.acquisition_config_ops_out_end_txt.setText(str(config.def_ops_out_end))
        self.acquisition_config_ops_out_ref_txt.setText(str(config.def_ops_out_ref))

        self.scope_config_box_ops_ch1.setCurrentIndex(config.ps_pico_def_scale)
        self.scope_config_box_ops_ch2.setCurrentIndex(config.ps_pico_def_scale)

        self.scope_config_box_pmt_ch1.setCurrentIndex(config.pmt_pico_def_scale[0])
        self.scope_config_box_pmt_ch2.setCurrentIndex(config.pmt_pico_def_scale[1])
        self.scope_config_box_pmt_ch3.setCurrentIndex(config.pmt_pico_def_scale[2])
        self.scope_config_box_pmt_ch4.setCurrentIndex(config.pmt_pico_def_scale[3])

