#include <Arduino_GFX_Library.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>

#define GFX_BL 23
#define ROTATION 0

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

static const char CPU_JSON[]  = R"JSON({"status":"success","data":{"resultType":"vector","result":[{"metric":{},"value":[1774888378.850,"0.24930475813034986"]}]}})JSON";
static const char MEM_JSON[]  = R"JSON({"status":"success","data":{"resultType":"vector","result":[{"metric":{"instance":"node-exporter:9100","job":"node_exporter"},"value":[1774888378.858,"7.113857518846956"]}]}})JSON";
static const char DISK_JSON[] = R"JSON({"status":"success","data":{"resultType":"vector","result":[{"metric":{"device":"/dev/sdf","fstype":"ext4","instance":"node-exporter:9100","job":"node_exporter","mountpoint":"/etc/hosts"},"value":[1774888378.864,"6.488473697675068"]}]}})JSON";
static const char CONN_JSON[] = R"JSON({"status":"success","data":{"resultType":"vector","result":[{"metric":{"__name__":"up","instance":"node-exporter:9100","job":"node_exporter"},"value":[1774888378.883,"1"]}]}})JSON";

static const char EMPTY_JSON[] =
R"JSON({
  "status":"success",
  "data":{"resultType":"vector","result":[]}
})JSON";

static const char FAIL_JSON[] =
R"JSON({
  "status":"error",
  "data":{"resultType":"vector","result":[]}
})JSON";

struct ParseResult {
  bool statusSuccess;
  bool resultTypeVector;
  bool emptyResult;
  bool hasValue;
  String valueText;
  String instance;
  String job;
  String device;
  String mountpoint;
};

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

String findLabelValue(const String &json, const char *label) {
  String key = "\"" + String(label) + "\"";
  int keyPos = json.indexOf(key);
  if (keyPos < 0) return "";
  int colon = json.indexOf(':', keyPos);
  if (colon < 0) return "";
  int q1 = json.indexOf('"', colon + 1);
  if (q1 < 0) return "";
  int q2 = json.indexOf('"', q1 + 1);
  if (q2 < 0) return "";
  return json.substring(q1 + 1, q2);
}

bool hasSuccessStatus(const String &json) {
  return json.indexOf("\"status\": \"success\"") >= 0 || json.indexOf("\"status\":\"success\"") >= 0;
}

bool hasVectorResultType(const String &json) {
  return json.indexOf("\"resultType\": \"vector\"") >= 0 || json.indexOf("\"resultType\":\"vector\"") >= 0;
}

bool resultArrayEmpty(const String &json) {
  int idx = json.indexOf("\"result\"");
  if (idx < 0) return true;
  int lb = json.indexOf('[', idx);
  if (lb < 0) return true;
  int i = lb + 1;
  while (i < json.length() && isspace((unsigned char)json[i])) i++;
  return (i < json.length() && json[i] == ']');
}

String extractValue1(const String &json) {
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

ParseResult parsePromFixture(const String &json) {
  ParseResult r;
  r.statusSuccess = hasSuccessStatus(json);
  r.resultTypeVector = hasVectorResultType(json);
  r.emptyResult = resultArrayEmpty(json);
  r.valueText = "";
  r.instance = findLabelValue(json, "instance");
  r.job = findLabelValue(json, "job");
  r.device = findLabelValue(json, "device");
  r.mountpoint = findLabelValue(json, "mountpoint");

  if (!r.emptyResult) {
    r.valueText = extractValue1(json);
    r.hasValue = r.valueText.length() > 0;
  } else {
    r.hasValue = false;
  }
  return r;
}

String formatPercent(const String &raw) {
  char buf[24];
  float v = atof(raw.c_str());
  snprintf(buf, sizeof(buf), "%.1f%%", v);
  return String(buf);
}

String formatConnectivity(const String &raw) {
  float v = atof(raw.c_str());
  return (v >= 0.5f) ? String("UP") : String("DOWN");
}

void drawSlot(int x, int y, const char *label, const String &value, uint16_t color) {
  gfx->fillRect(x, y, 74, 54, RGB565_WHITE);
  gfx->drawRect(x, y, 74, 54, RGB565_BLACK);

  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(x + 6, y + 7);
  gfx->println(label);

  gfx->fillRect(x + 4, y + 20, 66, 24, color);
  gfx->setTextColor(RGB565_WHITE);
  gfx->setTextSize(1);
  gfx->setCursor(x + 8, y + 28);
  gfx->println(value);
}

void drawHeader(const String &statusText) {
  gfx->fillRect(0, 0, 172, 34, RGB565_BLUE);
  gfx->setTextColor(RGB565_WHITE);
  gfx->setTextSize(2);
  gfx->setCursor(8, 9);
  gfx->println("FIXTURES");

  gfx->fillRect(0, 34, 172, 24, RGB565_GREEN);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(8, 42);
  gfx->println(statusText);
}

void drawFooter(uint32_t tick, const String &jobText) {
  gfx->fillRect(0, 286, 172, 34, RGB565_WHITE);
  gfx->drawFastHLine(0, 286, 172, RGB565_BLACK);

  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(8, 294);
  gfx->print("tick=");
  gfx->println(tick);

  gfx->setCursor(68, 294);
  gfx->print("job=");
  gfx->println(jobText);
}

ParseResult cpuRes, memRes, diskRes, connRes;
bool parserOk = false;
uint32_t tickCounter = 0;

void drawFixtureOverview() {
  String cpuText  = cpuRes.hasValue  ? formatPercent(cpuRes.valueText)   : String("MISS");
  String memText  = memRes.hasValue  ? formatPercent(memRes.valueText)   : String("MISS");
  String diskText = diskRes.hasValue ? formatPercent(diskRes.valueText)  : String("MISS");
  String netText  = connRes.hasValue ? formatConnectivity(connRes.valueText) : String("MISS");
  String dataText = String("FIXTURE");
  String parseText = parserOk ? String("OK") : String("ERR");

  gfx->fillScreen(RGB565_WHITE);
  drawHeader(parserOk ? String("PARSER OK / REAL FIXTURES") : String("PARSER ERROR"));

  drawSlot(8, 68,  "CPU",  cpuText,  RGB565_BLUE);
  drawSlot(90, 68, "MEM",  memText,  RGB565_BLUE);
  drawSlot(8, 130, "DISK", diskText, RGB565_BLUE);
  drawSlot(90, 130,"NET",  netText,  (netText == "UP") ? RGB565_GREEN : RGB565_RED);
  drawSlot(8, 192, "DATA", dataText, RGB565_GREEN);
  drawSlot(90, 192,"PARSE",parseText, parserOk ? RGB565_GREEN : RGB565_RED);

  drawFooter(tickCounter, connRes.job.length() ? connRes.job : String("n/a"));
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println();
  Serial.println("FIXTURE_PARSER_START");

  pinMode(GFX_BL, OUTPUT);
  digitalWrite(GFX_BL, HIGH);
  Serial.println("BACKLIGHT_HIGH");

  if (!gfx->begin()) {
    Serial.println("LCD_BEGIN_FAILED");
    while (true) delay(1000);
  }
  Serial.println("LCD_BEGIN_OK");

  lcd_reg_init();
  Serial.println("LCD_REG_INIT_OK");

  gfx->setRotation(ROTATION);

  cpuRes  = parsePromFixture(String(CPU_JSON));
  memRes  = parsePromFixture(String(MEM_JSON));
  diskRes = parsePromFixture(String(DISK_JSON));
  connRes = parsePromFixture(String(CONN_JSON));

  ParseResult emptyRes = parsePromFixture(String(EMPTY_JSON));
  ParseResult failRes  = parsePromFixture(String(FAIL_JSON));

  parserOk =
    cpuRes.statusSuccess && cpuRes.resultTypeVector && cpuRes.hasValue &&
    memRes.statusSuccess && memRes.resultTypeVector && memRes.hasValue &&
    diskRes.statusSuccess && diskRes.resultTypeVector && diskRes.hasValue &&
    connRes.statusSuccess && connRes.resultTypeVector && connRes.hasValue &&
    emptyRes.statusSuccess && emptyRes.resultTypeVector && emptyRes.emptyResult &&
    (!failRes.statusSuccess);

  drawFixtureOverview();

  Serial.print("CPU_VALUE=");
  Serial.println(cpuRes.valueText);
  Serial.print("MEM_VALUE=");
  Serial.println(memRes.valueText);
  Serial.print("DISK_VALUE=");
  Serial.println(diskRes.valueText);
  Serial.print("CONN_VALUE=");
  Serial.println(connRes.valueText);
  Serial.print("PARSER_OK=");
  Serial.println(parserOk ? "YES" : "NO");
}

void loop() {
  static uint32_t last = 0;
  if (millis() - last >= 1000) {
    last = millis();
    tickCounter++;
    drawFooter(tickCounter, connRes.job.length() ? connRes.job : String("n/a"));
    Serial.print("tick=");
    Serial.println(tickCounter);
  }
}
