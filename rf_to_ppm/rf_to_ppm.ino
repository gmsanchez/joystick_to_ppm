#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
 
const int pinCE = 9;
const int pinCSN = 10;
RF24 radio(pinCE, pinCSN);
 
// Single radio pipe address for the 2 nodes to communicate.
const uint64_t pipe = 0xE8E8F0F0E1LL;

//////////////////////CONFIGURATION///////////////////////////////
#define CHANNEL_NUMBER 12  //set the number of chanels
#define CHANNEL_DEFAULT_VALUE 1500  //set the default servo value
#define FRAME_LENGTH 22500  //set the PPM frame length in microseconds (1ms = 1000µs)
#define PULSE_LENGTH 300  //set the pulse length
#define onState 1  //set polarity of the pulses: 1 is positive, 0 is negative
#define sigPin 6  //set PPM signal output pin on the arduino

/*this array holds the servo values for the ppm signal
 change theese values in your code (usually servo values move between 1000 and 2000)*/
int ppm[CHANNEL_NUMBER];

#define JOYSTICK_LOW -32768
#define JOYSTICK_HIGH 32767
#define PPM_LOW 1000
#define PPM_HIGH 2000

byte receivedMsg[8];
int roll, pitch, yaw, throttle;

void setup()
{
  //initiallize default ppm values
  for(int i=0; i<CHANNEL_NUMBER; i++){
    ppm[i]= CHANNEL_DEFAULT_VALUE;
  }
  
  pinMode(sigPin, OUTPUT);
  digitalWrite(sigPin, !onState);  //set the PPM signal pin to the default state (off)
  
  cli();
  TCCR1A = 0; // set entire TCCR1 register to 0
  TCCR1B = 0;
    
  OCR1A = 100;  // compare match register, change this
  TCCR1B |= (1 << WGM12);  // turn on CTC mode
  TCCR1B |= (1 << CS11);  // 8 prescaler: 0,5 microseconds at 16mhz
  TIMSK1 |= (1 << OCIE1A); // enable timer compare interrupt
  sei();
    
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setAutoAck(1);
  radio.openReadingPipe(1, pipe);
  radio.startListening();

//  Serial.begin(9600); 
//  Serial.println("<Arduino is ready>");
}
 
void loop()
{
   if (radio.available())
   {    
      radio.read(receivedMsg, 8);
      showNewData();

        // http://ardupilot.org/rover/docs/common-radio-control-calibration.html
  // De acá saqué cómo ordenar los canales
//          # Recommended channels:
//        # Ch 1: Roll
//        # Ch 2: Pitch
//        # Ch 3: Throttle
//        # Ch 4: Yaw
//        # Ch 8: Flight modes
  ppm[0] = (int) map(roll, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH);
  ppm[1] = (int) map(pitch, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH);
  ppm[2] = (int) map(throttle, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH);
  ppm[3] = (int) map(yaw, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH);

  // ppm[7] =  // Acá deberiamos poner el cambiador de flight mode.
   }
   // delay(100);
}

ISR(TIMER1_COMPA_vect){  //leave this alone
  static boolean state = true;
  
  TCNT1 = 0;
  
  if (state) {  //start pulse
    digitalWrite(sigPin, onState);
    OCR1A = PULSE_LENGTH * 2;
    state = false;
  } else{  //end pulse and calculate when to start the next pulse
    static byte cur_chan_numb;
    static unsigned int calc_rest;
  
    digitalWrite(sigPin, !onState);
    state = true;

    if(cur_chan_numb >= CHANNEL_NUMBER){
      cur_chan_numb = 0;
      calc_rest = calc_rest + PULSE_LENGTH;// 
      OCR1A = (FRAME_LENGTH - calc_rest) * 2;
      calc_rest = 0;
    }
    else{
      OCR1A = (ppm[cur_chan_numb] - PULSE_LENGTH) * 2;
      calc_rest = calc_rest + ppm[cur_chan_numb];
      cur_chan_numb++;
    }     
  }
}


int get_data(byte h, byte l){
  return ((h << 8) + l - 32768);
}

void showNewData() {
//        Serial.print("This just in ... ");
        roll = get_data(receivedMsg[0], receivedMsg[1]);
        pitch = get_data(receivedMsg[2], receivedMsg[3]);
        throttle = get_data(receivedMsg[4], receivedMsg[5]);
        yaw = get_data(receivedMsg[6], receivedMsg[7]);
//        Serial.print(roll);
//        Serial.print(" == ");
//        Serial.print(pitch);
//        Serial.print(" == ");
//        Serial.print(throttle);
//        Serial.print(" == ");
//        Serial.print(yaw);
//        Serial.print(" ## ");
//        Serial.print(map(roll, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
//        Serial.print(" == ");
//        Serial.print(map(pitch, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
//        Serial.print(" == ");
//        Serial.print(map(throttle, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
//        Serial.print(" == ");
//        Serial.println(map(yaw, JOYSTICK_LOW, JOYSTICK_HIGH, PPM_LOW, PPM_HIGH));
}
