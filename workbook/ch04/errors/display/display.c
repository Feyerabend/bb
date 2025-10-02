#include "display.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/dma.h"
#include "hardware/irq.h"
#include "pico/time.h"
#include <string.h>

// Pin definitions
#define PIN_CS    17
#define PIN_CLK   18
#define PIN_MOSI  19
#define PIN_DC    16
#define PIN_RST   21
#define PIN_BL    20

// State tracking
static struct {
    bool initialized;
    bool dma_enabled;
    int dma_channel;
    volatile bool dma_busy;
    disp_error_context_t last_error;
    disp_config_t config;
} g_state = {
    .initialized = false,
    .dma_enabled = false,
    .dma_channel = -1,
    .dma_busy = false,
    .last_error = {DISP_OK, NULL, 0, NULL}
};

// Error strings
static const char* ERROR_STRINGS[] = {
    "Success",
    "Already initialized",
    "Not initialized",
    "SPI initialization failed",
    "GPIO initialization failed",
    "Reset failed",
    "Configuration failed",
    "NULL pointer",
    "Invalid coordinates",
    "Invalid dimensions",
    "Buffer too small",
    "DMA not available",
    "DMA configuration failed",
    "DMA timeout",
    "DMA abort failed",
    "SPI write failed",
    "Command failed",
    "Data write failed",
    "Operation timeout",
    "Out of memory",
    "Resource busy",
    "Unknown error"
};

// 5x7 minimal font
static const uint8_t FONT_5X7[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // Space (32)
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // !
    {0x00, 0x07, 0x00, 0x07, 0x00}, // "
    {0x14, 0x7F, 0x14, 0x7F, 0x14}, // #
    {0x24, 0x2A, 0x7F, 0x2A, 0x12}, // $
    {0x23, 0x13, 0x08, 0x64, 0x62}, // %
    {0x36, 0x49, 0x55, 0x22, 0x50}, // &
    {0x00, 0x05, 0x03, 0x00, 0x00}, // '
    {0x00, 0x1C, 0x22, 0x41, 0x00}, // (
    {0x00, 0x41, 0x22, 0x1C, 0x00}, // )
    {0x14, 0x08, 0x3E, 0x08, 0x14}, // *
    {0x08, 0x08, 0x3E, 0x08, 0x08}, // +
    {0x00, 0x50, 0x30, 0x00, 0x00}, // ,
    {0x08, 0x08, 0x08, 0x08, 0x08}, // -
    {0x00, 0x60, 0x60, 0x00, 0x00}, // .
    {0x20, 0x10, 0x08, 0x04, 0x02}, // /
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, // 0
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // 1
    {0x42, 0x61, 0x51, 0x49, 0x46}, // 2
    {0x21, 0x41, 0x45, 0x4B, 0x31}, // 3
    {0x18, 0x14, 0x12, 0x7F, 0x10}, // 4
    {0x27, 0x45, 0x45, 0x45, 0x39}, // 5
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, // 6
    {0x01, 0x71, 0x09, 0x05, 0x03}, // 7
    {0x36, 0x49, 0x49, 0x49, 0x36}, // 8
    {0x06, 0x49, 0x49, 0x29, 0x1E}, // 9
};

// Forward declarations
static void disp_set_error_context(disp_error_t code, const char *func, int line, const char *msg);
static disp_error_t disp_gpio_init_checked(void);
static disp_error_t disp_spi_init_checked(uint32_t baudrate);
static disp_error_t disp_reset_sequence(void);
static disp_error_t disp_configure_lcd(void);
static disp_error_t disp_dma_init(void);
static void disp_dma_deinit(void);
static disp_error_t disp_wait_dma(uint32_t timeout_ms);


// ERROR HANDLING


void disp_set_error_context(disp_error_t code, const char *func, int line, const char *msg) {
    g_state.last_error.code = code;
    g_state.last_error.function = func;
    g_state.last_error.line = line;
    g_state.last_error.message = msg;
}

const char* disp_error_string(disp_error_t error) {
    if (error < 0 || error >= (sizeof(ERROR_STRINGS) / sizeof(ERROR_STRINGS[0]))) {
        return ERROR_STRINGS[DISP_ERR_UNKNOWN];
    }
    return ERROR_STRINGS[error];
}

disp_error_context_t disp_get_last_error(void) {
    return g_state.last_error;
}

void disp_clear_error(void) {
    g_state.last_error.code = DISP_OK;
    g_state.last_error.function = NULL;
    g_state.last_error.line = 0;
    g_state.last_error.message = NULL;
}


// DMA HANDLING


static void __isr dma_irq_handler(void) {
    if (g_state.dma_channel >= 0 && (dma_hw->ints0 & (1u << g_state.dma_channel))) {
        dma_hw->ints0 = 1u << g_state.dma_channel;
        g_state.dma_busy = false;
    }
}

static disp_error_t disp_dma_init(void) {
    if (g_state.dma_enabled) {
        return DISP_OK;
    }
    
    g_state.dma_channel = dma_claim_unused_channel(false);
    if (g_state.dma_channel < 0) {
        return DISP_ERROR(DISP_ERR_DMA_NOT_AVAILABLE, "No DMA channels available");
    }
    
    dma_channel_set_irq0_enabled(g_state.dma_channel, true);
    irq_set_exclusive_handler(DMA_IRQ_0, dma_irq_handler);
    irq_set_enabled(DMA_IRQ_0, true);
    
    g_state.dma_enabled = true;
    return DISP_OK;
}

static void disp_dma_deinit(void) {
    if (!g_state.dma_enabled) return;
    
    disp_wait_dma(g_state.config.dma_timeout_ms);
    
    if (g_state.dma_channel >= 0) {
        dma_channel_set_irq0_enabled(g_state.dma_channel, false);
        dma_channel_unclaim(g_state.dma_channel);
        g_state.dma_channel = -1;
    }
    
    irq_set_enabled(DMA_IRQ_0, false);
    g_state.dma_enabled = false;
}

static disp_error_t disp_wait_dma(uint32_t timeout_ms) {
    if (!g_state.dma_busy) return DISP_OK;
    
    uint32_t start = to_ms_since_boot(get_absolute_time());
    while (g_state.dma_busy) {
        if (to_ms_since_boot(get_absolute_time()) - start > timeout_ms) {
            // Timeout - force abort
            if (g_state.dma_channel >= 0) {
                dma_channel_abort(g_state.dma_channel);
                dma_hw->ints0 = 1u << g_state.dma_channel;
            }
            g_state.dma_busy = false;
            return DISP_ERROR(DISP_ERR_DMA_TIMEOUT, "DMA operation timed out");
        }
        tight_loop_contents();
    }
    return DISP_OK;
}


// LOW-LEVEL COMMUNICATION


static disp_error_t disp_write_cmd(uint8_t cmd) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    
    disp_error_t err = disp_wait_dma(g_state.config.dma_timeout_ms);
    if (err != DISP_OK) return err;
    
    gpio_put(PIN_DC, 0);
    gpio_put(PIN_CS, 0);
    
    int written = spi_write_blocking(spi0, &cmd, 1);
    
    gpio_put(PIN_CS, 1);
    
    if (written != 1) {
        return DISP_ERROR(DISP_ERR_CMD_FAILED, "Command write failed");
    }
    
    return DISP_OK;
}

static disp_error_t disp_write_data_byte(uint8_t data) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    
    disp_error_t err = disp_wait_dma(g_state.config.dma_timeout_ms);
    if (err != DISP_OK) return err;
    
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_CS, 0);
    
    int written = spi_write_blocking(spi0, &data, 1);
    
    gpio_put(PIN_CS, 1);
    
    if (written != 1) {
        return DISP_ERROR(DISP_ERR_DATA_FAILED, "Data write failed");
    }
    
    return DISP_OK;
}

static disp_error_t disp_write_data_buf(const uint8_t *data, size_t len) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    if (!data) {
        return DISP_ERROR(DISP_ERR_NULL_POINTER, "NULL data buffer");
    }
    if (len == 0) {
        return DISP_ERROR(DISP_ERR_INVALID_DIMENSIONS, "Zero length buffer");
    }
    
    disp_error_t err = disp_wait_dma(g_state.config.dma_timeout_ms);
    if (err != DISP_OK) return err;
    
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_CS, 0);
    
    if (g_state.dma_enabled && len > 64) {
        // Use DMA for large transfers
        g_state.dma_busy = true;
        
        dma_channel_config c = dma_channel_get_default_config(g_state.dma_channel);
        channel_config_set_transfer_data_size(&c, DMA_SIZE_8);
        channel_config_set_dreq(&c, spi_get_dreq(spi0, true));
        channel_config_set_read_increment(&c, true);
        channel_config_set_write_increment(&c, false);
        
        dma_channel_configure(
            g_state.dma_channel,
            &c,
            &spi_get_hw(spi0)->dr,
            data,
            len,
            true
        );
        
        err = disp_wait_dma(g_state.config.dma_timeout_ms);
    } else {
        // Use blocking SPI for small transfers
        int written = spi_write_blocking(spi0, data, len);
        if ((size_t)written != len) {
            err = DISP_ERROR(DISP_ERR_SPI_WRITE_FAILED, "SPI write incomplete");
        }
    }
    
    gpio_put(PIN_CS, 1);
    return err;
}

static disp_error_t disp_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    disp_error_t err;
    
    // Column address set
    if ((err = disp_write_cmd(0x2A)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(x0 >> 8)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(x0 & 0xFF)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(x1 >> 8)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(x1 & 0xFF)) != DISP_OK) return err;
    
    // Row address set
    if ((err = disp_write_cmd(0x2B)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(y0 >> 8)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(y0 & 0xFF)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(y1 >> 8)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(y1 & 0xFF)) != DISP_OK) return err;
    
    // Memory write
    if ((err = disp_write_cmd(0x2C)) != DISP_OK) return err;
    
    return DISP_OK;
}


// INITIALIZATION


disp_config_t disp_get_default_config(void) {
    disp_config_t config = {
        .spi_baudrate = 31250000,  // 31.25 MHz
        .use_dma = true,
        .dma_timeout_ms = 1000,
        .enable_backlight = true
    };
    return config;
}

static disp_error_t disp_gpio_init_checked(void) {
    // Initialize all GPIO pins
    const uint8_t pins[] = {PIN_CS, PIN_DC, PIN_RST, PIN_BL};
    
    for (size_t i = 0; i < sizeof(pins); i++) {
        gpio_init(pins[i]);
        gpio_set_dir(pins[i], GPIO_OUT);
    }
    
    // Set initial states
    gpio_put(PIN_CS, 1);
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_BL, 0);
    gpio_put(PIN_RST, 1);
    
    return DISP_OK;
}

static disp_error_t disp_spi_init_checked(uint32_t baudrate) {
    uint32_t actual = spi_init(spi0, baudrate);
    if (actual == 0) {
        return DISP_ERROR(DISP_ERR_SPI_INIT_FAILED, "SPI initialization returned 0");
    }
    
    gpio_set_function(PIN_CLK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    
    return DISP_OK;
}

static disp_error_t disp_reset_sequence(void) {
    gpio_put(PIN_RST, 1);
    sleep_ms(10);
    gpio_put(PIN_RST, 0);
    sleep_ms(10);
    gpio_put(PIN_RST, 1);
    sleep_ms(120);
    
    return DISP_OK;
}

static disp_error_t disp_configure_lcd(void) {
    disp_error_t err;
    
    // Software reset
    if ((err = disp_write_cmd(0x01)) != DISP_OK) return err;
    sleep_ms(150);
    
    // Sleep out
    if ((err = disp_write_cmd(0x11)) != DISP_OK) return err;
    sleep_ms(120);
    
    // Color mode - 16-bit RGB565
    if ((err = disp_write_cmd(0x3A)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(0x55)) != DISP_OK) return err;
    
    // Memory access control
    if ((err = disp_write_cmd(0x36)) != DISP_OK) return err;
    if ((err = disp_write_data_byte(0x70)) != DISP_OK) return err;
    
    // Inversion on
    if ((err = disp_write_cmd(0x21)) != DISP_OK) return err;
    
    // Normal mode
    if ((err = disp_write_cmd(0x13)) != DISP_OK) return err;
    sleep_ms(10);
    
    // Display on
    if ((err = disp_write_cmd(0x29)) != DISP_OK) return err;
    sleep_ms(100);
    
    return DISP_OK;
}

disp_error_t disp_init(const disp_config_t *config) {
    if (g_state.initialized) {
        return DISP_ERROR(DISP_ERR_ALREADY_INIT, "Display already initialized");
    }
    
    // Use default config if NULL
    if (config) {
        g_state.config = *config;
    } else {
        g_state.config = disp_get_default_config();
    }
    
    disp_error_t err;
    
    // Initialize SPI
    if ((err = disp_spi_init_checked(g_state.config.spi_baudrate)) != DISP_OK) {
        return err;
    }
    
    // Initialize GPIOs
    if ((err = disp_gpio_init_checked()) != DISP_OK) {
        spi_deinit(spi0);
        return err;
    }
    
    // Hardware reset
    if ((err = disp_reset_sequence()) != DISP_OK) {
        spi_deinit(spi0);
        return err;
    }
    
    g_state.initialized = true;  // Set before LCD config
    
    // Configure LCD
    if ((err = disp_configure_lcd()) != DISP_OK) {
        g_state.initialized = false;
        spi_deinit(spi0);
        return err;
    }
    
    // Initialize DMA if requested
    if (g_state.config.use_dma) {
        err = disp_dma_init();
        // Don't fail init if DMA unavailable - just disable it
        if (err != DISP_OK) {
            g_state.config.use_dma = false;
        }
    }
    
    // Enable backlight if requested
    if (g_state.config.enable_backlight) {
        gpio_put(PIN_BL, 1);
    }
    
    return DISP_OK;
}

disp_error_t disp_deinit(void) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    
    // Turn off backlight
    gpio_put(PIN_BL, 0);
    
    // Clean up DMA
    disp_dma_deinit();
    
    // Deinitialize SPI
    spi_deinit(spi0);
    
    g_state.initialized = false;
    return DISP_OK;
}

bool disp_is_initialized(void) {
    return g_state.initialized;
}


// DRAWING FUNCTIONS


disp_error_t disp_clear(uint16_t color) {
    return disp_fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color);
}

disp_error_t disp_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    
    // Validate coordinates
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) {
        return DISP_ERROR(DISP_ERR_INVALID_COORDS, "Coordinates out of bounds");
    }
    
    // Clamp dimensions
    if (x + w > DISPLAY_WIDTH) w = DISPLAY_WIDTH - x;
    if (y + h > DISPLAY_HEIGHT) h = DISPLAY_HEIGHT - y;
    
    if (w == 0 || h == 0) return DISP_OK;
    
    disp_error_t err = disp_set_window(x, y, x + w - 1, y + h - 1);
    if (err != DISP_OK) return err;
    
    // Prepare color bytes (big-endian)
    uint8_t color_buf[2] = {color >> 8, color & 0xFF};
    uint32_t pixel_count = w * h;
    
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_CS, 0);
    
    // Write pixels
    for (uint32_t i = 0; i < pixel_count; i++) {
        spi_write_blocking(spi0, color_buf, 2);
    }
    
    gpio_put(PIN_CS, 1);
    return DISP_OK;
}

disp_error_t disp_draw_pixel(uint16_t x, uint16_t y, uint16_t color) {
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) {
        return DISP_ERROR(DISP_ERR_INVALID_COORDS, "Pixel coordinates out of bounds");
    }
    return disp_fill_rect(x, y, 1, 1, color);
}

disp_error_t disp_draw_hline(uint16_t x, uint16_t y, uint16_t w, uint16_t color) {
    return disp_fill_rect(x, y, w, 1, color);
}

disp_error_t disp_draw_vline(uint16_t x, uint16_t y, uint16_t h, uint16_t color) {
    return disp_fill_rect(x, y, 1, h, color);
}

disp_error_t disp_blit(uint16_t x, uint16_t y, uint16_t w, uint16_t h, const uint16_t *pixels) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    if (!pixels) {
        return DISP_ERROR(DISP_ERR_NULL_POINTER, "NULL pixel buffer");
    }
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) {
        return DISP_ERROR(DISP_ERR_INVALID_COORDS, "Coordinates out of bounds");
    }
    
    // Clamp dimensions
    if (x + w > DISPLAY_WIDTH) w = DISPLAY_WIDTH - x;
    if (y + h > DISPLAY_HEIGHT) h = DISPLAY_HEIGHT - y;
    
    if (w == 0 || h == 0) return DISP_OK;
    
    disp_error_t err = disp_set_window(x, y, x + w - 1, y + h - 1);
    if (err != DISP_OK) return err;
    
    size_t byte_count = w * h * 2;
    return disp_write_data_buf((const uint8_t*)pixels, byte_count);
}


// TEXT FUNCTIONS


disp_error_t disp_draw_char(uint16_t x, uint16_t y, char c, uint16_t fg, uint16_t bg) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) {
        return DISP_ERROR(DISP_ERR_INVALID_COORDS, "Character position out of bounds");
    }
    
    // Use space for unsupported characters
    if (c < 32 || c > 41) c = 32;
    
    const uint8_t *glyph = FONT_5X7[c - 32];
    
    // Draw character with bounds checking
    for (int col = 0; col < 5 && (x + col) < DISPLAY_WIDTH; col++) {
        uint8_t line = glyph[col];
        for (int row = 0; row < 7 && (y + row) < DISPLAY_HEIGHT; row++) {
            uint16_t pixel = (line & (1 << row)) ? fg : bg;
            disp_error_t err = disp_draw_pixel(x + col, y + row, pixel);
            if (err != DISP_OK) return err;
        }
    }
    
    return DISP_OK;
}

disp_error_t disp_draw_text(uint16_t x, uint16_t y, const char *text, uint16_t fg, uint16_t bg) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    if (!text) {
        return DISP_ERROR(DISP_ERR_NULL_POINTER, "NULL text string");
    }
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) {
        return DISP_ERROR(DISP_ERR_INVALID_COORDS, "Text position out of bounds");
    }
    
    uint16_t offset = 0;
    while (*text && (x + offset) < DISPLAY_WIDTH) {
        disp_error_t err = disp_draw_char(x + offset, y, *text, fg, bg);
        if (err != DISP_OK) return err;
        offset += 6;  // 5 pixel font + 1 spacing
        text++;
    }
    
    return DISP_OK;
}


// CONTROL FUNCTIONS


disp_error_t disp_set_backlight(bool enabled) {
    if (!g_state.initialized) {
        return DISP_ERROR(DISP_ERR_NOT_INIT, "Display not initialized");
    }
    
    gpio_put(PIN_BL, enabled ? 1 : 0);
    return DISP_OK;
}

disp_error_t disp_wait_complete(uint32_t timeout_ms) {
    return disp_wait_dma(timeout_ms);
}
