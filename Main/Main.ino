#include "DHT.h"
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <Servo.h>

Servo ser;
const char* ssid = "Orchid";
const char* password = "2Two%Tang0";
String serverName = "http://ec2-13-233-63-133.ap-south-1.compute.amazonaws.com:5000/dataDump";
boolean door = false, fan = false, light = false, aut = false;
String fin;
float humidity, temperature;
long t2 = millis(), t1, tm = millis();

DHT dht = DHT(D1, DHT11, 6); // DHT(uint8_t pin, uint8_t type, uint8_t count=6);

void httpGET()
{
    if(WiFi.status()== WL_CONNECTED)
    {
        StaticJsonDocument<96> doc;
        HTTPClient http;
        String serverPath = serverName;
        http.begin(serverPath.c_str());
        int httpResponseCode = http.GET();
        if (httpResponseCode>0) 
        {
            String payload = http.getString();
            deserializeJson(doc, payload);
            fan = doc["Fan"].as<boolean>();
            light = doc["Light"].as<boolean>();
            door = doc["Door"].as<boolean>();
            aut = doc["Auto"].as<boolean>();
            doc.clear();
            Serial.print(fan);
            Serial.print(" ");
            Serial.print(light);
            Serial.print(" ");
            Serial.print(aut);
            Serial.print(" ");
            Serial.println(door);
        }
        else 
        {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    }
    else 
    {
        Serial.println("WiFi Disconnected");
    }
}

void httpPost()
{
    if(WiFi.status()== WL_CONNECTED)
    {
        StaticJsonDocument<32> doc1;
        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "application/json");
        doc1["humid"] = humidity;
        doc1["temp"] = temperature;
        serializeJson(doc1, fin);
        Serial.println(fin);
        int httpResponseCode = http.POST(fin);
        fin = "";
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        http.end();
    }
    else 
    {
        Serial.println("WiFi Disconnected");
    }
}

void setup()
{
    Serial.begin(9600);
    dht.begin();
    WiFi.begin(ssid, password);
    Serial.println("Connecting");
    while(WiFi.status() != WL_CONNECTED) 
    {
        delay(500);
        Serial.print(".");
    }
    pinMode(D2, OUTPUT);
    pinMode(D3, OUTPUT);
    pinMode(D4, OUTPUT);
    pinMode(D5, OUTPUT);
    ser.attach(D6);
    ser.write(0);
}

void loop()
{
    if(millis() - t2 > 1000L)
    {    
        httpGET();
        t2 = millis();
    }
    if(fan == true && aut == false)
    {
        digitalWrite(D2, HIGH);
        digitalWrite(D3, LOW);
    }
    else if(aut == false)
    {
        digitalWrite(D2, LOW);
        digitalWrite(D3, LOW);
    }
    if(light == true)
    {
        digitalWrite(D4, HIGH);
        digitalWrite(D5, LOW);
    }
    else
    {
        digitalWrite(D4, LOW);
        digitalWrite(D5, LOW);
    }
    if(door == true)
    {
        ser.write(90);
        t1 = millis();
    }
    if(millis() - t1 > 10000L)
    {
        ser.write(0);
    }
    if(aut == true)
    {
        if(humidity > 70 || temperature > 28)
        {
            digitalWrite(D2, HIGH);
            digitalWrite(D3, LOW);
        }
        else
        {
            digitalWrite(D2, LOW);
            digitalWrite(D3, LOW);
        }
    }
    if(millis() - tm > 10000L)
    {
        humidity = dht.readHumidity();
        temperature = dht.readTemperature();
        Serial.print(humidity, 1);
        Serial.print("\t");
        Serial.print(temperature, 1);
        httpPost();
        tm = millis();
    }
}