#include <BluetoothSerial.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ESP32Servo.h>

#define SS_PIN  2
#define RST_PIN 15
#define Ir1 36
#define Ir2 39
#define Ir3 34
#define Ir4 35
#define buzzer 27

#define enter 33
#define Ir5 32

int bin = 0;
Servo servoin ;
Servo servoout ;

BluetoothSerial SerialBT;
MFRC522 mfrc522(SS_PIN, RST_PIN);

char t ;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_RFID"); // Name of the Bluetooth device
  pinMode(Ir1, INPUT);
  pinMode(Ir2, INPUT);
  pinMode(Ir3, INPUT);
  pinMode(Ir4, INPUT);
  pinMode(buzzer, OUTPUT);

  pinMode(enter, INPUT);
  pinMode(Ir5, INPUT);

  servoin.attach(25);
  servoout.attach(26);

  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Scan RFID...");
}

void loop() {
    t = 0;
   
   servoin.write(0);
   servoout.write(0);
   
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String rfid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      rfid += String(mfrc522.uid.uidByte[i], HEX);  }
    Serial.print(rfid);
    SerialBT.println(rfid); // Send over Bluetooth
    delay(1000); }

  if (digitalRead(enter) == bin ){
    SerialBT.println("car enter");
    delay(1000); }

  if(SerialBT.available()){
  t = SerialBT.read();
  Serial.println(t); }

  if (t == 'A'){
   servoin.write(90); }
   
  if (t == 'C'){
  servoout.write(90);
  delay(2000); }

  if (t == 'T'){
    digitalWrite(buzzer, HIGH);
    delay(1000);
    digitalWrite(buzzer, LOW);}

  String sensor1String = String(digitalRead(Ir1));
  String sensor2String = String(digitalRead(Ir2));
  String sensor3String = String(digitalRead(Ir3));
  String sensor4String = String(digitalRead(Ir4));
  String sensor5String = String(digitalRead(Ir5));

  String transmitString = sensor1String + "," + sensor2String + "," + sensor3String + "," + sensor4String + "," + sensor5String ;
  SerialBT.println(transmitString);

  delay(1000);  }