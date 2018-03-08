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

import sys
import QTabProcessedProfiles, QTabRawData, QTabMotionData

from PyQt5.QtWidgets import QTabWidget, QApplication


class QTabWidgetPlotting(QTabWidget):

    def __init__(self, parent=None):

        super(QTabWidgetPlotting, self).__init__(parent)

        self.tab_processed_profiles = QTabProcessedProfiles.QtabProcessedProfiles()
        self.tab_raw_data = QTabRawData.QTabRawData()
        self.tab_motion_data = QTabMotionData.QTabMotionData()

        self.addTab(self.tab_processed_profiles, "Processed Beam Profiles")
        self.addTab(self.tab_raw_data, "Raw Data")
        self.addTab(self.tab_motion_data, "Motion Data")

        # self.setFixedWidth(800)
        # self.setFixedHeight(800)

def main():
    app = QApplication(sys.argv)
    ex = QTabWidgetPlotting()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

