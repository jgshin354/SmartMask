import sys
from PyQt5 import QtWidgets
from PyQt5 import uic

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.ptime import time
from BLE_SPO2_Python_UI import Ui_Form


class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("BLE_SPO2_Python.ui")
        self.ui.setWindowTitle("BLE_SPO2_DGMIF")
        # self.initUI()

    # def initUI(self):
    #     self.gridLayout_W.removeWidget(self.grp_red)
        # self.grp_red.hide()
        # self.canvas321 = QtWidgets.QLabel()
        # self.gridLayout.addWidget(self.canvas232, 0, 2)
        # self.qImg232 = QtGui.QImage(np.int8(np.ones([self.sbox_smp_ascan.value(), self.sbox_smp_ascan.value()]) * 128),
        #                             self.sbox_smp_ascan.value(), self.sbox_smp_ascan.value(), QtGui.QImage.Format_Grayscale8)
        self.ui.show()




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())