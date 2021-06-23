import sys
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import *


from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.ptime import time


form_class = uic.loadUiType("BLE_SPO2_Python.ui")[0]

# class MyWindow(QMainWindow, form_class):

class MyWindow(QtWidgets.QDialog,form_class):
    def __init__(self):
        # QtWidgets.QDialog.__init__(self)
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("BLE_SPO2_DGMIF")
        self.gridLayout.removeWidget(self.grp221)
        self.grp221.hide()
        # self.canvas221 = pg.GraphicsLayoutWidget()
        # self.gridLayout.addWidget(self.canvas221, 0, 0)

        # self.pview = pg.GraphicsLayoutWidget()
        # self.pw1 = self.pview.addPlot(row=0, col=0, title='RED reflection')
        # self.pw2 = self.pview.addPlot(row=0, col=1, title='IR reflection')
        # self.pw3 = self.pview.addPlot(row=1, col=0, title='Heartbeat rate')
        # self.pw4 = self.pview.addPlot(row=1, col=1, title='SpO2')
        #  self.pw1_plot = self.pw1.plot()
        # self.pw2_plot = self.pw2.plot()
        # self.pw3_plot = self.pw3.plot()
        # self.pw4_plot = self.pw4.plot()
        # self.pview.show()
        # self.canvas221.show()




        # ### subplop 232, B-scan intensity image plot
        # self.gridLayout.removeWidget(self.grp_232)
        # self.grp_232.hide()
        # self.canvas232 = QtWidgets.QLabel()
        # self.gridLayout.addWidget(self.canvas232, 0, 2)
        # self.qImg232 = QtGui.QImage(np.int8(np.ones([self.sbox_smp_ascan.value(), self.sbox_smp_ascan.value()]) * 128),
        #                             self.sbox_smp_ascan.value(), self.sbox_smp_ascan.value(), QtGui.QImage.Format_Grayscale8)
        # self.pixmap232 = QtGui.QPixmap.fromImage(self.qImg232)
        # self.canvas232.setPixmap(self.pixmap232)
        # self.canvas232.show()






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
