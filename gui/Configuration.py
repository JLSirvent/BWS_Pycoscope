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

import configparser
import utils


class Configuration:

    def __init__(self):
        '''
        Configuration is an object containing the application configuraiton information. More convenient for data manipulation and access
        It collects the information form the data/configuration.cfg file
        '''

        # We use parameter file
        parameter_file = utils.resource_path('data/configuration.cfg')
        print(parameter_file)
        config = configparser.RawConfigParser()
        config.read(parameter_file)

        self.app_datapath = eval(config.get('Application Parameters', 'datapath'))
        self.info_datapath = eval(config.get('Application Parameters', 'info_datapath'))

        self.ps_pico_sn = eval(config.get('Scopes Config', 'ps_pico_sn'))
        self.ps_pico_def_scale = eval(config.get('Scopes Config', 'ps_pico_def_scale'))

        self.pmt_pico_sn = eval(config.get('Scopes Config', 'pmt_pico_sn'))
        self.pmt_pico_def_scale = eval(config.get('Scopes Config', 'pmt_pico_def_scale'))

        self.calib_fork_length = eval(config.get('CalibrationCurve', 'fork_length'))
        self.calib_rotation_offset = eval(config.get('CalibrationCurve', 'rotation_offset'))
        self.calib_fork_phase = eval(config.get('CalibrationCurve', 'fork_phase'))

        self.def_pmt_in_start = eval(config.get('Defaults', 'pmt_in_start'))
        self.def_pmt_in_end = eval(config.get('Defaults', 'pmt_in_stop'))
        self.def_ops_in_start = eval(config.get('Defaults', 'ops_in_start'))
        self.def_ops_in_end = eval(config.get('Defaults', 'ops_in_stop'))
        self.def_ops_in_ref = eval(config.get('Defaults', 'ops_in_ref'))

        self.def_pmt_out_start = eval(config.get('Defaults', 'pmt_out_start'))
        self.def_pmt_out_end = eval(config.get('Defaults', 'pmt_out_stop'))
        self.def_ops_out_start = eval(config.get('Defaults', 'ops_out_start'))
        self.def_ops_out_end = eval(config.get('Defaults', 'ops_out_stop'))
        self.def_ops_out_ref = eval(config.get('Defaults', 'ops_out_ref'))

        self.ops_prominence = eval(config.get('OPS processing parameters', 'prominence'))
        self.ops_slits_per_turn =  eval(config.get('OPS processing parameters', 'slits_per_turn'))
        self.ops_relative_distance_correction_prameters =  eval(config.get('OPS processing parameters', 'relative_distance_correction_prameters'))
        self.ops_camelback_threshold =  eval(config.get('OPS processing parameters', 'camelback_threshold'))
        self.ops_Compensate_Eccentricity =  eval(config.get('OPS processing parameters', 'Compensate_Eccentricity'))
        self.ops_low_pass_filter_freq =  eval(config.get('OPS processing parameters', 'low_pass_filter_freq'))

        self.pmt_filterfreq_rawview = eval(config.get('PMT processing parameters', 'filterfreq_rawview'))
        self.pmt_downsample_rawview = eval(config.get('PMT processing parameters', 'downsample_rawview'))

        self.pmt_filterfreq_profile = eval(config.get('PMT processing parameters', 'filterfreq_profile'))
        self.pmt_downsample_profile = eval(config.get('PMT processing parameters', 'downsample_profile'))