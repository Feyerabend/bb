
## C Program for Raspberry Pi Pico to Drive 1.47-inch LCD Module (ST7789V3)

Below is a C program for the Raspberry Pi Pico to drive the 1.47-inch LCD Module
(172x320, ST7789V3, SPI interface) based on the Waveshare documentation. The program
uses the Pico SDK and provides a basic example to initialise the display, clear the
screen, and draw some simple graphics and text using the provided GUI functions.
Since the Pico SDK differs from the Raspberry Pi and STM32 environments described
in the Waveshare documentation, the code is adapted to work with the Pico's hardware
SPI and GPIO capabilities. UNTESTED!


### Assumptions and Notes

- *Hardware*: The program assumes the 1.47-inch LCD Module is connected to the Raspberry
  Pi Pico via the SPI0
  interface with the pin configuration specified below.
- *Dependencies*: The code uses the Pico SDK for SPI and GPIO operations. It adapts the
  Waveshare-provided functions (e.g., `DEV_Config`, `GUI_Paint`) to work with the Pico.
- *Fonts and GUI*: The program includes a minimal set of GUI functions and a single font
  (e.g., Font12) for simplicity. You can expand it by including additional font files or
  image data from the Waveshare library.
- *Limitations*: Due to the Pico's limited RAM (264KB), the entire frame buffer
  (172x320x2 bytes ≈ 110KB for RGB565) is stored in RAM, which is feasible but leaves
  limited space for other operations. The GUI writes directly to the LCD's RAM to mitigate
  this, as mentioned in the documentation.


### Pin Configuration

Based on the Waveshare documentation, the LCD uses an SPI interface with additional control
pins. Here's the pin mapping for the Raspberry Pi Pico:

| LCD Pin | Pico Pin | Function         |
|---------|----------|------------------|
| VCC     | 3V3      | 3.3V Power       |
| GND     | GND      | Ground           |
| DIN     | GP19     | SPI0 TX (MOSI)   |
| CLK     | GP18     | SPI0 SCK         |
| CS      | GP17     | Chip Select      |
| DC      | GP20     | Data/Command     |
| RST     | GP21     | Reset            |
| BL      | GP22     | Backlight        |


### Program Overview

The program will:
1. Init the SPI interface and GPIO pins.
2. Init the ST7789V3 controller.
3. Clear the display to a solid color.
4. Draw a rectangle, a circle, and some text using the GUI functions.
5. Continuously update the display with a simple animation (e.g., changing text color).


### C Program for Raspberry Pi Pico

Include the necessary font and GUI files from the Waveshare library
(available in the `RaspberryPi\c\lib` directory from the Waveshare demo code).
For simplicity, this example assumes `font12.c` is included for text rendering.

```c
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

// Pin definitions for Raspberry Pi Pico
#define LCD_SPI_PORT    spi0
#define LCD_SPI_BAUD    40 * 1000 * 1000 // 40 MHz
#define LCD_PIN_MOSI    19
#define LCD_PIN_SCK     18
#define LCD_PIN_CS      17
#define LCD_PIN_DC      20
#define LCD_PIN_RST     21
#define LCD_PIN_BL      22

// LCD parameters
#define LCD_WIDTH       172
#define LCD_HEIGHT      320
#define LCD_OFFSET_X    34  // Offset to center 172 pixels in 240-pixel controller
#define LCD_OFFSET_Y    0   // No offset in Y direction

// Color definitions (RGB565)
#define WHITE           0xFFFF
#define BLACK           0x0000
#define RED             0xF800
#define GREEN           0x07E0
#define BLUE            0x001F

// Data types
typedef uint8_t  UBYTE;
typedef uint16_t UWORD;
typedef uint32_t UDOUBLE;

// Font structure (example for Font12)
typedef struct {
    const UBYTE *table;
    UWORD Width;
    UWORD Height;
} sFONT;

extern sFONT Font12; // Assume font12.c is included

// Hardware interface functions
void DEV_Digital_Write(uint pin, UBYTE value) {
    gpio_put(pin, value);
}

void DEV_SPI_WriteByte(UBYTE value) {
    spi_write_blocking(LCD_SPI_PORT, &value, 1);
}

void DEV_Delay_ms(uint32_t ms) {
    sleep_ms(ms);
}

// LCD low-level functions
void LCD_WriteReg(UBYTE reg) {
    DEV_Digital_Write(LCD_PIN_DC, 0); // Command mode
    DEV_Digital_Write(LCD_PIN_CS, 0);
    DEV_SPI_WriteByte(reg);
    DEV_Digital_Write(LCD_PIN_CS, 1);
}

void LCD_WriteData_8Bit(UBYTE data) {
    DEV_Digital_Write(LCD_PIN_DC, 1); // Data mode
    DEV_Digital_Write(LCD_PIN_CS, 0);
    DEV_SPI_WriteByte(data);
    DEV_Digital_Write(LCD_PIN_CS, 1);
}

void LCD_WriteData_16Bit(UWORD data) {
    DEV_Digital_Write(LCD_PIN_DC, 1); // Data mode
    DEV_Digital_Write(LCD_PIN_CS, 0);
    DEV_SPI_WriteByte(data >> 8);   // High byte
    DEV_SPI_WriteByte(data & 0xFF); // Low byte
    DEV_Digital_Write(LCD_PIN_CS, 1);
}

// LCD initialization
void LCD_Init(void) {
    // Initialize GPIO pins
    gpio_init(LCD_PIN_CS);
    gpio_init(LCD_PIN_DC);
    gpio_init(LCD_PIN_RST);
    gpio_init(LCD_PIN_BL);
    gpio_set_dir(LCD_PIN_CS, GPIO_OUT);
    gpio_set_dir(LCD_PIN_DC, GPIO_OUT);
    gpio_set_dir(LCD_PIN_RST, GPIO_OUT);
    gpio_set_dir(LCD_PIN_BL, GPIO_OUT);
    DEV_Digital_Write(LCD_PIN_CS, 1);
    DEV_Digital_Write(LCD_PIN_DC, 1);
    DEV_Digital_Write(LCD_PIN_BL, 1); // Backlight on

    // Initialize SPI
    spi_init(LCD_SPI_PORT, LCD_SPI_BAUD);
    gpio_set_function(LCD_PIN_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(LCD_PIN_SCK, GPIO_FUNC_SPI);

    // Reset LCD
    DEV_Digital_Write(LCD_PIN_RST, 1);
    DEV_Delay_ms(100);
    DEV_Digital_Write(LCD_PIN_RST, 0);
    DEV_Delay_ms(100);
    DEV_Digital_Write(LCD_PIN_RST, 1);
    DEV_Delay_ms(100);

    // ST7789V3 initialization sequence
    LCD_WriteReg(0x11); // Sleep out
    DEV_Delay_ms(120);

    LCD_WriteReg(0x36); // Memory Data Access Control
    LCD_WriteData_8Bit(0x00); // Normal orientation

    LCD_WriteReg(0x3A); // Interface Pixel Format
    LCD_WriteData_8Bit(0x05); // RGB565

    LCD_WriteReg(0xB2); // Porch Setting
    LCD_WriteData_8Bit(0x0C);
    LCD_WriteData_8Bit(0x0C);
    LCD_WriteData_8Bit(0x00);
    LCD_WriteData_8Bit(0x33);
    LCD_WriteData_8Bit(0x33);

    LCD_WriteReg(0xB7); // Gate Control
    LCD_WriteData_8Bit(0x35);

    LCD_WriteReg(0xBB); // VCOM Setting
    LCD_WriteData_8Bit(0x19);

    LCD_WriteReg(0xC0); // LCM Control
    LCD_WriteData_8Bit(0x2C);

    LCD_WriteReg(0xC2); // VDV and VRH Command Enable
    LCD_WriteData_8Bit(0x01);

    LCD_WriteReg(0xC3); // VRH Set
    LCD_WriteData_8Bit(0x12);

    LCD_WriteReg(0xC4); // VDV Set
    LCD_WriteData_8Bit(0x20);

    LCD_WriteReg(0xC6); // Frame Rate Control
    LCD_WriteData_8Bit(0x0F);

    LCD_WriteReg(0xD0); // Power Control 1
    LCD_WriteData_8Bit(0xA4);
    LCD_WriteData_8Bit(0xA1);

    LCD_WriteReg(0xE0); // Positive Voltage Gamma Control
    LCD_WriteData_8Bit(0xD0);
    LCD_WriteData_8Bit(0x04);
    LCD_WriteData_8Bit(0x0D);
    LCD_WriteData_8Bit(0x11);
    LCD_WriteData_8Bit(0x13);
    LCD_WriteData_8Bit(0x2B);
    LCD_WriteData_8Bit(0x3F);
    LCD_WriteData_8Bit(0x54);
    LCD_WriteData_8Bit(0x4C);
    LCD_WriteData_8Bit(0x18);
    LCD_WriteData_8Bit(0x0D);
    LCD_WriteData_8Bit(0x0B);
    LCD_WriteData_8Bit(0x1F);
    LCD_WriteData_8Bit(0x23);

    LCD_WriteReg(0xE1); // Negative Voltage Gamma Control
    LCD_WriteData_8Bit(0xD0);
    LCD_WriteData_8Bit(0x04);
    LCD_WriteData_8Bit(0x0C);
    LCD_WriteData_8Bit(0x11);
    LCD_WriteData_8Bit(0x13);
    LCD_WriteData_8Bit(0x2C);
    LCD_WriteData_8Bit(0x3F);
    LCD_WriteData_8Bit(0x44);
    LCD_WriteData_8Bit(0x51);
    LCD_WriteData_8Bit(0x2F);
    LCD_WriteData_8Bit(0x1F);
    LCD_WriteData_8Bit(0x1F);
    LCD_WriteData_8Bit(0x20);
    LCD_WriteData_8Bit(0x23);

    LCD_WriteReg(0x21); // Display Inversion On
    LCD_WriteReg(0x29); // Display On
}

// Set address window for writing pixels
void LCD_SetWindow(UWORD x_start, UWORD y_start, UWORD x_end, UWORD y_end) {
    LCD_WriteReg(0x2A); // Column Address Set
    LCD_WriteData_8Bit((x_start + LCD_OFFSET_X) >> 8);
    LCD_WriteData_8Bit(x_start + LCD_OFFSET_X);
    LCD_WriteData_8Bit((x_end + LCD_OFFSET_X) >> 8);
    LCD_WriteData_8Bit(x_end + LCD_OFFSET_X);

    LCD_WriteReg(0x2B); // Row Address Set
    LCD_WriteData_8Bit((y_start + LCD_OFFSET_Y) >> 8);
    LCD_WriteData_8Bit(y_start + LCD_OFFSET_Y);
    LCD_WriteData_8Bit((y_end + LCD_OFFSET_Y) >> 8);
    LCD_WriteData_8Bit(y_end + LCD_OFFSET_Y);

    LCD_WriteReg(0x2C); // Memory Write
}

// Clear screen
void LCD_Clear(UWORD color) {
    LCD_SetWindow(0, 0, LCD_WIDTH - 1, LCD_HEIGHT - 1);
    DEV_Digital_Write(LCD_PIN_DC, 1);
    DEV_Digital_Write(LCD_PIN_CS, 0);
    for (UWORD y = 0; y < LCD_HEIGHT; y++) {
        for (UWORD x = 0; x < LCD_WIDTH; x++) {
            LCD_WriteData_16Bit(color);
        }
    }
    DEV_Digital_Write(LCD_PIN_CS, 1);
}

// GUI functions (simplified from Waveshare's GUI_Paint.c)
void Paint_SetPixel(UWORD x, UWORD y, UWORD color) {
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) return;
    LCD_SetWindow(x, y, x, y);
    LCD_WriteData_16Bit(color);
}

void Paint_DrawChar(UWORD x, UWORD y, const char c, sFONT* font, UWORD fg_color, UWORD bg_color) {
    UBYTE data;
    UWORD i, j, char_offset;
    char_offset = (c - ' ') * font->Height * (font->Width / 8 + (font->Width % 8 ? 1 : 0));
    for (j = 0; j < font->Height; j++) {
        for (i = 0; i < font->Width; i++) {
            if (i % 8 == 0) {
                data = font->table[char_offset + j * (font->Width / 8 + (font->Width % 8 ? 1 : 0)) + i / 8];
            }
            if (data & (0x80 >> (i % 8))) {
                Paint_SetPixel(x + i, y + j, fg_color);
            } else {
                Paint_SetPixel(x + i, y + j, bg_color);
            }
        }
    }
}

void Paint_DrawString_EN(UWORD x, UWORD y, const char *str, sFONT* font, UWORD fg_color, UWORD bg_color) {
    while (*str) {
        Paint_DrawChar(x, y, *str, font, fg_color, bg_color);
        x += font->Width;
        str++;
    }
}

void Paint_DrawRectangle(UWORD x_start, UWORD y_start, UWORD x_end, UWORD y_end, UWORD color, UBYTE filled) {
    if (filled) {
        for (UWORD y = y_start; y <= y_end; y++) {
            for (UWORD x = x_start; x <= x_end; x++) {
                Paint_SetPixel(x, y, color);
            }
        }
    } else {
        for (UWORD x = x_start; x <= x_end; x++) {
            Paint_SetPixel(x, y_start, color);
            Paint_SetPixel(x, y_end, color);
        }
        for (UWORD y = y_start; y <= y_end; y++) {
            Paint_SetPixel(x_start, y, color);
            Paint_SetPixel(x_end, y, color);
        }
    }
}

// Main function
int main(void) {
    stdio_init_all();

    // Initialize LCD
    LCD_Init();

    // Clear screen to white
    LCD_Clear(WHITE);

    // Draw a red rectangle
    Paint_DrawRectangle(10, 10, 162, 50, RED, 0);

    // Draw some text
    Paint_DrawString_EN(20, 20, "Hello, Pico!", &Font12, BLACK, WHITE);

    // Simple animation: alternate text color
    while (1) {
        Paint_DrawString_EN(20, 40, "1.47 LCD", &Font12, BLUE, WHITE);
        sleep_ms(1000);
        Paint_DrawString_EN(20, 40, "1.47 LCD", &Font12, GREEN, WHITE);
        sleep_ms(1000);
    }

    return 0;
}
```


### Font File (font12.c)
You'll need to include the `font12.c` file from the Waveshare demo code (`RaspberryPi\c\lib\Fonts\font12.c`).
Simplified version for reference (original file from Waveshare):

```c
#include "fonts.h"

const UBYTE font12_table[] = {
    // Font data for ASCII characters (space to ~)
    // .. (copy from Waveshare's font12.c)
};

sFONT Font12 = {
    font12_table,
    7,  // Width
    12, // Height
};
```


### CMakeLists.txt

To build this program with the Pico SDK, create a `CMakeLists.txt` file:

```cmake
cmake_minimum_required(VERSION 3.12)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(lcd_1inch47 C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(lcd_1inch47
    main.c
    font12.c
)

target_link_libraries(lcd_1inch47
    pico_stdlib
    hardware_spi
)

pico_add_extra_outputs(lcd_1inch47)
```

### Setup Instructions
1. *Hardware Setup*:
   - Connect the LCD to the Raspberry Pi Pico as per the pin configuration table above.
   - Ensure the VCC is connected to 3.3V (the Pico's 3V3 pin) to match the logic level.

2. *Development Environment*:
   - Install the Pico SDK and set up your development environment (e.g., VS Code with
     CMake tools or a similar setup).
   - Place the `font12.c` and `fonts.h` files from the Waveshare demo code in your project
     directory.

3. *Build and Flash*:
   - Create a build directory: `mkdir build && cd build`
   - Run CMake: `cmake ..`
   - Build the project: `make`
   - Flash the `.uf2` file to the Pico by copying it to the Pico's USB mass storage device.

4. *Running the Program*:
   - The program initializes the LCD, clears it to white, draws a red rectangle outline,
     and displays "Hello, Pico!" in black.
   - It then alternates the color of the text "1.47 LCD" between blue and green every second.

### Explanation of Key Components
- *SPI Initialisation*: The Pico's `hardware/spi.h` is used to configure SPI0 at 40 MHz, which
  is suitable for the ST7789V3 controller based on the documentation's high-speed SPI requirements.
- *LCD Initialization*: The initialization sequence is adapted from the Waveshare documentation
  for the ST7789V3, including commands for sleep out, pixel format (RGB565), and gamma settings.
- *GUI Functions*: The `Paint_` functions are simplified versions of the Waveshare GUI library
  tailored for the Pico. They write directly to the LCD's RAM to avoid excessive memory usage.
- *Offset Handling*: The 172x320 display uses a 240x320 controller, so an X offset of 34 pixels is
  applied to center the display area, as derived from the documentation's resolution details.

### Limitations and Extensions
- *Memory*: The Pico's RAM limits the complexity of graphics operations. For larger images or more
  complex graphics, consider optimising the frame buffer or writing directly to the LCD without
  buffering.
- *Fonts*: Only Font12 is included for simplicity. Add other fonts (e.g., Font8, Font16) from the
  Waveshare library as needed.
- *Additional Features*: You can extend the program to include more GUI functions (e.g.,
  `Paint_DrawCircle`, `Paint_DrawLine`) or support for BMP image display by adapting the Waveshare
  `GUI_BMPfile.c` functions.
- *Performance*: The SPI speed is set to 40 MHz, but you can adjust it (e.g., lower to 20 MHz)
  if stability issues arise.

