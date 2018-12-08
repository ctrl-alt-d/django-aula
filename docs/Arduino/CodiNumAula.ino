#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <user_interface.h>

/* ------------------- WIFI ---------------------- */
const char* ssid = "docent";
const char* password = "___password_de_la_wifi___" ; 


const char* host = "djau.cendrassos.net";
const int httpsPort = 443;
const char* fingerprint = "99 05 E0 DA 52 56 F1 01 41 EE F2 C6 EE 98 A0 84 F5 45 56 52";  //finger key del certificat ssl
bool connectat = false;
//WiFi.begin(ssid, keyIndex, key); 
//keyIndex: WEP encrypted networks can hold up to 4 different keys. This identifies which key you are going to use.
//key: a hexadecimal string used as a security code for WEP encrypted networks.

/* ------------------- Crystal -------------------- */
LiquidCrystal_I2C lcd(0x3F,20,4);  

/* ------------------- Global ---------------------- */
String urlNow = "https://djau.cendrassos.net/aules/getStatus/?aula=313&key=___api__key____&outputformat=2liniesNow";
String urlNext = "https://djau.cendrassos.net/aules/getStatus/?aula=313&key=___api__key____&outputformat=2liniesNext";
String url = urlNow;
String serialMsg = "";

/* ------------------- setup ---------------------- */
void setup()
{

 
  //uint8_t mac[6] {0x9c, 0xb6, 0xd0, 0x1f, 0xbb, 0xe3};
  //wifi_set_macaddr(STATION_IF, mac);
  Serial.begin(9600);
  lcd.init();  
  printMsgL1("djau!");
  printMsgL2("");
}

void loop()
{
  actualitzaMarcador();
  delay(1000*15); //cada 15 segons
}

/* ------------------- Functions Core ---------------------- */
void actualitzaMarcador() {

  //
  if (!connectaWifi()) {
    return;
  }
  
    // Use WiFiClientSecure class to create TLS connection
  WiFiClientSecure client;
  serialMsg = "connecting to " + String(host);
  Serial.println(serialMsg);
  connectat = client.connect(host, httpsPort);
  if (!connectat) {
    serialMsg = "djau on ets?";
    Serial.println(serialMsg);
    printMsgL1( serialMsg);
    return;
  }

  if (client.verify(fingerprint, host)) {
    Serial.println("certificate matches");
  } else {
    Serial.println("certificate doesn't match");   
  }

  //switch urls ---------------------------------------------------------------
  url = (url==urlNext)?urlNow:urlNext;
  
  Serial.print("requesting URL: ");
  Serial.println(url);

  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "User-Agent: ESP8266\r\n" +
               "Connection: close\r\n\r\n");

  Serial.println("request sent");
  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") {
      Serial.println("headers received");
      break;
    }
  }

  String line1 = client.readStringUntil('\n');
  String line2 = client.readStringUntil('\n');
  Serial.println("reply was:");
  Serial.println("==========");
  Serial.println(line1);
  Serial.println(line2);
  Serial.println("==========");
  Serial.println("closing connection");

  //switch urls ------------------------------------------------------------------
  connectat = client.connect(host, httpsPort);
  if (!connectat) {
    serialMsg = "djau on ets?";
    Serial.println(serialMsg);
    printMsgL1( serialMsg);
    return;
  }
  url = (url==urlNext)?urlNow:urlNext;
  
  Serial.print("requesting URL: ");
  Serial.println(url);

  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "User-Agent: ESP8266\r\n" +
               "Connection: close\r\n\r\n");

  Serial.println("request sent");
  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") {
      Serial.println("headers received");
      break;
    }
  }

  String line3 = client.readStringUntil('\n');
  String line4 = client.readStringUntil('\n');
  Serial.println("reply was:");
  Serial.println("==========");
  Serial.println(line3);
  Serial.println(line4);
  Serial.println("==========");
  Serial.println("closing connection");

  // ------------------------------------------------------------------------------


  for ( int k=0; k<5; k++ ) {
    printMsgL1(line1);
    printMsgL2(line2);
    delay( 1000*5);
    for ( int j=0; j<16; j++ ) {
      lcd.scrollDisplayLeft();
      delay(200);
    }
    printMsgL1(line3);
    printMsgL2(line4);
    delay( 1000*5);
    for ( int j=0; j<16; j++ ) {
      lcd.scrollDisplayLeft();
      delay(200);
    }
  }
}

/* ------------------- Funcions WIFI ---------------------- */
bool connectaWifi() {

  if (connectat) return true;

  //
  serialMsg = "Connectant " + String(ssid);
  printMsgL1(serialMsg);
  Serial.println(serialMsg);

  //
  WiFi.begin(ssid, password);
  int intents = 40;
  int nextDelay = 10;
  do {
    Serial.print(".");
    delay(nextDelay);
    connectat = ( WiFi.status() == WL_CONNECTED);
    intents--;
    nextDelay = 200;
  } while (intents >0 && !connectat);

  //
  if (connectat) {
    serialMsg = "WiFi connectada " + String(WiFi.localIP());

  } else {
    
    serialMsg = "No Wifi no fun      " + String( WiFi.macAddress() );
    Serial.println( );
  }
  printMsgL1(serialMsg);
  Serial.println(serialMsg);

  return connectat;

}

/* ------------------- Funcioins Crystal ---------------------- */
void printMsgL1(String msg) {
                    
  // Print a message to the LCD.
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("                ");  
  lcd.setCursor(0,0);
  lcd.print(msg);
}

void printMsgL2(String msg) {
                    
  // Print a message to the LCD.
  lcd.backlight();
  lcd.setCursor(0,1);
  lcd.print("                ");
  lcd.setCursor(0,1);
  lcd.print(msg);
}

