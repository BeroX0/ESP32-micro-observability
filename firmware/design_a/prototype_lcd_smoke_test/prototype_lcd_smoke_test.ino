#include <Arduino_GFX_Library.h>

// =========================
// Board / panel config
// =========================
namespace BoardConfig {
  constexpr uint8_t PIN_LCD_DC   = 15;
  constexpr uint8_t PIN_LCD_CS   = 14;
  constexpr uint8_t PIN_LCD_SCK  = 1;
  constexpr uint8_t PIN_LCD_MOSI = 2;
  constexpr uint8_t PIN_LCD_RST  = 22;
  constexpr uint8_t PIN_LCD_BL   = 23;

  constexpr uint16_t LCD_WIDTH   = 172;
  constexpr uint16_t LCD_HEIGHT  = 320;
  constexpr uint8_t  ROTATION    = 0;

  constexpr uint16_t COL_OFFSET1 = 34;
  constexpr uint16_t ROW_OFFSET1 = 0;
  constexpr uint16_t COL_OFFSET2 = 34;
  constexpr uint16_t ROW_OFFSET2 = 0;

  constexpr uint32_t SERIAL_BAUD = 115200;
}

// =========================
// Display objects
// =========================
Arduino_DataBus* bus = new Arduino_HWSPI(
  BoardConfig::PIN_LCD_DC,
  BoardConfig::PIN_LCD_CS,
  BoardConfig::PIN_LCD_SCK,
  BoardConfig::PIN_LCD_MOSI
);

Arduino_GFX* gfx = new Arduino_ST7789(
  bus,
  BoardConfig::PIN_LCD_RST,
  BoardConfig::ROTATION,
  false,
  BoardConfig::LCD_WIDTH,
  BoardConfig::LCD_HEIGHT,
  BoardConfig::COL_OFFSET1,
  BoardConfig::ROW_OFFSET1,
  BoardConfig::COL_OFFSET2,
  BoardConfig::ROW_OFFSET2
);

// =========================
// Panel init sequence
// =========================
static const uint8_t PANEL_INIT_OPS[] = {
  BEGIN_WRITE,
  WRITE_COMMAND_8, 0x11,
  END_WRITE,
  DELAY, 120,

  BEGIN_WRITE,
  WRITE_C8_D16, 0xDF, 0x98, 0x53,
  WRITE_C8_D8,  0xB2, 0x23,

  WRITE_COMMAND_8, 0xB7,
  WRITE_BYTES, 4,
  0x00, 0x47, 0x00, 0x6F,

  WRITE_COMMAND_8, 0xBB,
  WRITE_BYTES, 6,
  0x1C, 0x1A, 0x55, 0x73, 0x63, 0xF0,

  WRITE_C8_D16, 0xC0, 0x44, 0xA4,
  WRITE_C8_D8,  0xC1, 0x16,

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
  WRITE_C8_D8,  0xE6, 0x14,
  WRITE_C8_D8,  0xDE, 0x01,

  WRITE_COMMAND_8, 0xB7,
  WRITE_BYTES, 5,
  0x03, 0x13, 0xEF, 0x35, 0x35,

  WRITE_COMMAND_8, 0xC1,
  WRITE_BYTES, 3,
  0x14, 0x15, 0xC0,

  WRITE_C8_D16, 0xC2, 0x06, 0x3A,
  WRITE_C8_D16, 0xC4, 0x72, 0x12,
  WRITE_C8_D8,  0xBE, 0x00,
  WRITE_C8_D8,  0xDE, 0x02,

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

// =========================
// Helpers
// =========================
void initBacklight() {
  pinMode(BoardConfig::PIN_LCD_BL, OUTPUT);
  digitalWrite(BoardConfig::PIN_LCD_BL, HIGH);
}

void initPanelRegisters() {
  bus->batchOperation(PANEL_INIT_OPS, sizeof(PANEL_INIT_OPS));
}

void drawColorBars() {
  const int barH = BoardConfig::LCD_HEIGHT / 4;
  gfx->fillRect(0, 0, BoardConfig::LCD_WIDTH, barH, RGB565_RED);
  gfx->fillRect(0, barH, BoardConfig::LCD_WIDTH, barH, RGB565_GREEN);
  gfx->fillRect(0, barH * 2, BoardConfig::LCD_WIDTH, barH, RGB565_BLUE);
  gfx->fillRect(0, barH * 3, BoardConfig::LCD_WIDTH, BoardConfig::LCD_HEIGHT - (barH * 3), RGB565_WHITE);
}

void drawFrame() {
  gfx->drawRect(0, 0, BoardConfig::LCD_WIDTH, BoardConfig::LCD_HEIGHT, RGB565_BLACK);
  gfx->drawRect(1, 1, BoardConfig::LCD_WIDTH - 2, BoardConfig::LCD_HEIGHT - 2, RGB565_BLACK);
}

void drawHelloScreen() {
  gfx->fillScreen(RGB565_WHITE);
  drawFrame();

  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(2);

  gfx->setCursor(12, 24);
  gfx->println(F("HELLO"));

  gfx->setCursor(12, 58);
  gfx->println(F("FROM OUR"));

  gfx->setCursor(12, 92);
  gfx->println(F("CODE"));

  gfx->drawLine(12, 128, 160, 128, RGB565_BLUE);

  gfx->setCursor(12, 146);
  gfx->setTextColor(RGB565_BLUE);
  gfx->println(F("ESP32-C6"));

  gfx->setCursor(12, 180);
  gfx->println(F("LCD TEST"));
}

void drawCounter(uint32_t count) {
  gfx->fillRect(12, 230, 148, 42, RGB565_WHITE);
  gfx->drawRect(12, 230, 148, 42, RGB565_BLACK);

  gfx->setCursor(20, 242);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(2);
  gfx->print(F("tick="));
  gfx->println(count);
}

// =========================
// Arduino entry points
// =========================
void setup() {
  Serial.begin(BoardConfig::SERIAL_BAUD);
  delay(1000);

  Serial.println();
  Serial.println(F("OUR_LCD_TEST_START"));

  initBacklight();
  Serial.println(F("BACKLIGHT_HIGH"));

  if (!gfx->begin()) {
    Serial.println(F("LCD_BEGIN_FAILED"));
    while (true) {
      delay(1000);
    }
  }
  Serial.println(F("LCD_BEGIN_OK"));

  initPanelRegisters();
  Serial.println(F("LCD_REG_INIT_OK"));

  gfx->setRotation(BoardConfig::ROTATION);

  drawColorBars();
  Serial.println(F("COLOR_BARS_DRAWN"));
  delay(1200);

  drawHelloScreen();
  Serial.println(F("HELLO_SCREEN_DRAWN"));

  drawCounter(0);
  Serial.println(F("COUNTER_DRAWN"));
}

void loop() {
  static uint32_t last = 0;
  static uint32_t tick = 1;

  if (millis() - last >= 1000) {
    last = millis();
    drawCounter(tick);
    Serial.print(F("tick="));
    Serial.println(tick);
    tick++;
  }
}
