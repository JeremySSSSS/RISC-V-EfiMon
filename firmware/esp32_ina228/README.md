# esp32_ina228 — power-meter firmware

Arduino firmware for the ESP32 that reads the INA228 (shunt and bus voltage on
the FPGA rail), integrates power over windows, and posts each window (`p_avg`,
`duration_ms`, energy) to the spreadsheet's `inbox` tab via the Apps Script Web
App. The bench (`common/sheet.py`) pairs each window with the run that produced
it using the duration as a guard.

## Configuration (required before building)

Credentials live in `secrets.h`, which is **not versioned**:

```
cp secrets.h.example secrets.h
# edit WIFI_SSID, WIFI_PASS and SCRIPT_URL (same URL as common/config_local.py)
```

## Build and flash

```
arduino-cli compile --fqbn esp32:esp32:esp32 .
arduino-cli upload --fqbn esp32:esp32:esp32 -p /dev/ttyUSB0 .
```
