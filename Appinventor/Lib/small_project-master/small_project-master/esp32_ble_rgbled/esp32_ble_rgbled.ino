#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "esp32-hal-cpu.h"

// led pin
#define LED1_R    32
#define LED1_G    33
#define LED1_B    25
#define LED2_R    26
#define LED2_G    27
#define LED2_B    14

#define LED_ROW     2
#define LED_COLUMN  3
#define PERIOD_MAX    256

int arrayLed[LED_ROW][3] = {{LED1_R, LED1_G, LED1_B}, {LED2_R, LED2_G, LED2_B}};
int arrayDuty[LED_ROW][3] = {{0, 0, 0}, {0, 0, 0}};

// ble
BLEServer *pServer = NULL;
BLECharacteristic * pTxCharacteristic;
bool deviceConnected = false;

#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // UART service UUID
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

// deebug
char buffer[50];

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      digitalWrite(LED_BUILTIN, HIGH);
    }

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      digitalWrite(LED_BUILTIN, LOW);
    }
};

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string rxValue = pCharacteristic->getValue();

      if (rxValue.length() > 0) {
        Serial.print("Received Value: ");
        for (int i = 0; i < rxValue.length(); i++)
          Serial.print(rxValue[i]);
        Serial.println();
        
        String strRxCmd = rxValue.c_str();
        if(strRxCmd.startsWith("LED"))
        {
          int pos_row = 0, pos_column = 0;
          String strDutyValue = strRxCmd.substring(strRxCmd.indexOf(",") + 1, strRxCmd.length());
          pos_row = (strRxCmd.charAt(3)=='1')?0:1;
          switch(strRxCmd.charAt(4))
          {
            case 'R': pos_column = 0;      break;
            case 'G': pos_column = 1;      break;
            case 'B': pos_column = 2;      break;
          }
          int ledc_count = (pos_row * LED_COLUMN) + pos_column;
          arrayDuty[pos_row][pos_column] = strDutyValue.toInt();
          ledcWrite(ledc_count, arrayDuty[pos_row][pos_column]);
        }
      }
    }
};
        
void setup() {
  Serial.begin(115200);

  int ledc_count = 0;
  for(int i = 0; i < LED_ROW; i++)
  {
    for(int j = 0; j < LED_COLUMN; j++)
    {
      ledcAttachPin(arrayLed[i][j], ledc_count);
      ledcSetup(ledc_count, 60, 8); // 12 kHz PWM, 8-bit resolution
      ledc_count++;
    }
  }
  sprintf(buffer, "getCpuFrequencyMhz : %d Mhz", getCpuFrequencyMhz());     Serial.println(buffer);
  sprintf(buffer, "getApbFrequency : %d Mhz", getApbFrequency());           Serial.println(buffer);
  sprintf(buffer, "getXtalFrequencyMhz : %d Mhz", getXtalFrequencyMhz());   Serial.println(buffer);
  
  pinMode(LED_BUILTIN, OUTPUT);

  // Create the BLE Device
  BLEDevice::init("UART Service");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(
                    CHARACTERISTIC_UUID_TX,
                    BLECharacteristic::PROPERTY_NOTIFY
                  );
                      
  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic * pRxCharacteristic = pService->createCharacteristic(
                       CHARACTERISTIC_UUID_RX,
                      BLECharacteristic::PROPERTY_WRITE
                    );

  pRxCharacteristic->setCallbacks(new MyCallbacks());

  // Start the service
  pService->start();

  // Start advertising
  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}

void loop() 
{
}
