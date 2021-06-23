import sys
from PyQt5 import QtWidgets
from PyQt5 import uic

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.ptime import time



class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        super().__init__()
        self.ui = uic.loadUi("BLE_SPO2_Python.ui")
        self.ui.setWindowTitle("BLE_SPO2_DGMIF")




        self.ui.gridLayout.removeWidget(self.ui.grp221)
        self.ui.grp221.hide()
        self.ui.red = pg.GraphicsLayoutWidget()
        self.ui.gridLayout.addWidget(self.ui.red, 0, 0)

        self.pw1 = self.ui.red.addPlot(row=0, col=0, title='RED reflection')
        self.pw2 = self.ui.red.addPlot(row=0, col=1, title='IR reflection')
        self.pw3 = self.ui.red.addPlot(row=1, col=0, title='Heartbeat rate')
        self.pw4 = self.ui.red.addPlot(row=1, col=1, title='SpO2')
        self.pw1_plot = self.pw1.plot()
        self.pw2_plot = self.pw2.plot()
        self.pw3_plot = self.pw3.plot()
        self.pw4_plot = self.pw4.plot()

        self.ui.gridLayout.removeWidget(self.ui.grp222)
        self.ui.grp222.hide()
        self.ui.ir = pg.GraphicsLayoutWidget()
        self.ui.gridLayout.addWidget(self.ui.ir, 0, 1)

        self.ui.gridLayout.removeWidget(self.ui.grp223)
        self.ui.grp223.hide()
        self.ui.hr = pg.GraphicsLayoutWidget()
        self.ui.gridLayout.addWidget(self.ui.hr, 1, 0)

        self.ui.gridLayout.removeWidget(self.ui.grp224)
        self.ui.grp224.hide()
        self.ui.spo2 = pg.GraphicsLayoutWidget()
        self.ui.gridLayout.addWidget(self.ui.spo2, 1, 1)

        # self.canvas221 = pg.GraphicsLayoutWidget()
        # self.gridLayout.addWidget(self.canvas221, 0, 0)

        # self.initUI()

    # def initUI(self):
        # self.gridLayout_W.removeWidget(self.grp_red)
        # self.gridLayout_3.removeWidget(self.grp_233)
        # self.grp_221.hide()
        # self.canvas321 = QtWidgets.QLabel()
        # self.gridLayout.addWidget(self.canvas232, 0, 2)
        # self.qImg232 = QtGui.QImage(np.int8(np.ones([self.sbox_smp_ascan.value(), self.sbox_smp_ascan.value()]) * 128),
        #                             self.sbox_smp_ascan.value(), self.sbox_smp_ascan.value(), QtGui.QImage.Format_Grayscale8)
        self.ui.show()




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())