#include <Arduino_GFX_Library.h>

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

struct Slot {
  const char *label;
  const char *value;
  uint16_t color;
};

Slot slots[] = {
  {"CPU",  "24%",      RGB565_BLUE},
  {"MEM",  "61%",      RGB565_BLUE},
  {"DISK", "42%",      RGB565_BLUE},
  {"NET",  "UP",       RGB565_GREEN},
  {"DATA", "LIVE",     RGB565_GREEN},
  {"MODE", "DESIGN A", RGB565_BLUE}
};

uint32_t tickCounter = 0;

void drawHeader() {
  gfx->fillRect(0, 0, 172, 34, RGB565_BLUE);
  gfx->setTextColor(RGB565_WHITE);
  gfx->setTextSize(2);
  gfx->setCursor(10, 10);
  gfx->println("OVERVIEW");
}

void drawStatusBar() {
  gfx->fillRect(0, 34, 172, 24, RGB565_GREEN);
  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(8, 42);
  gfx->println("STATUS: OK   DUMMY VALUES");
}

void drawSlot(int x, int y, const struct Slot &s) {
  gfx->fillRect(x, y, 74, 54, RGB565_WHITE);
  gfx->drawRect(x, y, 74, 54, RGB565_BLACK);

  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(x + 6, y + 7);
  gfx->println(s.label);

  gfx->fillRect(x + 4, y + 20, 66, 24, s.color);
  gfx->setTextColor(RGB565_WHITE);
  gfx->setTextSize(1);
  gfx->setCursor(x + 8, y + 28);
  gfx->println(s.value);
}

void drawFooter(uint32_t tick) {
  gfx->fillRect(0, 286, 172, 34, RGB565_WHITE);
  gfx->drawFastHLine(0, 286, 172, RGB565_BLACK);

  gfx->setTextColor(RGB565_BLACK);
  gfx->setTextSize(1);
  gfx->setCursor(8, 295);
  gfx->print("tick=");
  gfx->println(tick);

  gfx->setCursor(70, 295);
  gfx->println("STATE=RUN");
}

void drawOverview(uint32_t tick) {
  gfx->fillScreen(RGB565_WHITE);
  drawHeader();
  drawStatusBar();

  drawSlot(8, 68,  slots[0]);
  drawSlot(90, 68, slots[1]);
  drawSlot(8, 130, slots[2]);
  drawSlot(90, 130, slots[3]);
  drawSlot(8, 192, slots[4]);
  drawSlot(90, 192, slots[5]);

  drawFooter(tick);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println();
  Serial.println("DUMMY_OVERVIEW_START");

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
  drawOverview(tickCounter);
  Serial.println("DUMMY_OVERVIEW_DRAWN");
}

void loop() {
  static uint32_t last = 0;

  if (millis() - last >= 1000) {
    last = millis();
    tickCounter++;
    drawFooter(tickCounter);
    Serial.print("tick=");
    Serial.println(tickCounter);
  }
}
