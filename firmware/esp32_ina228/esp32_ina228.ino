// Firmware del banco de medicion (LilyGO TTGO LoRa32 + INA228) para el flujo de
// CARACTERIZACION y VALIDACION de ventana unica. Reemplaza al chopper viejo
// (ADS1115 + INA240): ya NO se resta idle en la ESP32; el idle se mide como una
// ventana mas desde el host (medir_uno con la carga idle.S).
//
// Semantica de la ventana (harness.S del SoC):
//   gpio_high  -> flanco de subida: abre la ventana (empieza a acumular P)
//   gpio_low   -> flanco de bajada: cierra la ventana (promedia y publica)
// La ESP32 promedia la potencia instantanea del riel +5V mientras la ventana
// esta abierta y, al cerrarse, sube p_avg (+ n muestras y duracion) al Sheet,
// pestana 'inbox'. El host lo recoge con sheet.Inbox.get_pavg().
//
// Lectura del INA228 tomada del sketch de prueba ina228_full_test.ino, pero con
// ADCRANGE=1 (paso de 78,125 nV, 4x resolucion) para la senal dinamica pequena
// del nucleo, coherente con la tesis (seccion 4.4).
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- Red / Sheet ---
// Credenciales y URL del Web App en secrets.h (local, no versionado);
// ver secrets.h.example para crear el suyo.
#include "secrets.h"

// Etiqueta opcional de la corrida (no la usa el host, solo diagnostico).
#ifndef RUN_LABEL
#define RUN_LABEL "ina228"
#endif

// --- Pines ---
static const int SDA_PIN  = 21;
static const int SCL_PIN  = 22;
static const int SYNC_PIN = 19;    // senal de ventana del FPGA (GPIO8 -> PMOD -> aqui)
static const int LED_PIN  = 25;    // LED verde integrado (TTGO LoRa32 V2.1): ON = midiendo
static const int LORA_CS_PIN    = 18;
static const int LORA_RESET_PIN = 23;
static const uint8_t OLED_ADDR = 0x3C;

// --- INA228 ---
// R015 = 15 mohm (resistor de derivacion integrado del modulo).
static const float RSHUNT_OHMS = 0.015f;
// CONFIG (0x00): ADCRANGE=1 (bit 4) -> fondo de escala +/-40.96 mV, LSB 78.125 nV.
static const uint16_t INA_CONFIG     = 0x0010;
// ADC_CONFIG (0x01): continuo VBUS+VSHUNT, 540 us/canal, promedio 4x.
static const uint16_t INA_ADC_CONFIG = 0xB901;
// LSB de tension: VSHUNT con ADCRANGE=1 = 78.125 nV; VBUS = 195.3125 uV.
static const float VSHUNT_LSB_V = 0.000000078125f;
static const float VBUS_LSB_V   = 0.0001953125f;

static const uint32_t END_GAP_MS   = 1500;  // reservado; el cierre lo da el flanco de bajada
static const uint8_t  SKIP_AFTER_EDGE = 2;  // descarta muestras tras un flanco (transitorio)

Adafruit_SSD1306 display(128, 64, &Wire, -1);

uint8_t inaAddr = 0;
bool    oledOk = false;
bool    wifiReady = false;

// --- Estado de la ventana ---
double   sumP = 0.0;
uint32_t cntP = 0;
uint32_t winStartMs = 0;
bool     running = false;
bool     prevHigh = false;
bool     sawLow = false;    // exige ver un bajo antes de armar (ignora el alto de arranque)
uint8_t  skip = 0;

// Ultimo resultado (para el OLED en reposo).
double   lastPavg = 0.0;
uint32_t lastN = 0, lastDur = 0;
bool     haveResult = false;

uint32_t lastDispMs = 0;

// ---------------------------------------------------------------------------
// I2C del INA228
// ---------------------------------------------------------------------------
uint32_t readReg(uint8_t addr, uint8_t reg, uint8_t bytes) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return 0;
  uint8_t got = Wire.requestFrom((int)addr, (int)bytes);
  if (got != bytes) {
    while (Wire.available()) Wire.read();
    return 0;
  }
  uint32_t value = 0;
  while (Wire.available()) value = (value << 8) | Wire.read();
  return value;
}

void writeReg16(uint8_t addr, uint8_t reg, uint16_t value) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(value >> 8);
  Wire.write(value & 0xFF);
  Wire.endTransmission();
}

int32_t signExtend20(uint32_t value) {
  value &= 0xFFFFF;
  return (value & 0x80000) ? (int32_t)(value | 0xFFF00000) : (int32_t)value;
}

bool findIna228() {
  for (uint8_t addr = 0x40; addr <= 0x4F; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() != 0) continue;
    uint16_t man = (uint16_t)readReg(addr, 0x3E, 2);
    uint16_t dev = (uint16_t)readReg(addr, 0x3F, 2);
    Serial.printf("I2C 0x%02X MAN=0x%04X DEV=0x%04X\n", addr, man, dev);
    if (man == 0x5449 && ((dev >> 4) == 0x228)) {
      inaAddr = addr;
      return true;
    }
  }
  return false;
}

// Temperatura interna del INA228 [C] (DIETEMP 0x06: 16 bits, 7.8125 mC/LSB).
// Se registra junto a cada ventana para poder ATRIBUIR la deriva del piso
// (silicio FPGA vs instrumento/shunt); no corrige nada por si sola.
float readInaTemp() {
  int16_t raw = (int16_t)readReg(inaAddr, 0x06, 2);
  return raw * 0.0078125f;
}

// Potencia instantanea del riel +5V (V_bus * I_shunt).
float readPower() {
  int32_t  vshRaw  = signExtend20(readReg(inaAddr, 0x04, 3) >> 4);
  uint32_t vbusRaw = readReg(inaAddr, 0x05, 3) >> 4;
  float vshuntV = vshRaw * VSHUNT_LSB_V;
  float vbusV   = vbusRaw * VBUS_LSB_V;
  float currentA = vshuntV / RSHUNT_OHMS;
  return vbusV * currentA;
}

// ---------------------------------------------------------------------------
// OLED
// ---------------------------------------------------------------------------
void header(const char* title) {
  display.clearDisplay();
  display.fillRect(0, 0, 128, 11, SSD1306_WHITE);
  display.setTextColor(SSD1306_BLACK);
  display.setTextSize(1);
  display.setCursor(3, 2); display.print(title);
  display.setTextColor(SSD1306_WHITE);
}
void line(int row, const char* s) {
  display.setCursor(0, 15 + row * 12); display.print(s);
}

void screenIdle() {
  if (!oledOk) return;
  header("INA228 ventana");
  char b[26];
  if (wifiReady) { snprintf(b, sizeof(b), "WiFi %lddBm", (long)WiFi.RSSI()); line(0, b); }
  else           line(0, "WiFi: ...");
  line(1, "esperando GPIO");
  if (haveResult) { snprintf(b, sizeof(b), "ult: %.4f W", lastPavg); line(2, b); }
  display.display();
}

void screenRun(float P) {
  if (!oledOk) return;
  header("MIDIENDO");
  char b[26];
  snprintf(b, sizeof(b), "P: %.4f W", P);                       line(0, b);
  snprintf(b, sizeof(b), "n: %lu", (unsigned long)cntP);        line(1, b);
  snprintf(b, sizeof(b), "t: %lu ms", (unsigned long)(millis() - winStartMs)); line(2, b);
  display.display();
}

void screenResult() {
  if (!oledOk) return;
  header("LISTO");
  char b[26];
  display.setTextSize(2);
  snprintf(b, sizeof(b), "%.4f", lastPavg);
  display.setCursor(0, 16); display.print(b);
  display.setTextSize(1); display.print(" W");
  snprintf(b, sizeof(b), "n %lu  %lums", (unsigned long)lastN, (unsigned long)lastDur); line(3, b);
  display.display();
}

// ---------------------------------------------------------------------------
// WiFi / Sheet
// ---------------------------------------------------------------------------
// BLOQUEANTE: solo se llama al subir una ventana (uploadWindow), nunca antes
// de medir. En setup() el WiFi se arranca sin esperar (ver nota alli).
void connectWifi() {
  if (WiFi.status() == WL_CONNECTED) { wifiReady = true; return; }
  WiFi.mode(WIFI_STA); WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 20000) delay(300);
  wifiReady = (WiFi.status() == WL_CONNECTED);
}

// Publica la ventana en 'inbox' (default del Apps Script). El host lee 'p_avg'.
// Reintenta con backoff: el Apps Script da 500 transitorios (arranque en frio,
// crear pestana) igual que en sheet.py. Sin esto, un 500 pierde la ventana y el
// host se queda esperando la fila para siempre.
bool uploadWindow(double pavg, uint32_t n, uint32_t durMs) {
  if (!wifiReady) connectWifi();
  if (!wifiReady) { Serial.println("WiFi: no conectado"); return false; }
  float tIna = readInaTemp();
  String url = String(SCRIPT_URL) +
               "?profile=" + RUN_LABEL +
               "&p_avg=" + String(pavg, 6) +
               "&samples=" + String(n) +
               "&duration_ms=" + String(durMs) +
               "&temp_ina=" + String(tIna, 2);
  for (int intento = 1; intento <= 4; intento++) {
    WiFiClientSecure client; client.setInsecure(); client.setTimeout(20000);
    HTTPClient https; https.begin(client, url);
    https.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    https.setConnectTimeout(15000); https.setTimeout(20000);
    int code = https.GET(); String resp = https.getString(); https.end();
    Serial.printf("Sheets intento %d HTTP=%d resp=%s\n", intento, code, resp.c_str());
    if (code > 0 && code < 400) return true;
    delay(1500 * intento);   // backoff creciente
  }
  Serial.println("Sheets: fallaron los 4 intentos, ventana perdida");
  return false;
}

// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(300);

  // Mantiene la radio LoRa en un estado conocido (no interfiere el SPI/I2C).
  pinMode(LORA_CS_PIN, OUTPUT);    digitalWrite(LORA_CS_PIN, HIGH);
  pinMode(LORA_RESET_PIN, OUTPUT); digitalWrite(LORA_RESET_PIN, LOW);
  pinMode(SYNC_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);        digitalWrite(LED_PIN, LOW);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  oledOk = display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  if (oledOk) { header("BOOT"); line(0, "SDA21 SCL22"); line(1, "buscando INA..."); display.display(); }

  // WiFi en segundo plano, SIN esperar: esperar aqui (hasta 20 s) dejaba a la
  // ESP32 ciega al GPIO durante el arranque, y la primera ventana tras un
  // reset caia dentro de ese bloqueo y se perdia siempre (el host la repetia).
  // La conexion recien se necesita al SUBIR la ventana, y uploadWindow()
  // llama a connectWifi() si aun no esta lista.
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.println();
  Serial.println("Banco INA228 (ventana unica)");

  if (!findIna228()) {
    Serial.println("No encontre INA228.");
    if (oledOk) { header("NO INA"); line(0, "revisa cableado"); line(1, "A0/A1 a GND"); display.display(); }
    return;
  }

  Serial.printf("INA228 OK addr=0x%02X\n", inaAddr);
  writeReg16(inaAddr, 0x00, INA_CONFIG);       // ADCRANGE=1
  writeReg16(inaAddr, 0x01, INA_ADC_CONFIG);   // continuo VBUS+VSHUNT
  screenIdle();
  Serial.println("Esperando ventana en GPIO19...");
}

void loop() {
  if (!inaAddr) { delay(1000); return; }

  bool high = digitalRead(SYNC_PIN) == HIGH;
  float P = readPower();
  uint32_t now = millis();
  wifiReady = (WiFi.status() == WL_CONNECTED);   // el begin() de setup conecta solo

  if (!high) sawLow = true;   // ya vimos un bajo -> el harness ya ejecuto gpio_init

  // Abre la ventana en el primer flanco BAJO->ALTO tras haber visto un bajo. Asi
  // se ignora el alto inicial con que arranca la FPGA / la carga por JTAG.
  if (high && !prevHigh && sawLow && !running) {
    running = true;
    sumP = 0.0; cntP = 0;
    winStartMs = now;
    digitalWrite(LED_PIN, HIGH);   // LED encendido mientras la ventana mide
  }

  if (high != prevHigh) { skip = SKIP_AFTER_EDGE; prevHigh = high; }

  if (running && high && skip == 0) {
    sumP += P; cntP++;
  }
  if (skip > 0) skip--;

  // Cierra la ventana en el flanco ALTO->BAJO: promedia y publica.
  if (running && !high && cntP > 0) {
    digitalWrite(LED_PIN, LOW);    // ventana cerrada
    double pavg = sumP / cntP;
    uint32_t dur = now - winStartMs;
    Serial.printf("VENTANA p_avg=%.6f W  n=%lu  dur=%lu ms\n",
                  pavg, (unsigned long)cntP, (unsigned long)dur);
    lastPavg = pavg; lastN = cntP; lastDur = dur; haveResult = true;
    screenResult();
    uploadWindow(pavg, cntP, dur);
    running = false;
    sawLow = false;          // exige un nuevo bajo antes de re-armar
    lastDispMs = millis();
  }

  // Refresca el OLED a ~1 Hz (la I2C del OLED frena el muestreo).
  if (now - lastDispMs > 1000) {
    lastDispMs = now;
    if (running) screenRun(P);
    else         screenIdle();
  }

  delay(2);   // ~500 lecturas/s nominal (el INA convierte cada ~4 ms)
}
