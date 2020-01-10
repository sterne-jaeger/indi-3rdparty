/*  Streaming functions for the BMP085 environment sensor.

    Copyright (C) 2019 Wolfgang Reissenberger <sterne-jaeger@t-online.de>

    This application is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.
*/
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085_U.h>

Adafruit_BMP085_Unified bmp = Adafruit_BMP085_Unified(10085);

struct {
  bool status;
  float temperature;
  float pressure;
} bmpData;

void updateBMP() {
  if (bmpData.status || (bmpData.status = bmp.begin())) {
    bmp.getTemperature(&bmpData.temperature);
    bmp.getPressure(&bmpData.pressure);
  }
}

void serializeBMP(JsonDocument &doc) {

  JsonObject data = doc.createNestedObject("BMP085");
  data["init"] = bmpData.status;

  if (bmpData.status) {
    data["Temp"] = bmpData.temperature;
    data["Pres"] = bmpData.pressure / 100;
  }
}
