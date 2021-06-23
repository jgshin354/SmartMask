/*
  Optical SP02 Detection (SPK Algorithm) using the MAX30105 Breakout
  By: Nathan Seidle @ SparkFun Electronics
  Date: October 19th, 2016
  https://github.com/sparkfun/MAX30105_Breakout

  This demo shows heart rate and SPO2 levels.

  It is best to attach the sensor to your finger using a rubber band or other tightening
  device. Humans are generally bad at applying constant pressure to a thing. When you
  press your finger against the sensor it varies enough to cause the blood in your
  finger to flow differently which causes the sensor readings to go wonky.

  This example is based on MAXREFDES117 and RD117_LILYPAD.ino from Maxim. Their example
  was modified to work with the SparkFun MAX30105 library and to compile under Arduino 1.6.11
  Please see license file for more info.

  Hardware Connections (Breakoutboard to Arduino):
  -5V = 5V (3.3V is allowed)
  -GND = GND
  -SDA = A4 (or SDA)
  -SCL = A5 (or SCL)
  -INT = Not connected

  The MAX30105 Breakout can handle 5V or 3.3V I2C logic. We recommend powering the board with 5V
  but it will also run at 3.3V.
*/

#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm_jgshin.h"

MAX30105 particleSensor;

#define MAX_BRIGHTNESS 255

/*
  #if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
  //Arduino Uno doesn't have enough SRAM to store 100 samples of IR led data and red led data in 32-bit format
  //To solve this problem, 16-bit MSB of the sampled data will be truncated. Samples become 16-bit data.
  uint16_t irBuffer[100]; //infrared LED sensor data
  uint16_t redBuffer[100];  //red LED sensor data
  #else
  uint32_t irBuffer[100]; //infrared LED sensor data
  uint32_t redBuffer[100];  //red LED sensor data
  #endif
*/

#define BUF_LEN 100

int32_t bufferLength; //data length
uint32_t irBuffer[BUF_LEN]; //infrared LED sensor data
uint32_t redBuffer[BUF_LEN];  //red LED sensor data


int32_t spo2; //SPO2 value
int8_t validSPO2; //indicator to show if the SPO2 calculation is valid
int32_t heartRate; //heart rate value
int8_t validHeartRate; //indicator to show if the heart rate calculation is valid

byte pulseLED = 11; //Must be on PWM pin
byte readLED = 13; //Blinks with each data read

byte bluetooth_send[9];
unsigned long time_a, time_b, delta_t;
float sampfreq = 1;

//BLE Code init.
/*
    Video: https://www.youtube.com/watch?v=oCMOYS71NIU
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleNotify.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updated by chegewara

   Create a BLE server that, once we receive a connection, will send periodic notifications.
   The service advertises itself as: 4fafc201-1fb5-459e-8fcc-c5c9c331914b
   And has a characteristic of: beb5483e-36e1-4688-b7f5-ea07361b26a8

   The design of creating the BLE server is:
   1. Create a BLE Server
   2. Create a BLE Service
   3. Create a BLE Characteristic on the Service
   4. Create a BLE Descriptor on the characteristic
   5. Start the service.
   6. Start advertising.

   A connect hander associated with the server starts a background task that performs notification
   every couple of seconds.
*/
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;
uint32_t value = 0;

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"


class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};






void setup()
{
  Serial.begin(115200); // initialize serial communication at 115200 bits per second:

  pinMode(pulseLED, OUTPUT);
  pinMode(readLED, OUTPUT);

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println(F("0 found. Please check wiring/power."));
    while (1);
  }

  //Serial.println(F("Attach sensor to finger with rubber band. Press any key to start conversion"));
  //while (Serial.available() == 0) ; //wait until user presses a key
  //Serial.read();
  /*
    byte ledBrightness = 60; //Options: 0=Off to 255=50mA
    byte sampleAverage = 4; //Options: 1, 2, 4, 8, 16, 32
    byte ledMode = 2; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
    byte sampleRate = 100; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
    int pulseWidth = 411; //Options: 69, 118, 215, 411
    int adcRange = 4096; //Options: 2048, 4096, 8192, 16384
  */

  byte ledBrightness = 5; //Options: 0=Off to 255=50mA
  byte sampleAverage = 4; //Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 3; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  int sampleRate = 200; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; //Options: 69, 118, 215, 411
  int adcRange = 2048; //Options: 2048, 4096, 8192, 16384



  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings



  //BLE Code setup
  // Serial.begin(115200);

  // Create the BLE Device
  BLEDevice::init("ESP32_DGMIF");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY 
                    );

  // https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
  // Create a BLE Descriptor
  pCharacteristic->addDescriptor(new BLE2902());

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
  Serial.println("Waiting a client connection to notify...");

}

void loop()
{

  if (deviceConnected)  {
    bufferLength = BUF_LEN; //buffer length of 100 stores 4 seconds of samples running at 25sps

    //read the first 100 samples, and determine the signal range

    time_b = millis();

    for (int i = 0 ; i < bufferLength ; i++)
    {
      while (particleSensor.available() == false) //do we have new data?
        particleSensor.check(); //Check the sensor for new data

      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample(); //We're finished with this sample so move to next sample

      //Serial.print(F("red="));
      //Serial.print(redBuffer[i], DEC);
      //Serial.print(F(", ir="));
      //Serial.println(irBuffer[i], DEC);
      /*
      if (i % 10 == 0)
      {
        uint8_t tmp;
        tmp = i / 10;
        pCharacteristic->setValue((uint8_t*)&tmp, 1); //bluetooth value send
        pCharacteristic->notify();                  //bluetooth value send
      } */

    }

    time_a = millis();
    delta_t = time_a - time_b;
    sampfreq = 1 / ((float) delta_t / (float) bufferLength / 1000);

    //calculate heart rate and SpO2 after first 100 samples (first 4 seconds of samples)
    maxim_heart_rate_and_oxygen_saturation_b(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate, sampfreq);

    //Continuously taking samples from MAX30102.  Heart rate and SpO2 are calculated every 1 second
    while (1)
    {
      //dumping the first 25 sets of samples in the memory and shift the last 75 sets of samples to the top
      for (int i = 25; i < bufferLength; i++)
      {
        redBuffer[i - 25] = redBuffer[i];
        irBuffer[i - 25] = irBuffer[i];


        //      Serial.print(F("iter="));
        //      Serial.println(i, DEC);
      }

      //take 25 sets of samples before calculating the heart rate.
      for (int i = bufferLength - 25; i < bufferLength; i++)
      {
        while (particleSensor.available() == false) //do we have new data?
          particleSensor.check(); //Check the sensor for new data

        digitalWrite(readLED, !digitalRead(readLED)); //Blink onboard LED with every data read

        redBuffer[i] = particleSensor.getRed();
        irBuffer[i] = particleSensor.getIR();
        particleSensor.nextSample(); //We're finished with this sample so move to next sample

        //send samples and calculation result to terminal program through UART
        //Serial.print(F("iter="));
        //Serial.print(i, DEC);

        //      Serial.print(F(", red="));
        bluetooth_send[0] = 1;
        memcpy(&bluetooth_send + 1, &redBuffer[i], sizeof(uint32_t));
//        bluetooth_send[0] = 1;
//        bluetooth_send[1] = redBuffer[i];
//        bluetooth_send[2] = irBuffer[i];
//        bluetooth_send[3] = 0;
//        bluetooth_send[4] = 0;
        Serial.print(F("red="));
        Serial.println(redBuffer[i], DEC);
        
        pCharacteristic->setValue((uint8_t*)&bluetooth_send, 5); //bluetooth value send
        pCharacteristic->notify();                  //bluetooth value send
        /*
          Serial.print(F("red="));
          Serial.print(redBuffer[i], DEC);
          Serial.print(F(", ir="));
          Serial.print(irBuffer[i], DEC);

          Serial.print(F(", HR="));
          Serial.print(heartRate, DEC);

          Serial.print(F(", HRvalid="));
          Serial.print(validHeartRate, DEC);

          Serial.print(F(", SPO2="));
          Serial.print(spo2, DEC);

          Serial.print(F(", SPO2Valid="));
          Serial.println(validSPO2, DEC);
          //maxim_heart_rate_and_oxygen_saturation_b(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate, sampfreq);
        */

      }
      time_b = time_a;
      time_a = millis();
      delta_t = time_a - time_b;
      sampfreq = 1 / ((float) delta_t / 25 / 1000);

      //After gathering 25 new samples recalculate HR and SP02
      maxim_heart_rate_and_oxygen_saturation_b(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate, sampfreq);
      if (heartRate > 255) heartRate = 255;
      else if (heartRate < 0) heartRate = 0;
      if (spo2 < 0) spo2 = 0;
      
      bluetooth_send[0] = 2;
      bluetooth_send[1] = heartRate;
      bluetooth_send[2] = validHeartRate;
      bluetooth_send[3] = spo2;
      bluetooth_send[4] = validSPO2;
      
      
      Serial.print(F(", HR="));
      Serial.print(heartRate, DEC);

      Serial.print(F(", HRvalid="));
      Serial.print(validHeartRate, DEC);

      Serial.print(F(", SPO2="));
      Serial.print(spo2, DEC);

      Serial.print(F(", SPO2Valid="));
      Serial.println(validSPO2, DEC);

      pCharacteristic->setValue((uint8_t*)&bluetooth_send, 5); //bluetooth value send
      pCharacteristic->notify();                  //bluetooth value send
      if (!deviceConnected || !oldDeviceConnected){
      break;
      }
    }
  }
  if (!deviceConnected && oldDeviceConnected) {
    delay(500); // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising(); // restart advertising
    Serial.println("Disconnecting");
    oldDeviceConnected = deviceConnected;
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected) {
    // do stuff here on connecting
    oldDeviceConnected = deviceConnected;
    Serial.println("Connecting");
  }
}
