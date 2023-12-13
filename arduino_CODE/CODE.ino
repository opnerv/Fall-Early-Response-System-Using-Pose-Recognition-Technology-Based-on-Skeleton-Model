#define USE_ARDUINO_INTERRUPTS true
#include <PulseSensorPlayground.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "dd";
const char* password = "1234";
const char* serverAddress = "192.168.0.11";
const int serverPort = 3200;

const int PulseWire = 0;
int Threshold = 550;

PulseSensorPlayground pulseSensor;

void setup() {   
  Serial.begin(9600);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  pulseSensor.analogInput(PulseWire);
  pulseSensor.setThreshold(Threshold);

  if (pulseSensor.begin()) {
    Serial.println("We created a pulseSensor Object !");
  }
}

void loop() {
  int myBPM = pulseSensor.getBeatsPerMinute();

  if (pulseSensor.sawStartOfBeat()) {
    Serial.println("♥ A HeartBeat Happened !");
    Serial.print("BPM: ");
    Serial.println(myBPM);
    
    // Send myBPM value to the server
    sendDataToServer(myBPM);
  }

  delay(20);
}

void sendDataToServer(int data) {
  HTTPClient http;

  String url = "http://" + String(serverAddress) + ":" + String(serverPort) + "/get_value";

  String jsonPayload = "{\"data\":" + String(data) + "}";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
  } else {
    Serial.println("HTTP POST request failed");
  }

  http.end();
}