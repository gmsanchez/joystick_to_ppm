#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
 
const int pinCE = 9;
const int pinCSN = 10;
RF24 radio(pinCE, pinCSN);
 
// Single radio pipe address for the 2 nodes to communicate.
const uint64_t pipe = 0xE8E8F0F0E1LL;
 
//float data[2];
byte receivedMsg[8];
boolean newData = false;
int bytesRead = 0;
int roll, pitch, yaw, throttle;

void setup()
{
   radio.begin();
   radio.setPALevel(RF24_PA_MAX);
   radio.setDataRate(RF24_1MBPS);
   radio.setAutoAck(1);
   radio.openWritingPipe(pipe);
     Serial.begin(9600);
  Serial.println("<Arduino is ready>");

}
 
void loop()
{ 
//   data[0]= 3.14;
//   data[1] = millis()/1000.0;
   recvMsg();
   showNewData();
  
   radio.write(receivedMsg, 8);
   // delay(100);
}

void recvMsg() {
    if (Serial.available() > 0) {
        bytesRead = Serial.readBytes(receivedMsg, 8);
        if (bytesRead == 8)
          newData = true;
    }
}

int get_data(byte h, byte l){
  return ((h << 8) + l - 32768);
}

void showNewData() {
    if (newData == true) {
        Serial.print("This just in ... ");
        roll = get_data(receivedMsg[0], receivedMsg[1]);
        pitch = get_data(receivedMsg[2], receivedMsg[3]);
        throttle = get_data(receivedMsg[4], receivedMsg[5]);
        yaw = get_data(receivedMsg[6], receivedMsg[7]);
        Serial.print(roll);
        Serial.print(" == ");
        Serial.print(pitch);
        Serial.print(" == ");
        Serial.print(throttle);
        Serial.print(" == ");
        Serial.println(yaw);
//        Serial.print(" ## ");
//        Serial.print(map(roll, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
//        Serial.print(" == ");
//        Serial.print(map(pitch, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
//        Serial.print(" == ");
//        Serial.print(map(throttle, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
//        Serial.print(" == ");
//        Serial.println(map(yaw, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
        newData = false;
    }
}
