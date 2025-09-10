#include "display_pack.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/dma.h"
#include "hardware/irq.h"

// Display Pack pin defs
#define DISPLAY_CS_PIN 17
#define DISPLAY_CLK_PIN 18
#define DISPLAY_MOSI_PIN 19
#define DISPLAY_DC_PIN 16
#define DISPLAY_RESET_PIN 21
#define DISPLAY_BL_PIN 20

// Button pins
#define BUTTON_A_PIN 12
#define BUTTON_B_PIN 13
#define BUTTON_X_PIN 14
#define BUTTON_Y_PIN 15

// DMA configuration
static uint dma_channel = 0;
static bool dma_initialized = false;
static volatile bool dma_busy = false;

// Internal state
static button_callback_t button_callbacks[4] = {NULL};
static bool button_state[4] = {false};
static bool button_last_state[4] = {false};
static uint32_t last_button_check = 0;

// DMA buffer for repeated pixel data (for solid fills)
static uint8_t dma_fill_buffer[512]; // Buffer for repeated color data
static uint8_t dma_single_pixel[2];  // Single pixel buffer for DMA

// Fixed 5x8 font
static const uint8_t font5x8[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // Space
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // !
    {0x00, 0x07, 0x00, 0x07, 0x00}, // "
    {0x14, 0x7F, 0x14, 0x7F, 0x14}, // #
    {0x12, 0x2A, 0x7F, 0x2A, 0x24}, // $
    {0x62, 0x64, 0x08, 0x13, 0x23}, // %
    {0x50, 0x22, 0x55, 0x49, 0x36}, // &
    {0x00, 0x00, 0x07, 0x00, 0x00}, // '
    {0x00, 0x41, 0x22, 0x1C, 0x00}, // (
    {0x00, 0x1C, 0x22, 0x41, 0x00}, // )
    {0x14, 0x08, 0x3E, 0x08, 0x14}, // *
    {0x08, 0x08, 0x3E, 0x08, 0x08}, // +
    {0x00, 0x30, 0x40, 0x00, 0x00}, // ,
    {0x08, 0x08, 0x08, 0x08, 0x08}, // -
    {0x00, 0x60, 0x60, 0x00, 0x00}, // .
    {0x02, 0x04, 0x08, 0x10, 0x20}, // /
    {0x3E, 0x45, 0x49, 0x51, 0x3E}, // 0
    {0x00, 0x40, 0x7F, 0x42, 0x00}, // 1
    {0x46, 0x49, 0x51, 0x61, 0x42}, // 2
    {0x31, 0x4B, 0x45, 0x41, 0x21}, // 3
    {0x10, 0x7F, 0x12, 0x14, 0x18}, // 4
    {0x39, 0x49, 0x49, 0x49, 0x2F}, // 5
    {0x30, 0x49, 0x49, 0x4A, 0x3C}, // 6
    {0x03, 0x05, 0x09, 0x71, 0x01}, // 7
    {0x36, 0x49, 0x49, 0x49, 0x36}, // 8
    {0x1E, 0x29, 0x49, 0x49, 0x0E}, // 9
    {0x00, 0x36, 0x36, 0x00, 0x00}, // :
    {0x00, 0x36, 0x76, 0x00, 0x00}, // ;
    {0x00, 0x41, 0x22, 0x14, 0x08}, // <
    {0x14, 0x14, 0x14, 0x14, 0x14}, // =
    {0x08, 0x14, 0x22, 0x41, 0x00}, // >
    {0x06, 0x09, 0x51, 0x01, 0x06}, // ?
    {0x0E, 0x49, 0x4F, 0x41, 0x3E}, // @
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, // A
    {0x36, 0x49, 0x49, 0x49, 0x7F}, // B
    {0x22, 0x41, 0x41, 0x41, 0x3E}, // C
    {0x1C, 0x22, 0x41, 0x41, 0x7F}, // D
    {0x41, 0x49, 0x49, 0x49, 0x7F}, // E
    {0x01, 0x09, 0x09, 0x09, 0x7F}, // F
    {0x7A, 0x49, 0x49, 0x41, 0x3E}, // G
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, // H
    {0x00, 0x41, 0x7F, 0x41, 0x00}, // I
    {0x01, 0x3F, 0x41, 0x40, 0x20}, // J
    {0x41, 0x22, 0x14, 0x08, 0x7F}, // K
    {0x40, 0x40, 0x40, 0x40, 0x7F}, // L
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // M
    {0x7F, 0x10, 0x0C, 0x02, 0x7F}, // N
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, // O
    {0x06, 0x09, 0x09, 0x09, 0x7F}, // P
    {0x5E, 0x21, 0x51, 0x41, 0x3E}, // Q
    {0x46, 0x29, 0x19, 0x09, 0x7F}, // R
    {0x32, 0x49, 0x49, 0x49, 0x26}, // S
    {0x01, 0x01, 0x7F, 0x01, 0x01}, // T
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, // U
    {0x1F, 0x20, 0x40, 0x20, 0x1F}, // V
    {0x3F, 0x40, 0x38, 0x40, 0x3F}, // W
    {0x63, 0x14, 0x08, 0x14, 0x63}, // X
    {0x07, 0x08, 0x70, 0x08, 0x07}, // Y
    {0x43, 0x45, 0x49, 0x51, 0x61}, // Z
};

// DMA interrupt handler
void dma_handler() {
    // Clear the interrupt request
    dma_hw->ints0 = 1u << dma_channel;
    dma_busy = false;
}

// Initialize DMA
static bool dma_init(void) {
    if (dma_initialized) return true;
    
    // Get a free DMA channel
    dma_channel = dma_claim_unused_channel(true);
    if (dma_channel < 0) return false;
    
    // Set up the DMA interrupt
    dma_channel_set_irq0_enabled(dma_channel, true);
    irq_set_exclusive_handler(DMA_IRQ_0, dma_handler);
    irq_set_enabled(DMA_IRQ_0, true);
    
    dma_initialized = true;
    return true;
}

// Wait for DMA to complete
static void dma_wait_for_finish(void) {
    while (dma_busy) {
        tight_loop_contents();
    }
}

// DMA-based SPI write for large data transfers
static void dma_spi_write_repeated(uint8_t* data, size_t data_size, uint32_t repeat_count) {
    if (!dma_initialized && !dma_init()) {
        // Fallback to regular SPI if DMA init fails
        for (uint32_t i = 0; i < repeat_count; i++) {
            spi_write_blocking(spi0, data, data_size);
        }
        return;
    }
    
    dma_wait_for_finish();
    dma_busy = true;
    
    // Configure DMA channel
    dma_channel_config c = dma_channel_get_default_config(dma_channel);
    channel_config_set_transfer_data_size(&c, DMA_SIZE_8);
    channel_config_set_dreq(&c, spi_get_dreq(spi0, true)); // TX DREQ
    channel_config_set_read_increment(&c, data_size > 1); // Don't increment for single byte
    channel_config_set_write_increment(&c, false); // Don't increment write address (SPI DR)
    
    // Set up the transfer
    dma_channel_configure(
        dma_channel,
        &c,
        &spi_get_hw(spi0)->dr,  // Write to SPI data register
        data,                   // Read from our data
        data_size * repeat_count, // Total transfer count
        false                   // Don't start yet
    );
    
    // Start the transfer
    dma_channel_start(dma_channel);
}

// DMA-based SPI write for buffer data
static void dma_spi_write_buffer(uint8_t* data, size_t len) {
    if (!dma_initialized && !dma_init()) {
        // Fallback to regular SPI if DMA init fails
        spi_write_blocking(spi0, data, len);
        return;
    }
    
    dma_wait_for_finish();
    dma_busy = true;
    
    // Configure DMA channel
    dma_channel_config c = dma_channel_get_default_config(dma_channel);
    channel_config_set_transfer_data_size(&c, DMA_SIZE_8);
    channel_config_set_dreq(&c, spi_get_dreq(spi0, true)); // TX DREQ
    channel_config_set_read_increment(&c, true);  // Increment read address
    channel_config_set_write_increment(&c, false); // Don't increment write address (SPI DR)
    
    // Set up the transfer
    dma_channel_configure(
        dma_channel,
        &c,
        &spi_get_hw(spi0)->dr,  // Write to SPI data register
        data,                   // Read from buffer
        len,                    // Transfer count
        false                   // Don't start yet
    );
    
    // Start the transfer
    dma_channel_start(dma_channel);
}

// Display low-level functions
static void display_write_command(uint8_t cmd) {
    dma_wait_for_finish(); // Ensure any DMA transfer is complete
    gpio_put(DISPLAY_DC_PIN, 0);
    gpio_put(DISPLAY_CS_PIN, 0);
    spi_write_blocking(spi0, &cmd, 1);
    gpio_put(DISPLAY_CS_PIN, 1);
}

static void display_write_data(uint8_t data) {
    dma_wait_for_finish(); // Ensure any DMA transfer is complete
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_CS_PIN, 0);
    spi_write_blocking(spi0, &data, 1);
    gpio_put(DISPLAY_CS_PIN, 1);
}

static void display_write_data_buf(uint8_t *data, size_t len) {
    dma_wait_for_finish(); // Ensure any DMA transfer is complete
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_CS_PIN, 0);
    
    if (len > 64) { // Use DMA for larger transfers
        dma_spi_write_buffer(data, len);
        dma_wait_for_finish();
    } else {
        spi_write_blocking(spi0, data, len);
    }
    
    gpio_put(DISPLAY_CS_PIN, 1);
}

static void display_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    display_write_command(0x2A); // CASET (Column Address Set)
    display_write_data((x0 + 53) >> 8);
    display_write_data((x0 + 53) & 0xFF);
    display_write_data((x1 + 53) >> 8);
    display_write_data((x1 + 53) & 0xFF);

    display_write_command(0x2B); // RASET (Row Address Set)
    display_write_data((y0 + 40) >> 8);
    display_write_data((y0 + 40) & 0xFF);
    display_write_data((y1 + 40) >> 8);
    display_write_data((y1 + 40) & 0xFF);
    
    display_write_command(0x2C); // RAMWR - Write to RAM
}

// Public display functions
bool display_pack_init(void) {
    // Init SPI
    spi_init(spi0, 20000000); // Increased to 20MHz for better performance
    gpio_set_function(DISPLAY_CLK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(DISPLAY_MOSI_PIN, GPIO_FUNC_SPI);
    
    // Init control pins
    gpio_init(DISPLAY_CS_PIN);
    gpio_init(DISPLAY_DC_PIN);
    gpio_init(DISPLAY_RESET_PIN);
    gpio_init(DISPLAY_BL_PIN);
    
    gpio_set_dir(DISPLAY_CS_PIN, GPIO_OUT);
    gpio_set_dir(DISPLAY_DC_PIN, GPIO_OUT);
    gpio_set_dir(DISPLAY_RESET_PIN, GPIO_OUT);
    gpio_set_dir(DISPLAY_BL_PIN, GPIO_OUT);
    
    // Start with everything high
    gpio_put(DISPLAY_CS_PIN, 1);
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_BL_PIN, 0); // Backlight off initially
    
    // Hardware reset
    gpio_put(DISPLAY_RESET_PIN, 1);
    sleep_ms(10);
    gpio_put(DISPLAY_RESET_PIN, 0);
    sleep_ms(10);
    gpio_put(DISPLAY_RESET_PIN, 1);
    sleep_ms(120);
    
    // Initialize DMA
    dma_init();
    
    // ST7789 initialisation sequence
    display_write_command(0x01); // SWRESET - Software reset
    sleep_ms(150);
    
    display_write_command(0x11); // SLPOUT - Sleep out
    sleep_ms(10);
    
    display_write_command(0x3A); // COLMOD - Interface Pixel Format
    display_write_data(0x55);    // 16-bit RGB565
    
    display_write_command(0x36); // MADCTL - Memory Data Access Control
    display_write_data(0x60);    //
    
    // Set display area to 240x135 (rotated)
    display_write_command(0x2A); // CASET (Column Address Set)
    display_write_data(0x00);
    display_write_data(0x35);    // Start at column 53
    display_write_data(0x00);
    display_write_data(0xBB);    // End at column 187

    display_write_command(0x2B); // RASET (Row Address Set)
    display_write_data(0x00);
    display_write_data(0x28);    // Start at row 40
    display_write_data(0x01);
    display_write_data(0x17);    // End at row 279
    
    display_write_command(0x21); // INVON - Invert colors
    display_write_command(0x13); // NORON - Normal display mode on
    sleep_ms(10);
    display_write_command(0x29); // DISPON - Display on
    sleep_ms(10);
    
    // Turn on backlight
    gpio_put(DISPLAY_BL_PIN, 1);
    
    return true;
}

void display_clear(uint16_t color) {
    display_fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color);
}

void display_fill_rect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color) {
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) return;
    if (x + width > DISPLAY_WIDTH) width = DISPLAY_WIDTH - x;
    if (y + height > DISPLAY_HEIGHT) height = DISPLAY_HEIGHT - y;
    
    uint32_t pixel_count = width * height;
    
    display_set_window(x, y, x + width - 1, y + height - 1);
    
    // Prepare color data
    uint8_t color_bytes[2] = {color >> 8, color & 0xFF};
    dma_single_pixel[0] = color_bytes[0];
    dma_single_pixel[1] = color_bytes[1];
    
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_CS_PIN, 0);
    
    if (pixel_count > 32 && dma_initialized) {
        // Use DMA for large fills
        // Fill our buffer with repeated color pattern
        size_t buffer_pixels = sizeof(dma_fill_buffer) / 2;
        for (size_t i = 0; i < buffer_pixels; i++) {
            dma_fill_buffer[i * 2] = color_bytes[0];
            dma_fill_buffer[i * 2 + 1] = color_bytes[1];
        }
        
        // Send full buffer chunks
        uint32_t full_chunks = pixel_count / buffer_pixels;
        for (uint32_t i = 0; i < full_chunks; i++) {
            dma_spi_write_buffer(dma_fill_buffer, sizeof(dma_fill_buffer));
            dma_wait_for_finish();
        }
        
        // Send remaining pixels
        uint32_t remaining = pixel_count % buffer_pixels;
        if (remaining > 0) {
            dma_spi_write_buffer(dma_fill_buffer, remaining * 2);
            dma_wait_for_finish();
        }
    } else {
        // Use blocking SPI for small fills
        for (uint32_t i = 0; i < pixel_count; i++) {
            spi_write_blocking(spi0, color_bytes, 2);
        }
    }
    
    gpio_put(DISPLAY_CS_PIN, 1);
}

void display_draw_pixel(uint16_t x, uint16_t y, uint16_t color) {
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) return;
    display_fill_rect(x, y, 1, 1, color);
}

void display_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg_color) {
    if (c < 32 || c > 90) c = 32; // Space for unsupported chars
    
    const uint8_t *char_data = font5x8[c - 32];
    
    // Draw character bitmap
    for (int col = 0; col < 5; col++) {
        uint8_t line = char_data[4 - col]; // Reverse column order
        for (int row = 0; row < 8; row++) {
            uint16_t pixel_color = (line & (1 << row)) ? color : bg_color;
            if (x + col < DISPLAY_WIDTH && y + row < DISPLAY_HEIGHT) {
                display_draw_pixel(x + col, y + row, pixel_color);
            }
        }
    }
}

void display_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg_color) {
    int offset_x = 0;
    while (*str && x + offset_x < DISPLAY_WIDTH) {
        display_draw_char(x + offset_x, y, *str, color, bg_color);
        offset_x += 6; // 5 pixel font + 1 pixel spacing
        str++;
    }
}

void display_set_backlight(bool on) {
    gpio_put(DISPLAY_BL_PIN, on ? 1 : 0);
}

// Button functions (unchanged)
void buttons_init(void) {
    const uint8_t pins[] = {BUTTON_A_PIN, BUTTON_B_PIN, BUTTON_X_PIN, BUTTON_Y_PIN};
    
    for (int i = 0; i < 4; i++) {
        gpio_init(pins[i]);
        gpio_set_dir(pins[i], GPIO_IN);
        gpio_pull_up(pins[i]);
        button_state[i] = true; // Pulled up initially
        button_last_state[i] = true;
    }
}

void buttons_update(void) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    
    // Debounce - only check buttons every 50ms
    if (now - last_button_check < 50) return;
    last_button_check = now;
    
    const uint8_t pins[] = {BUTTON_A_PIN, BUTTON_B_PIN, BUTTON_X_PIN, BUTTON_Y_PIN};
    
    for (int i = 0; i < 4; i++) {
        button_last_state[i] = button_state[i];
        button_state[i] = gpio_get(pins[i]);
        
        // Call callback if button was just pressed
        if (button_last_state[i] && !button_state[i] && button_callbacks[i]) {
            button_callbacks[i]((button_t)i);
        }
    }
}

bool button_pressed(button_t button) {
    if (button > BUTTON_Y) return false;
    return !button_state[button]; // Inverted because of pull-up
}

bool button_just_pressed(button_t button) {
    if (button > BUTTON_Y) return false;
    return button_last_state[button] && !button_state[button];
}

bool button_just_released(button_t button) {
    if (button > BUTTON_Y) return false;
    return !button_last_state[button] && button_state[button];
}

void button_set_callback(button_t button, button_callback_t callback) {
    if (button <= BUTTON_Y) {
        button_callbacks[button] = callback;
    }
}

// LED functions (still not implemented)
void led_init(void) {
    // Not yet implemented in Display Pack
}

void led_set(bool on) {
    // Not yet implemented in Display Pack
}

// Utility function to check if DMA is busy (for external use)
bool display_dma_busy(void) {
    return dma_busy;
}

// Function to wait for any pending DMA operations
void display_wait_for_dma(void) {
    dma_wait_for_finish();
}

// Function to deinitialize DMA (if needed)
void display_dma_deinit(void) {
    if (dma_initialized) {
        dma_channel_unclaim(dma_channel);
        irq_set_enabled(DMA_IRQ_0, false);
        dma_initialized = false;
    }
}

// Cleanup function to be called at program end
void display_cleanup(void) {
    display_dma_deinit();
    spi_deinit(spi0);
    gpio_put(DISPLAY_BL_PIN, 0); // Turn off backlight
}

