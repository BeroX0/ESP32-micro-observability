#include <Arduino_GFX_Library.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "esp_lcd_touch_axs5106l.h"

#define GFX_BL 23
#define ROTATION 0

#define TOUCH_SDA 18
#define TOUCH_SCL 19
#define TOUCH_RST 20
#define TOUCH_INT 21

#define SCREEN_W 172
#define SCREEN_H 320

Arduino_DataBus *bus = new Arduino_HWSPI(
  15 /* DC */, 14 /* CS */, 1 /* SCK */, 2 /* MOSI */
);

Arduino_GFX *gfx = new Arduino_ST7789(
  bus,
  22 /* RST */, ROTATION, false /* IPS */,
  172 /* width */, 320 /* height */,
  34 /* col_offset1 */, 0 /* row_offset1 */,
  34 /* col_offset2 */, 0 /* row_offset2 */
);

static const char WIFI_SSID[] = "";
static const char WIFI_PASSWORD[] = "";
static const char HOST_TEXT[] = "192.168.1.134";

static const char URL_CPU[]  = "http://192.168.1.134:9090/api/v1/query?query=100%20*%20sum(rate(node_cpu_seconds_total%7Bjob%3D%22node_exporter%22%2Cmode!%3D%22idle%22%7D%5B5m%5D))%20%2F%20count(count(node_cpu_seconds_total%7Bjob%3D%22node_exporter%22%2Cmode%3D%22idle%22%7D)%20by%20(cpu))";
static const char URL_MEM[]  = "http://192.168.1.134:9090/api/v1/query?query=100%20*%20(1%20-%20(node_memory_MemAvailable_bytes%7Bjob%3D%22node_exporter%22%7D%20%2F%20node_memory_MemTotal_bytes%7Bjob%3D%22node_exporter%22%7D))";
static const char URL_DISK[] = "http://192.168.1.134:9090/api/v1/query?query=100%20*%20(1%20-%20(node_filesystem_avail_bytes%7Bjob%3D%22node_exporter%22%2Cmountpoint%3D%22%2Fetc%2Fhosts%22%7D%20%2F%20node_filesystem_size_bytes%7Bjob%3D%22node_exporter%22%2Cmountpoint%3D%22%2Fetc%2Fhosts%22%7D))";
static const char URL_CONN[] = "http://192.168.1.134:9090/api/v1/query?query=up%7Bjob%3D%22node_exporter%22%7D";
static const char URL_RX[]   = "http://192.168.1.134:9090/api/v1/query?query=rate(node_network_receive_bytes_total%7Bjob%3D%22node_exporter%22%2Cdevice%3D%22eth0%22%7D%5B5m%5D)";
static const char URL_TX[]   = "http://192.168.1.134:9090/api/v1/query?query=rate(node_network_transmit_bytes_total%7Bjob%3D%22node_exporter%22%2Cdevice%3D%22eth0%22%7D%5B5m%5D)";

enum MetricKind : uint8_t { MK_PERCENT, MK_BOOL, MK_RATE };
enum MetricState : uint8_t { MS_UNKNOWN, MS_LIVE, MS_STALE, MS_FAIL };

struct Metric {
  const char *title;
  const char *shortLabel;
  const char *url;
  MetricKind kind;
  String rawValue;
  MetricState state;
  int httpCode;
  uint32_t lastGoodMs;
};

enum MetricIndex : uint8_t {
  IDX_CPU = 0,
  IDX_MEM = 1,
  IDX_DISK = 2,
  IDX_CONN = 3,
  IDX_RX = 4,
  IDX_TX = 5,
  METRIC_COUNT = 6
};

Metric metrics[METRIC_COUNT] = {
  {"CPU",  "cpu%", URL_CPU,  MK_PERCENT, "", MS_UNKNOWN, 0, 0},
  {"MEM",  "mem%", URL_MEM,  MK_PERCENT, "", MS_UNKNOWN, 0, 0},
  {"DISK", "disk%", URL_DISK, MK_PERCENT, "", MS_UNKNOWN, 0, 0},
  {"NET",  "conn", URL_CONN, MK_BOOL,    "", MS_UNKNOWN, 0, 0},
  {"RX",   "rx",   URL_RX,   MK_RATE,    "", MS_UNKNOWN, 0, 0},
  {"TX",   "tx",   URL_TX,   MK_RATE,    "", MS_UNKNOWN, 0, 0}
};

bool wifiConfigured = false;
bool wifiStarted = false;
bool wifiConnected = false;
String deviceIpText = "n/a";
uint32_t lastWifiBeginAttempt = 0;

uint32_t tickCounter = 0;
uint32_t lastWifiPoll = 0;
uint32_t lastFetchSweep = 0;
uint32_t lastTick = 0;
uint32_t lastTouchNavMs = 0;
uint8_t fetchIndex = 0;

static const uint32_t HTTP_TIMEOUT_MS = 200;
static const uint32_t FETCH_STEP_MS = 700;
static const uint32_t STALE_TO_FAIL_MS = 30000;
static const uint32_t WIFI_RETRY_MS = 5000;

uint8_t currentPage = 0;
bool touchReady = false;
String lastRenderKey = "";

void drawFooter();
void drawCurrentPage();
void redrawIfChanged();

void lcd_reg_init() {
  static const uint8_t init_operations[] = {
    BEGIN_WRITE,
    WRITE_COMMAND_8, 0x11,
    END_WRITE,
    DELAY, 120,

    BEGIN_WRITE,
    WRITE_C8_D16, 0xDF, 0x98, 0x53,
    WRITE_C8_D8, 0xB2, 0x23,

    WRITE_COMMAND_8, 0xB7,
    WRITE_BYTES, 4,
    0x00, 0x47, 0x00, 0x6F,

    WRITE_COMMAND_8, 0xBB,
    WRITE_BYTES, 6,
    0x1C, 0x1A, 0x55, 0x73, 0x63, 0xF0,

    WRITE_C8_D16, 0xC0, 0x44, 0xA4,
    WRITE_C8_D8, 0xC1, 0x16,

    WRITE_COMMAND_8, 0xC3,
    WRITE_BYTES, 8,
    0x7D, 0x07, 0x14, 0x06, 0xCF, 0x71, 0x72, 0x77,

    WRITE_COMMAND_8, 0xC4,
    WRITE_BYTES, 12,
    0x00, 0x00, 0xA0, 0x79, 0x0B, 0x0A, 0x16, 0x79, 0x0B, 0x0A, 0x16, 0x82,

    WRITE_COMMAND_8, 0xC8,
    WRITE_BYTES, 32,
    0x3F, 0x32, 0x29, 0x29, 0x27, 0x2B, 0x27, 0x28,
    0x28, 0x26, 0x25, 0x17, 0x12, 0x0D, 0x04, 0x00,
    0x3F, 0x32, 0x29, 0x29, 0x27, 0x2B, 0x27, 0x28,
    0x28, 0x26, 0x25, 0x17, 0x12, 0x0D, 0x04, 0x00,

    WRITE_COMMAND_8, 0xD0,
    WRITE_BYTES, 5,
    0x04, 0x06, 0x6B, 0x0F, 0x00,

    WRITE_C8_D16, 0xD7, 0x00, 0x30,
    WRITE_C8_D8, 0xE6, 0x14,
    WRITE_C8_D8, 0xDE, 0x01,

    WRITE_COMMAND_8, 0xB7,
    WRITE_BYTES, 5,
    0x03, 0x13, 0xEF, 0x35, 0x35,

    WRITE_COMMAND_8, 0xC1,
    WRITE_BYTES, 3,
    0x14, 0x15, 0xC0,

    WRITE_C8_D16, 0xC2, 0x06, 0x3A,
    WRITE_C8_D16, 0xC4, 0x72, 0x12,
    WRITE_C8_D8, 0xBE, 0x00,
    WRITE_C8_D8, 0xDE, 0x02,

    WRITE_COMMAND_8, 0xE5,
    WRITE_BYTES, 3,
    0x00, 0x02, 0x00,

    WRITE_COMMAND_8, 0xE5,
    WRITE_BYTES, 3,
    0x01, 0x02, 0x00,

    WRITE_C8_D8, 0xDE, 0x00,
    WRITE_C8_D8, 0x35, 0x00,
    WRITE_C8_D8, 0x3A, 0x05,

    WRITE_COMMAND_8, 0x2A,
    WRITE_BYTES, 4,
    0x00, 0x22, 0x00, 0xCD,

    WRITE_COMMAND_8, 0x2B,
    WRITE_BYTES, 4,
    0x00, 0x00, 0x01, 0x3F,

    WRITE_C8_D8, 0xDE, 0x02,

    WRITE_COMMAND_8, 0xE5,
    WRITE_BYTES, 3,
    0x00, 0x02, 0x00,

    WRITE_C8_D8, 0xDE, 0x00,
    WRITE_C8_D8, 0x36, 0x00,
    WRITE_COMMAND_8, 0x21,
    END_WRITE,

    DELAY, 10,

    BEGIN_WRITE,
    WRITE_COMMAND_8, 0x29,
    END_WRITE
  };
  bus->batchOperation(init_operations, sizeof(init_operations));
}

String extractValue1FromPromResponse(const String &json) {
  int idx = json.indexOf("\"value\"");
  if (idx < 0) return "";
  int lb = json.indexOf('[', idx);
  if (lb < 0) return "";
  int comma = json.indexOf(',', lb);
  if (comma < 0) return "";
  int q1 = json.indexOf('"', comma);
  if (q1 < 0) return "";
  int q2 = json.indexOf('"', q1 + 1);
  if (q2 < 0) return "";
  return json.substring(q1 + 1, q2);
}

String formatPercent(const String &raw) {
  if (raw.length() == 0) return "NO";
  char buf[24];
  snprintf(buf, sizeof(buf), "%.1f%%", atof(raw.c_str()));
  return String(buf);
}

String formatBool(const String &raw) {
  if (raw.length() == 0) return "NO";
  return (atof(raw.c_str()) >= 0.5f) ? "UP" : "DOWN";
}

String formatRate(const String &raw) {
  if (raw.length() == 0) return "NO";
  float v = atof(raw.c_str());
  char buf[24];
  if (v < 1024.0f) {
    snprintf(buf, sizeof(buf), "%.0fB/s", v);
  } else if (v < 1024.0f * 1024.0f) {
    snprintf(buf, sizeof(buf), "%.1fKB/s", v / 1024.0f);
  } else {
    snprintf(buf, sizeof(buf), "%.1fMB/s", v / (1024.0f * 1024.0f));
  }
  return String(buf);
}

String metricDisplayValue(const Metric &m) {
  if (m.state == MS_FAIL && m.rawValue.length() == 0) return "NO";

  switch (m.kind) {
    case MK_PERCENT: return formatPercent(m.rawValue);
    case MK_BOOL:    return formatBool(m.rawValue);
    case MK_RATE:    return formatRate(m.rawValue);
    default:         return "NO";
  }
}

const char* stateText(MetricState st) {
  switch (st) {
    case MS_LIVE: return "LIVE";
    case MS_STALE: return "STALE";
    case MS_FAIL: return "FAIL";
    default: return "WAIT";
  }
}

uint16_t stateColor(MetricState st) {
  switch (st) {
    case MS_LIVE: return RGB565_GREEN;
    case MS_STALE: return RGB565_YELLOW;
    case MS_FAIL: return RGB565_RED;
    default: return RGB565_BLUE;
  }
}

uint32_t metricAgeSeconds(const Metric &m) {
  if (m.lastGoodMs == 0) return 0;
  return (millis() - m.lastGoodMs) / 1000;
}

MetricState summaryState() {
  MetricState s = MS_LIVE;
  for (int i = 0; i < 4; i++) {
    if (metrics[i].state == MS_FAIL) return MS_FAIL;
    if (metrics[i].state == MS_STALE) s = MS_STALE;
    if (metrics[i].state == MS_UNKNOWN && s == MS_LIVE) s = MS_UNKNOWN;
  }
  return s;
}

Metric& pageMetric() {
  if (currentPage == 1) return metrics[IDX_CPU];
  if (currentPage == 2) return metrics[IDX_MEM];
  if (currentPage == 3) return metrics[IDX_DISK];
  return metrics[IDX_CONN];
}

void applyFailedFetchState(Metric &m) {
  if (m.lastGoodMs == 0) {
    m.state = MS_FAIL;
    return;
  }

  uint32_t ageMs = millis() - m.lastGoodMs;
  if (ageMs >= STALE_TO_FAIL_MS) {
    m.state = MS_FAIL;
  } else {
    m.state = MS_STALE;
  }
}

void refreshMetricStatesFromAge() {
  for (int i = 0; i < METRIC_COUNT; i++) {
    Metric &m = metrics[i];
    if (m.state == MS_LIVE || m.state == MS_STALE) {
      if (m.lastGoodMs == 0) continue;

      uint32_t ageMs = millis() - m.lastGoodMs;
      if (ageMs >= STALE_TO_FAIL_MS) {
        m.state = MS_FAIL;
      } else if (m.state != MS_LIVE) {
        m.state = MS_STALE;
      }
    }
  }
}

void fetchOneMetricStep() {
  fetchMetric(metrics[fetchIndex]);
  fetchIndex = (fetchIndex + 1) % METRIC_COUNT;
}

void updateWifiState() {
  wifiConfigured = (strlen(WIFI_SSID) > 0);

  if (!wifiConfigured) {
    wifiStarted = false;
    wifiConnected = false;
    deviceIpText = "n/a";
    return;
  }

  wl_status_t st = WiFi.status();
  if (st == WL_CONNECTED) {
    wifiConnected = true;
    wifiStarted = true;
    deviceIpText = WiFi.localIP().toString();
    return;
  }

  wifiConnected = false;
  deviceIpText = "n/a";

  uint32_t now = millis();
  if (!wifiStarted || (now - lastWifiBeginAttempt >= WIFI_RETRY_MS)) {
    WiFi.disconnect();
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    wifiStarted = true;
    lastWifiBeginAttempt = now;
  }
}

void fetchMetric(Metric &m) {
  if (!wifiConnected) return;

  HTTPClient http;
  http.setTimeout(HTTP_TIMEOUT_MS);
  http.begin(m.url);

  int code = http.GET();
  m.httpCode = code;

  if (code > 0) {
    String body = http.getString();
    String value = extractValue1FromPromResponse(body);
    bool ok = (body.indexOf("\"status\":\"success\"") >= 0 || body.indexOf("\"status\": \"success\"") >= 0) &&
              (body.indexOf("\"resultType\":\"vector\"") >= 0 || body.indexOf("\"resultType\": \"vector\"") >= 0) &&
              (value.length() > 0);

    if (ok) {
      m.rawValue = value;
      m.state = MS_LIVE;
      m.lastGoodMs = millis();
    } else {
      applyFailedFetchState(m);
    }
  } else {
    applyFailedFetchState(m);
  }

  http.end();
}

void initTouch() {
  Wire.begin(TOUCH_SDA, TOUCH_SCL);
  bsp_touch_init(&Wire, TOUCH_RST, TOUCH_INT, ROTATION, SCREEN_W, SCREEN_H);
  touchReady = true;
}

void checkTouchNavigation() {
  if (!touchReady) return;

  bsp_touch_read();
  touch_data_t td = {};
  if (!bsp_touch_get_coordinates(&td)) return;

  if (millis() - lastTouchNavMs < 250) return;
  lastTouchNavMs = millis();

  uint16_t x = td.coords[0].x;

  if (x < 40) {
    currentPage = (currentPage == 0) ? 4 : currentPage - 1;
  } else if (x > 132) {
    currentPage = (currentPage + 1) % 5;
  } else {
    currentPage = 0;
  }

  lastRenderKey = "";
  drawCurrentPage();
}

void drawHeader(const String &title, const String &statusText, uint16_t statusColor) {
  gfx->fillRect(0, 0, SCREEN_W, 34, RGB565_BLUE);
  gfx->setTextColor(RGB565_WHITE);
  gfx->setTextSize(2);
  gfx->setCursor(8, 9);
  gfx->println(title);

  gfx->fillRect(0, 34, SCREEN_W, 24, statusColor);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(8, 42);
  gfx->println(statusText);
}

void drawFooter() {
  gfx->fillRect(0, 286, SCREEN_W, 34, RGB565_WHITE);
  gfx->drawFastHLine(0, 286, SCREEN_W, RGB565_BLACK);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);

  gfx->setCursor(6, 294);
  gfx->println("<");

  gfx->setCursor(16, 294);
  gfx->print("p");
  gfx->print(currentPage + 1);
  gfx->print("/5");

  uint32_t age = 0;
  if (currentPage == 0 || currentPage == 4) {
    age = metricAgeSeconds(metrics[IDX_CONN]);
  } else {
    age = metricAgeSeconds(pageMetric());
  }

  gfx->setCursor(62, 294);
  gfx->print("age ");
  gfx->print(age);
  gfx->print("s");

  gfx->setCursor(145, 294);
  gfx->println(">");
}

void drawMetricCard(int x, int y, int w, int h, const Metric &m) {
  gfx->fillRect(x, y, w, h, RGB565_WHITE);
  gfx->drawRect(x, y, w, h, RGB565_BLACK);

  gfx->fillRect(x + 4, y + 4, w - 8, 16, stateColor(m.state));
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(x + 8, y + 8);
  gfx->println(m.title);

  gfx->setTextColor(RGB565_BLACK);
  gfx->setCursor(x + 8, y + 28);
  gfx->println(metricDisplayValue(m));

  gfx->setCursor(x + 8, y + 44);
  gfx->println(stateText(m.state));
}

void drawOverviewPage() {
  MetricState s = summaryState();

  gfx->fillScreen(RGB565_WHITE);
  drawHeader("D-A OVER", String("SUMMARY ") + stateText(s), stateColor(s));

  drawMetricCard(8, 68, 74, 86, metrics[IDX_CPU]);
  drawMetricCard(90, 68, 74, 86, metrics[IDX_MEM]);
  drawMetricCard(8, 168, 74, 86, metrics[IDX_DISK]);
  drawMetricCard(90, 168, 74, 86, metrics[IDX_CONN]);

  drawFooter();
}

void drawDetailPage(const Metric &m) {
  gfx->fillScreen(RGB565_WHITE);
  drawHeader(String("D-A ") + m.title, String(m.title) + " " + stateText(m.state), stateColor(m.state));

  gfx->fillRect(8, 72, 156, 76, RGB565_WHITE);
  gfx->drawRect(8, 72, 156, 76, RGB565_BLACK);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(16, 82);
  gfx->println("VALUE");
  gfx->setTextSize(2);
  gfx->setCursor(16, 106);
  gfx->println(metricDisplayValue(m));

  gfx->setTextSize(1);
  gfx->fillRect(8, 160, 156, 30, stateColor(m.state));
  gfx->drawRect(8, 160, 156, 30, RGB565_BLACK);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setCursor(16, 171);
  gfx->println(stateText(m.state));

  gfx->fillRect(8, 198, 156, 24, RGB565_WHITE);
  gfx->drawRect(8, 198, 156, 24, RGB565_BLACK);
  gfx->setCursor(16, 206);
  gfx->print("HOST ");
  gfx->println(HOST_TEXT);

  gfx->fillRect(8, 230, 156, 24, RGB565_WHITE);
  gfx->drawRect(8, 230, 156, 24, RGB565_BLACK);
  gfx->setCursor(16, 238);
  gfx->print("AGE ");
  gfx->print(metricAgeSeconds(m));
  gfx->println("s");

  drawFooter();
}

void drawNetworkPage() {
  Metric &conn = metrics[IDX_CONN];

  gfx->fillScreen(RGB565_WHITE);
  drawHeader("D-A NET", String("NET ") + stateText(conn.state), stateColor(conn.state));

  drawMetricCard(8, 68, 156, 52, metrics[IDX_CONN]);
  drawMetricCard(8, 130, 156, 52, metrics[IDX_RX]);
  drawMetricCard(8, 192, 156, 52, metrics[IDX_TX]);

  drawFooter();
}

void drawCurrentPage() {
  if (currentPage == 0) {
    drawOverviewPage();
  } else if (currentPage == 4) {
    drawNetworkPage();
  } else {
    drawDetailPage(pageMetric());
  }
}

String renderKey() {
  String k;
  k += String(currentPage) + "|";
  k += wifiConfigured ? "1" : "0"; k += "|";
  k += wifiStarted ? "1" : "0"; k += "|";
  k += wifiConnected ? "1" : "0"; k += "|";
  k += deviceIpText; k += "|";
  for (int i = 0; i < METRIC_COUNT; i++) {
    k += String((int)metrics[i].state); k += "|";
    k += String(metrics[i].httpCode); k += "|";
    k += metrics[i].rawValue; k += "|";
  }
  return k;
}

void redrawIfChanged() {
  String k = renderKey();
  if (k != lastRenderKey) {
    lastRenderKey = k;
    drawCurrentPage();
  }
}

void setup() {
  Serial.begin(115200);
  unsigned long serialWaitStart = millis();
  while (!Serial && (millis() - serialWaitStart < 3000)) {
    delay(10);
  }
  Serial.println("SERIAL_ATTACHED");
  delay(300);
  Serial.println();
  Serial.println("DESIGN_A_V1_BOOT");

  pinMode(GFX_BL, OUTPUT);
  digitalWrite(GFX_BL, HIGH);

  if (!gfx->begin()) {
    Serial.println("LCD_BEGIN_FAILED");
    while (true) delay(1000);
  }

  lcd_reg_init();
  gfx->setRotation(ROTATION);

  initTouch();
  updateWifiState();
  drawCurrentPage();
  Serial.println("DESIGN_A_V1_SAFE_START");
}

void loop() {
  uint32_t now = millis();

  checkTouchNavigation();

  if (now - lastWifiPoll >= 1000) {
    lastWifiPoll = now;
    updateWifiState();
    refreshMetricStatesFromAge();
    redrawIfChanged();
  }

  if (wifiConnected && (lastFetchSweep == 0 || (now - lastFetchSweep >= FETCH_STEP_MS))) {
    lastFetchSweep = now;
    fetchOneMetricStep();
    redrawIfChanged();
  }

  if (now - lastTick >= 1000) {
    lastTick = now;
    tickCounter++;
    drawFooter();

    Serial.print("tick=");
    Serial.print(tickCounter);
    Serial.print(" page=");
    Serial.print(currentPage + 1);
    Serial.print(" wifi=");
    Serial.print(wifiConnected ? "UP" : "DOWN");
    Serial.print(" cpu=");
    Serial.print(metricDisplayValue(metrics[IDX_CPU]));
    Serial.print("/");
    Serial.print(stateText(metrics[IDX_CPU].state));
    Serial.print(" mem=");
    Serial.print(metricDisplayValue(metrics[IDX_MEM]));
    Serial.print("/");
    Serial.print(stateText(metrics[IDX_MEM].state));
    Serial.print(" disk=");
    Serial.print(metricDisplayValue(metrics[IDX_DISK]));
    Serial.print("/");
    Serial.print(stateText(metrics[IDX_DISK].state));
    Serial.print(" net=");
    Serial.print(metricDisplayValue(metrics[IDX_CONN]));
    Serial.print("/");
    Serial.print(stateText(metrics[IDX_CONN].state));
    Serial.println();
  }
}

