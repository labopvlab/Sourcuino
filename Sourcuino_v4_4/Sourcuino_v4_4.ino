//Sorcuino Code V2
//Concept from J. Werner and J Geissbuhler
//Sourcuino provides a 2 channels, 4 quadrant source and measure to charaterize small R&D solar cells such as 4 terminals tandem solar cells
//February 16th 2017
// The MCP 3550 part of the code is based on the forum post of John Beale, arduino.cc



/***********************************
 * Calibration:
 * top channel April 14th 2017 JGR
 * 
 *********************************** 
 */



/* LIST OF FUNCTIONS AND INSTRUCTIONS TO COMMUNICATE VIA THE COM PORT 
 *  
 *  
 *  read_(V/I,top/bot)
 *  write_(top/bot,A/B/D,2345)
 *  iv_
 *  sweepbot=-200:1200;70,0.2 //bot/top=Vstart:Vend;Nbofpoints,delay (which is not yet implemented due to slow DAC)
 *  
 * 
*/

// include the SPI library:
#include <SPI.h>


// chip select definition
#define CSadcU5 9     // CS for adc U5
#define CSadcU6 7     // CS for adc U6
#define CSadcU7 10     // CS for adc U7
#define CSadcU8 8     // CS for adc U8
#define CSdacU3 6    // CS for dac U3
#define CSdacU4 5     // CS for dac U4

//SPI definition
#define MOSI 11  
#define MISO 12  
#define SCK 13   // SPI clock 
#define LDAC 3 // ldac for the dac 
#define SHDN 2 // shut down pin of the dac

//variable definition
String str;   //incomming string from the COM Port
String instruction; 
String command;
int sepapos;
int sepapos1;
int sepapos2;
int sepapos3;
int sepapos4;

int adcsamples = 1;    // how many samples to group together for avg. and std.dev
                      // MCP3550-60 does 15 samples per second (max) or 66.7 msec per sample
double vout = 1024;

int incomingByte = 0;

void setup() {
  // put your setup code here, to run once:

  pinMode(CSadcU5, OUTPUT); //define the CS pins for adc and dac as output
  pinMode(CSadcU6, OUTPUT);
  pinMode(CSadcU7, OUTPUT);
  pinMode(CSadcU8, OUTPUT);
  pinMode(CSdacU3, OUTPUT);
  pinMode(CSdacU4, OUTPUT);
  
  pinMode(MISO, INPUT); //define the SPI and other control pin disections
  pinMode(MOSI, OUTPUT);
  pinMode(SCK, OUTPUT);
  pinMode(LDAC, OUTPUT);
  pinMode(SHDN, OUTPUT);


  digitalWrite(CSadcU5,HIGH);   //put the CS high (i.e. ==> not enabled)
  digitalWrite(CSadcU6,HIGH);
  digitalWrite(CSadcU7,HIGH); 
  digitalWrite(CSadcU8,HIGH); 
     
  digitalWrite(LDAC,HIGH);
  digitalWrite(SHDN, HIGH); //activate the DAC

  Serial.begin(115200);    //set the COM port baudrate
  Serial.setTimeout(10);   // ...and it's timeout
  pinMode(LED_BUILTIN, OUTPUT);

  SPI.beginTransaction(SPISettings(SPI_CLOCK_DIV32, MSBFIRST, SPI_MODE3));




}

void loop() {

  if (Serial.available()>0) {
    str = Serial.readString();


    if(str.substring(0,5)=="sweep"){
      //message to start sweep: sweepbot=-200:1200;70,0.2   
      //sweeptop=vstart:vend;nbpoints,delay
      
      sepapos=str.indexOf('=',0); //find where the "=" is in the string
      sepapos2=str.indexOf(':',0); //find where the ":" is in the string
      sepapos3=str.indexOf(';',0); //find where the ";" is in the string
      sepapos4=str.indexOf(',',0); //find where the "," is in the string
      
      float Vstart=str.substring(sepapos+1,sepapos2).toFloat();
      float Vend=str.substring(sepapos2+1,sepapos3).toFloat();
      int Nbofpoints=str.substring(sepapos3+1,sepapos4).toInt();
      float delaytime=str.substring(sepapos4+1,str.length()).toFloat();
 
      String chip = str.substring(5,8);

      Serial.println("sweepstarting");
      sweep(chip,Vstart,Vend,Nbofpoints,delaytime);
      Serial.println("sweepending");

    }else if(str.substring(0,3)=="voc"){
      //vocbot=400,10;100 Vstart mV,Vstep mV;duration s
      //voctop
      //voctwo=400:500,10;100 Vstarttop:Vstartbot,Vstep;duration
      String chip = str.substring(3,6);
      if(chip=="two")
      {
      sepapos=str.indexOf('=',0); //find where the "=" is in the string
      sepapos1=str.indexOf(':',0); //find where the ":" is in the string
      sepapos2=str.indexOf(',',0); //find where the ":" is in the string
      sepapos3=str.indexOf(';',0); //find where the ";" is in the string
      float Vstarttop=str.substring(sepapos+1,sepapos1).toFloat();
      float Vstartbot=str.substring(sepapos1+1,sepapos2).toFloat();
      float Vstep=str.substring(sepapos2+1,sepapos3).toFloat();
      float duration=str.substring(sepapos3+1,str.length()).toFloat();
      
      Serial.println("trackingstarting");
      VocTrackboth(Vstarttop, Vstartbot, Vstep, duration);
      Serial.println("trackingending"); 
      }else
      {
      sepapos=str.indexOf('=',0); //find where the "=" is in the string
      sepapos2=str.indexOf(',',0); //find where the ":" is in the string
      sepapos3=str.indexOf(';',0); //find where the ";" is in the string
      float Vstart=str.substring(sepapos+1,sepapos2).toFloat();
      float Vstep=str.substring(sepapos2+1,sepapos3).toFloat();
      float duration=str.substring(sepapos3+1,str.length()).toFloat();
      
      Serial.println("trackingstarting");
      VocTrack(chip, Vstart, Vstep, duration);
      Serial.println("trackingending");     
      }
      
    }else if(str.substring(0,3)=="mpp"){
      //mppbot=400,10;100 Vstart mV,Vstep mV;duration s
      //mpptop=400,10;100
      //mpptwo=400:500,10;100 Vstarttop:Vstartbot,Vstep;duration
      String chip = str.substring(3,6);
      if(chip=="two")
      {
      sepapos=str.indexOf('=',0); //find where the "=" is in the string
      sepapos1=str.indexOf(':',0); //find where the ":" is in the string
      sepapos2=str.indexOf(',',0); //find where the ":" is in the string
      sepapos3=str.indexOf(';',0); //find where the ";" is in the string
      float Vstarttop=str.substring(sepapos+1,sepapos1).toFloat();
      float Vstartbot=str.substring(sepapos1+1,sepapos2).toFloat();
      float Vstep=str.substring(sepapos2+1,sepapos3).toFloat();
      float duration=str.substring(sepapos3+1,str.length()).toFloat();
      
      Serial.println("trackingstarting");
      mppboth(Vstarttop, Vstartbot, Vstep, duration);
      Serial.println("trackingending"); 
      }else
      {
      sepapos=str.indexOf('=',0); //find where the "=" is in the string
      sepapos2=str.indexOf(',',0); //find where the ":" is in the string
      sepapos3=str.indexOf(';',0); //find where the ";" is in the string
      float Vstart=str.substring(sepapos+1,sepapos2).toFloat();
      float Vstep=str.substring(sepapos2+1,sepapos3).toFloat();
      float duration=str.substring(sepapos3+1,str.length()).toFloat();
      
      Serial.println("trackingstarting");
      mpp(chip, Vstart, Vstep, duration);
      Serial.println("trackingending");     
      }
        
    }else if(str.substring(0,5)=="write"){
      sepapos=str.indexOf('_',0); //find where the "_" is in the string
      command = str.substring(sepapos+2,str.length()-1); //... from the command 
      //get all the parameters needed to call the function  
      String chip = command.substring(0,3);
      Serial.println(chip);
      String channel = command.substring(4,5); 
      Serial.println(channel);
      String val = command.substring(6,command.length());
      Serial.println(val);
      // call the function
      write_(chip,channel,val.toInt());
      Serial.println("voltage is written");
      

    }else if(str.substring(0,4)=="read"){
      sepapos=str.indexOf('_',0); //find where the "_" is in the string
      command = str.substring(sepapos+1,str.length()-1); //... from the command 
      String chip = command.substring(3,6);
      String type = command.substring(1,2);
      //call the function
      double result;
      result = read_(type,chip);   
      Serial.println(result);

    }else if(str.substring(0,4)=="comm"){
      Serial.println("IcommwithU");
    }else{
      Serial.println("invalid!");
    }
    
    Serial.flush();
    //delay(100);    //temporize the main loop
  }

}


//===========================================================================================
//====================DAC - ADC reading/writing===============================================================

// ------------------DAC writting part------------

void write_(String chip, String channel ,float VDAC) {
  float valdac = (map(VDAC,0,4000,0,4000));
  long indicatif;
  int CS;

  //chip selection
  if(chip=="top"){
    CS = CSdacU3;
  }
  if(chip=="bot"){
    CS = CSdacU4;
  }

  //Channel selection
  if(channel=="A"){
    indicatif=12288;
  }
  if(channel=="B"){
    indicatif=45056;
  }

  if (channel=="D"){
    //for channel A
    float valdacD = 2000.0+valdac/2;
    indicatif=12288;
    if ((valdacD <= 4095) & (valdacD >= 0)){
      digitalWrite(CS,LOW);
      delay(1);
      SPI.transfer16(indicatif+valdacD); 
      delay(1);
      digitalWrite(CS,HIGH);
      //LDAC
      digitalWrite(LDAC,LOW);
      delay(1);
      digitalWrite(LDAC,HIGH);
    }
    //for channel B
    valdacD = 2000.0-valdac/2;
    indicatif=45056;
    if ((valdacD <= 4095) & (valdacD >= 0)){
      digitalWrite(CS,LOW);
      delay(1);
      SPI.transfer16(indicatif+valdacD); 
      delay(1);
      digitalWrite(CS,HIGH);
      //LDAC
      digitalWrite(LDAC,LOW);
      delay(1);
      digitalWrite(LDAC,HIGH);
    }
    
  }
  else if ((valdac <= 4095) & (valdac >= 0)){
    digitalWrite(CS,LOW);
    delay(1);
    SPI.transfer16(indicatif+valdac); 
    delay(1);
    digitalWrite(CS,HIGH);
    //LDAC
    digitalWrite(LDAC,LOW);
    delay(1);
    digitalWrite(LDAC,HIGH);
  }
}


// ------------------ADC reading part------------
//---This part of the code is based on the soft written by John Beale found on the Arduino forum
// It has been simplified for the Sourcuino usage

// Arduino program to read Microchip MCP3550-60 using SPI bus 
// by John Beale www.bealecorner.com Feb. 9 2012

/* =======================================================
MCP3550 is a differential input 22-bit ADC (21 bits + sign)  
+Fullscale = (+Vref -1 LSB) = 0x1fffff
-Fullscale = (-Vref) = 0x200000
1 LSB => Vref / 2^21    for Vref=2 V, 1 LSB = 0.95 uV
Datasheet Spec: noise = 2.5 uV RMS with Vref = 2.5 V
measured results: 
Noise Test setup: Vdd = 5V, +Vin = -Vin = Vref/2, Zin = 500 ohms (2x 1k divider)
with Vref = 0.500 V, RMS noise = 8.60 LSB or 2.05 uV  (1 LSB = 0.24 uV)
with Vref = 1.000 V, RMS noise = 4.33 LSB or 2.06 uV  (1 LSB = 0.48 uV)
with Vref = 2.048 V, RMS noise = 2.16 LSB or 2.12 uV  (1 LSB = 0.98 uV)
with Vref = 4.00 V,  RMS noise = 1.24 LSB or 2.37 uV  (1 LSB = 1.91 uV)
==========================================================
Serial.print("start=");
    unsigned long start = millis();
    Serial.println(start);
*/

double read_(String type, String chip){           // example ==> read_(V,top)

  //variables definition
  byte OVL, OVH;      // overload condition HIGH and LOW, respectively
  unsigned int i;              // loop counter
  unsigned long w;
  long x;
  double  mean, delta ;
  mean = 0;
  int CS;
  //selection of the adc chip
  if(chip=="top"){
    if(type=="V"){
      CS = CSadcU5;
    }
    if(type=="I"){
      CS = CSadcU7;
    } 
  }
  if(chip=="bot"){
    if(type=="V"){
      CS = CSadcU6;
    }
    if(type=="I"){
      CS = CSadcU8;
    }
  }
    
  //measurement part
  for (int n=0;n<adcsamples;) {
     digitalWrite(CS,HIGH); 
     delayMicroseconds(100);
     digitalWrite(CS,LOW);   // start next conversion
     delay(1);            // delay in milliseconds (nominal MCP3550-60 rate: 66.7 msec => 15 Hz)
     i=0;                // use i as loop counter

     do {
       i++;
       delayMicroseconds(50);                            // loop keeps trying for up to 1 second
     } while ((digitalRead(MISO)==HIGH) && (i < 2000));   // wait for bit to drop low (ready)

     w = readword();    // data in:  32-bit word gets 24 bits via SPI port

     //OVL = ((w & 0x80000000) != 0x00000000);  // ADC negative overflow bit (input > +Vref)
     //OVH = ((w & 0x40000000) != 0x00000000);  // ADC positive overflow bit (input < -Vref)
  
     if ((i < 10000)) {
       n++;
       x = w <<2;  // to use the sign bit
       x = x/1024; // to move the LSB to bit 0 position
       delta = x - mean;
       mean += delta/n;
     }
   } // end for i..

  double vadc = 1 ;
  double vadc_calib = 1 ;
  
  vadc = 4089*mean;

  for(int t=0; t<21; t++){
    vadc = vadc/2;
  }


  //calibration
  //vadc_calib = map(vadc,-1988,1995,-2019,2026); 
  vadc_calib = vadc;
  
  digitalWrite(CS,HIGH);
  if(type=="I"){
    if(chip=="bot"){
      vadc_calib=vadc_calib/10;//with 10.4 Ohm resistor and wires
    }
    else if(chip=="top"){
      vadc_calib=vadc_calib/10;//with 10.4 Ohm resistor and wires
    }
  }
  

  return vadc_calib;


  
}//end of adcreadfct

unsigned long readword() {
  union {
    unsigned long svar;
    byte c[4];
  } w;        // allow access to 4-byte word, or each byte separately
 
  w.c[3] = SPI.transfer(0x00);  // fill 3 bytes with data: 22 bit signed int + 2 overflow bits
  w.c[2] = SPI.transfer(0x00);
  w.c[1] = SPI.transfer(0x00);
  w.c[0]=0x00;                  // low-order byte set to zero
  return(w.svar);    // return unsigned long word
} // end readword()



//===========================================================================================
//====================IV sweep===============================================================
void sweep(String cell, float Vstart, float Vend, int Nbofpoints, float delaytime){
  float Vstep = abs(Vend-Vstart)/Nbofpoints;
  if(Vstart>Vend){
    Vstep=-Vstep;
  }
 
  //digitalWrite(LED_BUILTIN, HIGH);
  
  for(int i=0;i<=Nbofpoints;i++){
    double result;
    write_(cell,"D",Vstart+i*Vstep); 
   
    result=read_("V",cell);
    Serial.print(result);
    
    result=read_("I",cell);
    Serial.print(",");
    Serial.println(result);

  }
  //digitalWrite(LED_BUILTIN, LOW);
  write_(cell,"D",0); 
}

//===========================================================================================
//========================MPPT===============================================================
void mpp(String cell, float Vstart, float Vstep, float duration){ //perturbe&observe algorithm
  unsigned long start = millis();
  write_(cell,"D",0);
  float Vapplied = Vstart;
  write_(cell,"D",Vapplied); 
  double V0=read_("V",cell);
  double V1=0;
  Serial.print(V0);
  double I0 =read_("I",cell);
  double I1=0;
  double Power0 = V0 * (-I0);
  Serial.print(",");
  Serial.print(I0);  
  Serial.print(",");
  Serial.print(Power0);  
  Serial.print(",");
  float timenow=(millis()-start)/1000.0;
  Serial.println(timenow);
  Vapplied+=Vstep;
  double Power1=0;
  do{
    Power0=V0 * (-I0);
    write_(cell,"D",Vapplied);
    V1=read_("V",cell);
    I1 =read_("I",cell);
    Serial.print(V1);
    Serial.print(",");
    Serial.print(I1);  
    Serial.print(",");
    Power1=V1 * (-I1);
    Serial.print(Power1);  
    Serial.print(",");
    timenow=(millis()-start)/1000.0;
    Serial.println(timenow);

    if (Serial.available()>0) {
      str = Serial.readString();
      if(str.substring(0,4)=="STOP"){
        timenow=duration;
        Serial.println("stoparduino");
      }
    }
    
    if(Power1>Power0){
      if(V1>V0){
        Vapplied = Vapplied+Vstep;
      }
      else {
        Vapplied = Vapplied-Vstep;
      }
    }
    else {
      if(V1>V0){
        Vapplied = Vapplied-Vstep;
      }
      else {
        Vapplied = Vapplied+Vstep;
      }
    }
    V0=V1;
    I0=I1;
    delay(200);
  }while(timenow<duration);
  write_(cell,"D",0);  
}


void mppboth(float Vstarttop,float Vstartbot, float Vstep, float duration){
  unsigned long start = millis();
  write_("top","D",0);
  write_("bot","D",0);
  float Vappliedtop =Vstarttop;
  float Vappliedbot =Vstartbot;
  
  write_("bot","D",Vstartbot); 
  double V0bot=read_("V","bot");
  double V1bot=0;
  Serial.print(V0bot);
  double I0bot =read_("I","bot");
  double I1bot=0;
  double Power0bot = V0bot * (-I0bot);
  Serial.print(",");
  Serial.print(I0bot);  
  Serial.print(",");
  Serial.print(Power0bot);  
  Serial.print(",");
  
  write_("top","D",Vstarttop); 
  double V0top=read_("V","top");
  double V1top=0;
  Serial.print(V0top);
  double I0top =read_("I","top");
  double I1top=0;
  double Power0top = V0top * (-I0top);
  Serial.print(",");
  Serial.print(I0top);  
  Serial.print(",");
  Serial.print(Power0top);  
  Serial.print(",");
  
  float timenow=(millis()-start)/1000.0;
  Serial.println(timenow);
  
  Vappliedtop+=Vstep;
  Vappliedbot+=Vstep;
  double Power1top=0;
  double Power1bot=0;
  do{
    Power0bot=V0bot * (-I0bot);
    write_("bot","D",Vappliedbot);
    V1bot=read_("V","bot");
    I1bot =read_("I","bot");
    Serial.print(V1bot);
    Serial.print(",");
    Serial.print(I1bot);  
    Serial.print(",");
    Power1bot=V1bot * (-I1bot);
    Serial.print(Power1bot);  
    Serial.print(",");
    
    Power0top=V0top * (-I0top);
    write_("top","D",Vappliedtop);
    V1top=read_("V","top");
    I1top =read_("I","top");
    Serial.print(V1top);
    Serial.print(",");
    Serial.print(I1top);  
    Serial.print(",");
    Power1top=V1top * (-I1top);
    Serial.print(Power1top);  
    Serial.print(",");
    
    timenow=(millis()-start)/1000.0;
    Serial.println(timenow);

    if (Serial.available()>0) {
      str = Serial.readString();
      if(str.substring(0,4)=="STOP"){
        timenow=duration;
        Serial.println("stoparduino");
      }
    }
    
    if(Power1bot>Power0bot){
      if(V1bot>V0bot){
        Vappliedbot = Vappliedbot+Vstep;
      }
      else {
        Vappliedbot = Vappliedbot-Vstep;
      }
    }
    else {
      if(V1bot>V0bot){
        Vappliedbot = Vappliedbot-Vstep;
      }
      else {
        Vappliedbot = Vappliedbot+Vstep;
      }
    }
    V0bot=V1bot;
    I0bot=I1bot;
    
    if(Power1top>Power0top){
      if(V1top>V0top){
        Vappliedtop = Vappliedtop+Vstep;
      }
      else {
        Vappliedtop = Vappliedtop-Vstep;
      }
    }
    else {
      if(V1top>V0top){
        Vappliedtop = Vappliedtop-Vstep;
      }
      else {
        Vappliedtop = Vappliedtop+Vstep;
      }
    }
    V0top=V1top;
    I0top=I1top;
    delay(200);
  }while(timenow<duration);
  write_("top","D",0);
  write_("bot","D",0); 
}

void VocTrackboth(float Vstarttop,float Vstartbot, float Vstep, float duration){
  unsigned long start = millis();
  write_("top","D",0);
  write_("bot","D",0);
  float Vappliedtop =Vstarttop;
  float Vappliedbot =Vstartbot;
  
  write_("bot","D",Vstartbot); 
  double V0bot=read_("V","bot");
  double V1bot=0;
  Serial.print(V0bot);
  double I0bot =read_("I","bot");
  double I1bot=0;
  double Power0bot = V0bot * (-I0bot);
  Serial.print(",");
  Serial.print(I0bot);  
  Serial.print(",");
  Serial.print(Power0bot);  
  Serial.print(",");
  
  write_("top","D",Vstarttop); 
  double V0top=read_("V","top");
  double V1top=0;
  Serial.print(V0top);
  double I0top =read_("I","top");
  double I1top=0;
  double Power0top = V0top * (-I0top);
  Serial.print(",");
  Serial.print(I0top);  
  Serial.print(",");
  Serial.print(Power0top);  
  Serial.print(",");
  
  float timenow=(millis()-start)/1000.0;
  Serial.println(timenow);
  
  Vappliedtop+=Vstep;
  Vappliedbot+=Vstep;
  double Power1top=0;
  double Power1bot=0;
  do{
    Power0bot=V0bot * (-I0bot);
    write_("bot","D",Vappliedbot);
    V1bot=read_("V","bot");
    I1bot =read_("I","bot");
    Serial.print(V1bot);
    Serial.print(",");
    Serial.print(I1bot);  
    Serial.print(",");
    Power1bot=V1bot * (-I1bot);
    Serial.print(Power1bot);  
    Serial.print(",");
    
    Power0top=V0top * (-I0top);
    write_("top","D",Vappliedtop);
    V1top=read_("V","top");
    I1top =read_("I","top");
    Serial.print(V1top);
    Serial.print(",");
    Serial.print(I1top);  
    Serial.print(",");
    Power1top=V1top * (-I1top);
    Serial.print(Power1top);  
    Serial.print(",");
    
    timenow=(millis()-start)/1000.0;
    Serial.println(timenow);

    if (Serial.available()>0) {
      str = Serial.readString();
      if(str.substring(0,4)=="STOP"){
        timenow=duration;
        Serial.println("stoparduino");
      }
    }
    
    if(I1bot>0){
      Vappliedbot = Vappliedbot-Vstep;
    }
    else {
      Vappliedbot = Vappliedbot+Vstep;
    }
    V0bot=V1bot;
    I0bot=I1bot;
    
    if(I1top>0){
      Vappliedtop = Vappliedtop-Vstep;
    }
    else {
      Vappliedtop = Vappliedtop+Vstep;
    }
    V0top=V1top;
    I0top=I1top;
    delay(200);
  }while(timenow<duration);
  write_("top","D",0);
  write_("bot","D",0); 
}

void VocTrack(String cell, float Vstart, float Vstep, float duration){ //perturbe&observe algorithm
  unsigned long start = millis();
  write_(cell,"D",0);
  float Vapplied = Vstart;
  write_(cell,"D",Vapplied); 
  double V0=read_("V",cell);
  double V1=0;
  Serial.print(V0);
  double I0 =read_("I",cell);
  double I1=0;
  double Power0 = V0 * (-I0);
  Serial.print(",");
  Serial.print(I0);  
  Serial.print(",");
  Serial.print(Power0);  
  Serial.print(",");
  float timenow=(millis()-start)/1000.0;
  Serial.println(timenow);
  Vapplied+=Vstep;
  double Power1=0;
  do{
    Power0=V0 * (-I0);
    write_(cell,"D",Vapplied);
    V1=read_("V",cell);
    I1 =read_("I",cell);
    Serial.print(V1);
    Serial.print(",");
    Serial.print(I1);  
    Serial.print(",");
    Power1=V1 * (-I1);
    Serial.print(Power1);  
    Serial.print(",");
    timenow=(millis()-start)/1000.0;
    Serial.println(timenow);

    if (Serial.available()>0) {
      str = Serial.readString();
      if(str.substring(0,4)=="STOP"){
        timenow=duration;
        Serial.println("stoparduino");
      }
    }

    if(I1>0){
      Vapplied = Vapplied-Vstep;
    }
    else {
      Vapplied = Vapplied+Vstep;
    }
    V0=V1;
    I0=I1;
    delay(200);
  }while(timenow<duration);
  write_(cell,"D",0);  
}

