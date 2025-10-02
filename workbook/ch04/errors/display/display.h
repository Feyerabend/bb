#ifndef DISPLAY_H
#define DISPLAY_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Display specifications
#define DISPLAY_WIDTH  320
#define DISPLAY_HEIGHT 240

// RGB565 colors
#define COLOR_BLACK   0x0000
#define COLOR_WHITE   0xFFFF
#define COLOR_RED     0xF800
#define COLOR_GREEN   0x07E0
#define COLOR_BLUE    0x001F
#define COLOR_YELLOW  0xFFE0
#define COLOR_CYAN    0x07FF
#define COLOR_MAGENTA 0xF81F

// Comprehensive error codes
typedef enum {
    DISP_OK = 0,
    
    // Initialization errors
    DISP_ERR_ALREADY_INIT,
    DISP_ERR_NOT_INIT,
    DISP_ERR_SPI_INIT_FAILED,
    DISP_ERR_GPIO_INIT_FAILED,
    DISP_ERR_RESET_FAILED,
    DISP_ERR_CONFIG_FAILED,
    
    // Parameter errors
    DISP_ERR_NULL_POINTER,
    DISP_ERR_INVALID_COORDS,
    DISP_ERR_INVALID_DIMENSIONS,
    DISP_ERR_BUFFER_TOO_SMALL,
    
    // DMA errors
    DISP_ERR_DMA_NOT_AVAILABLE,
    DISP_ERR_DMA_CONFIG_FAILED,
    DISP_ERR_DMA_TIMEOUT,
    DISP_ERR_DMA_ABORT_FAILED,
    
    // Communication errors
    DISP_ERR_SPI_WRITE_FAILED,
    DISP_ERR_CMD_FAILED,
    DISP_ERR_DATA_FAILED,
    DISP_ERR_TIMEOUT,
    
    // Resource errors
    DISP_ERR_OUT_OF_MEMORY,
    DISP_ERR_RESOURCE_BUSY,
    
    DISP_ERR_UNKNOWN
} disp_error_t;

// Error context for debugging
typedef struct {
    disp_error_t code;
    const char *function;
    int line;
    const char *message;
} disp_error_context_t;

// Configuration options
typedef struct {
    uint32_t spi_baudrate;
    bool use_dma;
    uint32_t dma_timeout_ms;
    bool enable_backlight;
} disp_config_t;

// Get default configuration
disp_config_t disp_get_default_config(void);

// Core display functions
disp_error_t disp_init(const disp_config_t *config);
disp_error_t disp_deinit(void);
bool disp_is_initialized(void);

// Drawing functions
disp_error_t disp_clear(uint16_t color);
disp_error_t disp_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);
disp_error_t disp_draw_pixel(uint16_t x, uint16_t y, uint16_t color);
disp_error_t disp_draw_hline(uint16_t x, uint16_t y, uint16_t w, uint16_t color);
disp_error_t disp_draw_vline(uint16_t x, uint16_t y, uint16_t h, uint16_t color);
disp_error_t disp_blit(uint16_t x, uint16_t y, uint16_t w, uint16_t h, const uint16_t *pixels);

// Text functions
disp_error_t disp_draw_char(uint16_t x, uint16_t y, char c, uint16_t fg, uint16_t bg);
disp_error_t disp_draw_text(uint16_t x, uint16_t y, const char *text, uint16_t fg, uint16_t bg);

// Control functions
disp_error_t disp_set_backlight(bool enabled);
disp_error_t disp_wait_complete(uint32_t timeout_ms);

// Error handling utilities
const char* disp_error_string(disp_error_t error);
disp_error_context_t disp_get_last_error(void);
void disp_clear_error(void);

// Macro for error context tracking
#define DISP_ERROR(code, msg) disp_set_error_context((code), __func__, __LINE__, (msg))

#endif // DISPLAY_H

