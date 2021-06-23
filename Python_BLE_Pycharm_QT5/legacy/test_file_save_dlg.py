import sys
from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtGui, QtCore



from BLE_SPO2_Python_UI import Ui_Form

class BLE_DGMIF(Ui_Form):
    def __init__(self, widget):
        Ui_Form.__init__(self)
        self.setupUi(widget)
        widget.setWindowTitle("BLE_SPO2_DGMIF")
        ### Event handler settings
        # self.PushButton.clicked.connect(self.opbtn_clicked)
        # self.saveButton.clicked.connect(self.showDialog)


        openFile = self.saveButton
        # openFile.setShortcut('Ctrl+O')
        # openFile.setStatusTip('Open New File')
        openFile.clicked.connect(self.showDialog)

    def showDialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', './')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                self.textEdit.setText(data)






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    execUi = BLE_DGMIF(Form)
    Form.show()
    sys.exit(app.exec_())