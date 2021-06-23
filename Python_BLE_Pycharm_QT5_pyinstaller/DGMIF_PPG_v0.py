import sys
from os import getcwd
from PyQt5 import QtWidgets
from PyQt5 import uic
# from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.ptime import time
import numpy as np
# import time
import asyncio # 비동기화 통신을 위한 라이브러리
# import bleak   # bleak 라이브러리
from bleak import BleakScanner # BLE 검색 모듈
from bleak import BleakClient
from datetime import datetime
# import nest_asyncio
# nest_asyncio.apply()

class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        super().__init__()
        self.ui = uic.loadUi(getcwd() + "\\DGMIF_PPG.ui")
        self.ui.setWindowTitle("DGMIF_PPG_v0")

        ### initialization of global variables
        self.pts_n = 256
        self.init_var()
        self.op_flag = 1
        self.ble_address = ''
        self.device_name = 'ESP32_DGMIF'
        self.device_find_flag = False
        self.device_busy = False



        ### Event handler settings
        self.ui.PushButton.clicked.connect(self.opbtn_clicked)
        self.ui.radioButton_1.clicked.connect(self.radioButtonClicked)
        self.ui.radioButton_2.clicked.connect(self.radioButtonClicked)
        self.ui.radioButton_3.clicked.connect(self.radioButtonClicked)
        self.ui.radioButton_4.clicked.connect(self.radioButtonClicked)

        ### Graph layout settings
        self.ui.gridLayout.removeWidget(self.ui.grp_dummy1)
        self.ui.grp_dummy1.hide()
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

        self.fig_update()
        self.ui.show()

    def init_var(self):
        self.red = np.array([])
        self.ir = np.array([])
        self.spo2 = np.array([])
        self.hr = np.array([])
        self.date_hr_spo2 = []
        self.time_hr_spo2 = []
        self.red_plot = np.ones([ self.pts_n])
        self.ir_plot = np.ones([ self.pts_n])

    def radioButtonClicked(self):
        msg = ""
        if self.ui.radioButton_1.isChecked():
            self.device_find_flag = False
            msg = "Discover"
            self.op_flag = 1
        elif self.ui.radioButton_2.isChecked():
            msg = "BLE Connecting"
            self.op_flag = 2
        elif self.ui.radioButton_3.isChecked():
            msg = "BLE Disconnecting"
            self.op_flag = 3
        elif self.ui.radioButton_4.isChecked():
            msg = "File Saving"
            self.op_flag = 4
        self.ui.label.setText(msg + "\n is selected.")

    def opbtn_clicked(self):
        self.ui.label.setText("OP. button \n is clicked")
        if self.op_flag == 1:
            self.loop = asyncio.get_event_loop()
            self.loop.run_until_complete(self.ble_discover())
        elif self.op_flag == 2:
            if self.device_find_flag == False:
                self.text_update('BLE Device is not found.')
            else:
                if self.device_busy == False:
                    self.init_var()
                    self.device_busy = True
                    self.loop = asyncio.get_event_loop()
                    self.loop.run_until_complete(self.ble_connect())
                else:
                    self.text_update('Device is busy.')
        elif self.op_flag ==3:
            self.running_flag = False
            if self.device_find_flag == False:
                self.text_update('BLE Device is not found.')
            if self.device_busy == False:
                self.text_update('Device is not running.')
        elif self.op_flag == 4:
            self.text_update('file saving is activated')
            self.file_save_action()


        #
        # elif self.op_flag = 2:
        #
        # elif self.op_flag = 3:
        #
        # elif self.op_flag = 4:
    def file_save_action(self):


        fname = QtWidgets.QFileDialog.getSaveFileName(None, "Save CSV file", "./", "CSV Files (*.csv)",
                                                    '/home',options=QtWidgets.QFileDialog.DontUseNativeDialog, )[0]
        if fname == '':
            fname = getcwd() +  '\\test.csv'
        elif fname[-4:] != '.csv':
            fname = fname+'.csv'
        tmp_text = 'Filename to save : ' + '"' +str(fname) +'"'
        self.text_update(tmp_text)

        if fname[0]:
            file_ppg = open(fname, 'w')
            for i in range(0,len(self.spo2)):
                print(i)
                text_tmp = str(self.date_hr_spo2[i]) + ',' + str(self.time_hr_spo2[i]) +','+ str(self.hr[i])+',' + str(self.spo2[i]) + '\n'
                # print(text_tmp)
                file_ppg.write(text_tmp)
            file_ppg.close()
        tmp_text = 'File writing is completed'
        self.text_update(tmp_text)



        # fname = QFileDialog.getOpenFileName(self, 'Save file', "",
        #                                     "CSV Rawdata (*.csv);;Python Files(*.py);;All Files(*)", '/home')
        # tmp_text = 'Filename to save : ' + str(fname[0])
        # self.text_update(tmp_text)
        # if fname[0]:
        #     file_ppg = open(fname[0], 'w')
        #     for i in range(0,len(self.spo2)):
        #         text_tmp = self.date_hr_spo2[i] + ',' +self.time_hr_spo2[i] +','+ str(self.hr[i])+',' + str(self.spo2[i]), '\n'
        #         file_ppg.write(text_tmp)
        #     file_ppg.close()
        # tmp_text = 'File writing is completed'
        # self.text_update(tmp_text)

    def fig_update(self):
        self.pw1_plot.setData(self.red_plot)
        self.pw2_plot.setData(self.ir_plot)
        self.pw3_plot.setData(self.hr)
        self.pw4_plot.setData(self.spo2)
        app.processEvents()

    def detection_callback(self, device, advertisement_data):
        #print(device.address, "RSSI:", device.rssi, advertisement_data)
        if advertisement_data.local_name == self.device_name:
            self.device_find_flag = True
            self.running_flag = False
            self.device_busy = False

    def text_update(self, text):
        self.ui.textBrowser.append(text)
        app.processEvents()

    def on_disconnect_ble(self, client):
        self.text_update("Client with address {" +self.ble_address +"} got disconnected!")
        # print('disconnected!')
        self.device_busy = False
        # print(self.device_busy)

    def notify_callback(self, sender: int, data: bytearray):
        if data[0] == 1:
            red_curr = int.from_bytes(data[1:4], "little")
            ir_curr = int.from_bytes(data[5:8], "little")
            self.red = np.append(self.red, red_curr)
            self.ir = np.append(self.ir, ir_curr)

            if len(self.red) == 1:
                self.red_plot = self.red_plot * red_curr
                self.ir_plot = self.ir_plot * ir_curr
            else:
                self.red_plot = np.roll(self.red_plot, -1)
                self.red_plot[len(self.red_plot) - 1] = red_curr
                self.ir_plot = np.roll(self.ir_plot, -1)
                self.ir_plot[len(self.ir_plot) - 1] = ir_curr
        elif data[0] == 2:
            if data[4] == 1:
                hr_curr = data[1]
                spo2_curr = data[3]
                date_curr = datetime.now().strftime('%Y-%m-%d')
                time_curr = datetime.now().strftime('%H:%M:%S')
                self.hr = np.append(self.hr, hr_curr)
                self.spo2 = np.append(self.spo2, spo2_curr)
                self.date_hr_spo2.append(date_curr)
                self.time_hr_spo2.append(time_curr)
                text_tmp = date_curr + ',  ' +time_curr + ', heartbeat rate:' + str(hr_curr) + ', SpO2: ' + str(spo2_curr) + '%'
                self.text_update(text_tmp)
        self.fig_update()

    async def ble_connect(self):
        client = BleakClient(self.ble_address)
        try:
            # 장치 연결 해제 콜백 함수 등록
            client.set_disconnected_callback(self.on_disconnect_ble)
            await client.connect()
            self.text_update('connected')
            services = await client.get_services()
            # 서비스들을 루프돌려 내부 캐릭터리스틱 정보 조회
            for service in services:
                self.text_update('service uuid:' + service.uuid)
                # 각 서비스들에 있는 캐릭터리스틱을 루프 돌려 속성들 파악하기
                for characteristic in service.characteristics:
                    self.text_update('  uuid:' + characteristic.uuid)
                    # handle 정보도 함께 확인
                    self.text_update('  handle:' + str(characteristic.handle))
                    self.text_update('  properties: ')
                    for property in characteristic.properties:
                        self.text_update('      ' + property)
                    # 캐릭터리스틱 UUID가 우리가 찾는 UUID인지 먼저 확인
                    # if characteristic.uuid == notity_charcteristic_uuid:
                    #     # 우리가 찾던 UUID가 맞다면
                    #     # 해당 캐릭터리스틱에 notify 속성이 있는지 확인
                    if 'notify' in characteristic.properties:
                        # notify 속성이 있다면 BLE 장치의 notify 속성을
                        # 활성화 작업 후 notify_callback 함수 연결
                        self.text_update('try to activate notify.')
                        #print(characteristic.uuid)
                        await client.start_notify(characteristic, self.notify_callback)
                        self.characteristic_notify_uuid = characteristic.uuid
            self.running_flag = True
            while(self.running_flag):
                await asyncio.sleep(1)
        except Exception as e:
            # 연결 실패시 발생
            self.text_update('error: ' + e)
        finally:
            self.text_update('try to deactivate notify.')
            await client.stop_notify(self.characteristic_notify_uuid)
            self.text_update('start disconnect')
            # 장치 연결 해제
            await client.disconnect()

    async def ble_discover(self):
        # # BleakClient 클래스 생성 및 바로 연결 시작
        # # address: ESP32 맥주소
        # # timeout: 연결 제한 시간 5초가 넘어가면 더 이상 연결하지 말고 종료
        # devices = await BleakScanner.discover()
        # device_find_flag = False
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.detection_callback)
        await self.scanner.start()
        self.text_update('Starting BLE discover')
        self.text_update('5 Seconds remained')
        await asyncio.sleep(1.0)
        if self.device_find_flag == False:
            self.text_update('4 Seconds remained')
            await asyncio.sleep(1.0)
        if self.device_find_flag == False:
            self.text_update('3 Seconds remained')
            await asyncio.sleep(1.0)
        if self.device_find_flag == False:
            self.text_update('2 Seconds remained')
            await asyncio.sleep(1.0)
        if self.device_find_flag == False:
            self.text_update('1 Seconds remained')
            await asyncio.sleep(1.0)
        else:
            self.text_update('ESP32 BLE device found.')
        self.text_update('Ending BLE Discover')


        await self.scanner.stop()
        # FutureWarning: This method will be removed in a future version of Bleak. Use the `discovered_devices` property instead.
        self.devices = await self.scanner.get_discovered_devices()
        # self.devices = await self.scanner.discovered_devices()

        for i in self.devices:
            if i.name == self.device_name:
                self.ble_address = i.address
                tmp_text = 'ESP32 BLE Address is ' + self.ble_address
                self.text_update(tmp_text)
        if self.device_find_flag == False:
            self.text_update('Device is not found')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())