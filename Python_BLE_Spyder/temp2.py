import nest_asyncio
nest_asyncio.apply()


import asyncio # 비동기화 통신을 위한 라이브러리
# import bleak   # bleak 라이브러리
from bleak import BleakScanner # BLE 검색 모듈
from bleak import BleakClient
import numpy as np
import matplotlib.pyplot as plt


root_path = 'C:\\Users\\jgshi\\Documents\\GitHub\\SmartMask\\Python_BLE'
output_file = f"{root_path}\\Desktop\\microphone_dump.csv"

# ESP32 맥 주소
device_name = 'ESP32_DGMIF'
address = '84:CC:A8:5E:70:6A'
# ESP32 BLE_notity 예제에 있는 캐릭터리스틱 주소
notity_charcteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"                                
'''
# ESP32가 notify로 보낸 데이터를 받는 콜백함수
def notify_callback(sender: int, data: bytearray):
    print('sender: ', sender, 'data: ', data)
'''
red = np.array([])
ir = np.array([])
red_plot = np.ones([256])
ir_plot = np.ones([256])
tmp_dat = [];
# plt.ion()                           #그래프 창의 애니메이션 기능 활성화
# fig = plt.figure()
# sf1 = fig.add_subplot(211)
# line1, = sf1.plot(red_plot)
# sf2 = fig.add_subplot(212)
# line2, = sf2.plot(ir_plot)
# plt.gcf().canvas.draw()

# class DataToFile:

#     column_names = ["time", "delay", "data_value"]

#     def __init__(self, write_path):
#         self.path = write_path

#     def write_to_csv(self, times: [int], delays: [datetime], data_values: [Any]):

#         if len(set([len(times), len(delays), len(data_values)])) > 1:
#             raise Exception("Not all data lists are the same length.")

#         with open(self.path, "a+") as f:
#             if os.stat(self.path).st_size == 0:
#                 print("Created file.")
#                 f.write(",".join([str(name) for name in self.column_names]) + ",\n")
#             else:
#                 for i in range(len(data_values)):
#                     f.write(f"{times[i]},{delays[i]},{data_values[i]},\n")

# data_to_file = DataToFile(output_file)
# data_dump_handler = data_to_file.write_to_csv

def foo():
    global red
    red = np.append(red,int.from_bytes([1,3,2,4],"big"))
    print(red)


def notify_callback(sender: int, data: bytearray):
    global red#red, ir, red_plot, ir_plot, tmp_dat
    # 기본
    # print('sender: ', sender, 'data: ', data)
    # # 데이터의 길이 출력(바이트 단위)
    # print('\tdata len: ', len(data))

    # # Big Endian 기준으로 10진수로 변환
    # print('\tbig endian int: ', int.from_bytes(data, "big"))
    # # Little Endian 기준으로 10진수로 변환
    # print('\tlittle endian int: ', int.from_bytes(data, "little"))
    # # int 형으로 리스트 출력
    # print('\tint list: ', [b for b in data])
    # # 각 인덱스별로 개별 출력    
    # for idx, b in enumerate(data):
    #     print('\t\t', idx, ': ', b)
    # # 16진수 문자열로 출력
    # print('\tHexadecimal: ', data.hex())
    # # 각각 바이트씩 16진수 문자열로 출력 
    # print('\thex string list: ', [hex(b) for b in data])
    
    # data_dump_handler(self.rx_data, self.rx_timestamps, self.rx_delays)
    
    # print('data:', data)
    # print('data[1:4]:', int.from_bytes(data[1:4],"big"))
    # print('data[0]', data[0])
    # if data[0] == 1:
    #     tmp_dat = data
    
    
    if data[0] == 1:
        red = np.append(red,int.from_bytes(data[1:4],"little"))
        #red = np.append(red,np.int(data[1]))#int.from_bytes(data[1:4],"big"))
        # ir = np.append(ir,from_bytes(data[5:8],"big"))
    # if len(red)==1:
    #     red_plot = red_plot*int.from_bytes(data[1:4],"big")
    #     # ir_plot = ir_plot*from_bytes(data[5:8],"big")
    # else:
    #     red_plot = np.roll(red_plot,-1)
    #     red_plot[len(red_plot)-1] = int.from_bytes(data[1:4],"big")
    #     # ir_plot = np.roll(ir_plot,-1)
    #     # ir_plot[len(ir_plot)-1] = from_bytes(data[5:8],"big")
    # # line1.set_ydata(red_plot)
    # # line2.set_ydata(ir_plot)    
    # #plt.gcf().canvas.draw()
    # print(red)
    
# async def running():
#     while True:
#         key_input = input()
#         if key_input == 'k':
#             break
        
    
    # 장치와 연결해제시 발생하는 콜백 이벤트
def on_disconnect(client):
    print("Client with address {} got disconnected!".format(client.address))
def detection_callback(device, advertisement_data):
    print(device.address, "RSSI:", device.rssi, advertisement_data)    

async def run(device_name):              
    # # BleakClient 클래스 생성 및 바로 연결 시작
    # # address: ESP32 맥주소
    # # timeout: 연결 제한 시간 5초가 넘어가면 더 이상 연결하지 말고 종료
    # devices = await BleakScanner.discover()
    # device_find_flag = False
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(5.0)
    await scanner.stop()
    devices = await scanner.get_discovered_devices()    


    for i in devices:
        if i.name == device_name:
            ble_address = i.address
            print('ESP32 BLE Address is', i.address)
            device_find_flag = True
    if device_find_flag == False:
        print('Device is not found')
    #ble_address = address
    
    client = BleakClient(ble_address)
    try:
        # 장치 연결 해제 콜백 함수 등록
        client.set_disconnected_callback(on_disconnect)
        await client.connect()
        print('connected')
        services = await client.get_services()
        # 서비스들을 루프돌려 내부 캐릭터리스틱 정보 조회
        for service in services:
            print('service uuid:', service.uuid)
            # 각 서비스들에 있는 캐릭터리스틱을 루프 돌려 속성들 파악하기
            for characteristic in service.characteristics:
                print('  uuid:', characteristic.uuid)
                # handle 정보도 함께 확인
                print('  handle:', characteristic.handle) 
                print('  properties: ', characteristic.properties)
                # 캐릭터리스틱 UUID가 우리가 찾는 UUID인지 먼저 확인
                if characteristic.uuid == notity_charcteristic_uuid:  
                    # 우리가 찾던 UUID가 맞다면 
                    # 해당 캐릭터리스틱에 notify 속성이 있는지 확인
                    if 'notify' in characteristic.properties:
                        # notify 속성이 있다면 BLE 장치의 notify 속성을 
                        # 활성화 작업 후 notify_callback 함수 연결
                        print('try to activate notify.')
                        await client.start_notify(characteristic, notify_callback)        
        await asyncio.sleep(25)                
    except Exception as e:
        # 연결 실패시 발생
        print('error: ', e, end='')        
    finally:
        await client.stop_notify(notity_charcteristic_uuid)
        print('start disconnect')
        # 장치 연결 해제
        await client.disconnect()
    
    
#         # 연결을 성공함
#         print('connected')
#         # 연결된 BLE 장치의 서비스 요청
#         services = await client.get_services()
#         # 서비스들을 루프돌려 내부 캐릭터리스틱 정보 조회
#         for service in services:
#             print('service uuid:', service.uuid)
#             # 각 서비스들에 있는 캐릭터리스틱을 루프 돌려 속성들 파악하기
#             for characteristic in service.characteristics:
#                 print('  uuid:', characteristic.uuid)
#                 # handle 정보도 함께 확인
#                 print('  handle:', characteristic.handle) 
#                 print('  properties: ', characteristic.properties)
#                 # 캐릭터리스틱 UUID가 우리가 찾는 UUID인지 먼저 확인
#                 if characteristic.uuid == notity_charcteristic_uuid:  
#                     # 우리가 찾던 UUID가 맞다면 
#                     # 해당 캐릭터리스틱에 notify 속성이 있는지 확인
#                     if 'notify' in characteristic.properties:
#                         # notify 속성이 있다면 BLE 장치의 notify 속성을 
#                         # 활성화 작업 후 notify_callback 함수 연결
#                         print('try to activate notify.')
#                         await client.start_notify(characteristic, notify_callback)

#         # client 가 연결된 상태라면
#         if client.is_connected:
#             await asyncio.sleep(5)
#         # while await client.is_connected():
#             # await asyncio.sleep(1)            
#             # while True:
#             #     await asyncio.sleep(1)
#             # input_key = input()
#             # if input_key == 'k':
#             #     print('k')
#             # # 1초간 대기
#             # # while(1):
#             # #     input_key = input()
#             # #     if input_key == 'k':
#             # #         break
#             # #     await asyncio.sleep(20)
#             # await running()
#         print('try to deactivate notify.')
#             # 활성시켰단 notify를 중지 시킨다.
#         await client.stop_notify(notity_charcteristic_uuid)

#     #with 문을 빠져나오면 장치는 알아서 disconnect가 된다.
#     print('disconnect')

loop = asyncio.get_event_loop()
loop.run_until_complete(run(device_name))
print('done')



