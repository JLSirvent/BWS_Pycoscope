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
        self.acquisition_config_box_pmt = QGroupBox('PMTs')

        self.acquisition_config_pmt_in_start_lbl = QLabel('Start')
        self.acquisition_config_pmt_in_start_txt = QLineEdit()
        self.acquisition_config_pmt_in_end_lbl = QLabel('End')
        self.acquisition_config_pmt_in_end_txt = QLineEdit()
        self.acquisition_config_pmt_out_start_lbl = QLabel('Start')
        self.acquisition_config_pmt_out_start_txt = QLineEdit()
        self.acquisition_config_pmt_out_end_lbl = QLabel('End')
        self.acquisition_config_pmt_out_end_txt = QLineEdit()

        self.acquisition_config_box_ops =  QGroupBox('Position Sensors')
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

        self.dataset_box = QGroupBox('Available Dataset')
        self.dataset_list = QListWidget()

        # Components layout construction

        # SCOPE CONFIGURATION
        # Connect Buttons Layout
        self.scopes_connect_layout = QHBoxLayout()
        self.scopes_connect_layout.addWidget(self.scope_connect_btn)
        self.scopes_connect_layout.addWidget(self.scope_connect_status)

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
        self.scope_config_box_pmt.setLayout(self.scope_config_box_pmt_layout)

        # Scope Config OPS Layout
        self.scope_config_box_ops_layout = QHBoxLayout(self)
        self.scope_config_box_ops_layout.addWidget(self.scope_config_box_ops_ch1_lbl)
        self.scope_config_box_ops_layout.addWidget(self.scope_config_box_ops_ch1)
        self.scope_config_box_ops_layout.addWidget(self.scope_config_box_ops_ch2_lbl)
        self.scope_config_box_ops_layout.addWidget(self.scope_config_box_ops_ch2)
        self.scope_config_box_ops.setLayout(self.scope_config_box_ops_layout)

        # General Scope Config Layout
        self.scope_config_box_layout = QVBoxLayout(self)
        self.scope_config_box_layout.addStretch(1)
        self.scope_config_box_layout.addLayout(self.scopes_connect_layout)
        self.scope_config_box_layout.addWidget(self.scope_config_box_pmt)
        self.scope_config_box_layout.addWidget(self.scope_config_box_ops)
        self.scope_config_box.setLayout(self.scope_config_box_layout)

        # ACQUISITION CONFIGURATION

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

        # General Acquisition Config Layout
        self.acquisition_config_box_layout = QVBoxLayout(self)
        self.acquisition_config_box_layout.addWidget(self.acquisition_config_box_pmt)
        self.acquisition_config_box_layout.addWidget(self.acquisition_config_box_ops)
        self.acquisition_config_box.setLayout(self.acquisition_config_box_layout)

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

        # FileList
        self.dataset_box_layout = QVBoxLayout(self)
        self.dataset_box_layout.addWidget(self.dataset_list)
        self.dataset_box.setLayout(self.dataset_box_layout)

        # Whole Window Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scope_config_box)
        main_layout.addWidget(self.acquisition_config_box)
        main_layout.addWidget(self.acquisition_launch_box)
        main_layout.addWidget(self.dataset_box)
        self.setLayout(main_layout)
        self.setFixedWidth(250)

        # Some actions


    def add_ranges(self,ItemToLoad):
        ItemToLoad.addItems(['OFF', '50 mv', '100 mv', '200 mv', '500 mv', '1 v', '2 v'])

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

