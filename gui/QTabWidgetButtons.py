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
import QButtonsSet, QButtonsSet_Configuration

from PyQt5.QtWidgets import QTabWidget, QApplication


class QTabWidgetButtons(QTabWidget):

    def __init__(self, parent=None):

        super(QTabWidgetButtons, self).__init__(parent)

        self.buttons_pannel = QButtonsSet.QButtonsSet()
        self.buttons_pannel_config = QButtonsSet_Configuration.QButtonsSet_Configuration()

        self.addTab(self.buttons_pannel, "Triggering")
        self.addTab(self.buttons_pannel_config, 'Configuration')

        self.setFixedWidth(250)

def main():
    app = QApplication(sys.argv)
    ex = QTabWidgetButtons()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

