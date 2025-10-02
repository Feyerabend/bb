
## Error-Focused Display Driver

A comprehensive display driver for the Pimoroni Display Pack 2.0 (ST7789 320x240)
with some robust error handling as the primary design focus.

This driver prioritises *error handling and reliability* over everything else:

1. *Every operation returns an error code*
2. *Detailed error context tracking* (function, line, message)
3. *Comprehensive parameter validation*
4. *Graceful degradation* (e.g., falls back to non-DMA if DMA fails)
5. *Timeout protection* on all blocking operations
6. *State validation* prevents use-after-free and double-init bugs
7. *NULL pointer checks* on all user-provided data
8. *Bounds checking* on all coordinate and dimension parameters


### Error Codes

```c
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
    DISP_ERR_RESOURCE_BUSY
} disp_error_t;
```

### Context Tracking

Every error includes detailed context:

```c
typedef struct {
    disp_error_t code;      // Error code
    const char *function;   // Function where error occurred
    int line;               // Line number
    const char *message;    // Human-readable message
} disp_error_context_t;

// Get the last error
disp_error_context_t ctx = disp_get_last_error();
printf("Error at %s:%d - %s\n", ctx.function, ctx.line, ctx.message);
```

### Handling Utilities

```c
// Get human-readable error string
const char* disp_error_string(disp_error_t error);

// Get detailed error context
disp_error_context_t disp_get_last_error(void);

// Clear error state
void disp_clear_error(void);
```


### Minimal Example

```c
#include "display.h"

int main(void) {
    // Initialize with defaults
    disp_error_t err = disp_init(NULL);
    if (err != DISP_OK) {
        // Handle error
        printf("Init failed: %s\n", disp_error_string(err));
        return -1;
    }
    
    // Clear to black
    if ((err = disp_clear(COLOR_BLACK)) != DISP_OK) {
        printf("Clear failed: %s\n", disp_error_string(err));
        return -1;
    }
    
    // Draw rectangle
    err = disp_fill_rect(10, 10, 100, 50, COLOR_RED);
    if (err != DISP_OK) {
        printf("Draw failed: %s\n", disp_error_string(err));
        return -1;
    }
    
    return 0;
}
```

### With Error Context

```c
disp_error_t err = disp_draw_text(10, 10, NULL, COLOR_WHITE, COLOR_BLACK);

if (err != DISP_OK) {
    disp_error_context_t ctx = disp_get_last_error();
    printf("ERROR: %s\n", disp_error_string(err));
    printf("  Function: %s\n", ctx.function);
    printf("  Line: %d\n", ctx.line);
    printf("  Details: %s\n", ctx.message);
}
```


### API Init

```c
// Get default configuration
disp_config_t disp_get_default_config(void);

// Initialize display
disp_error_t disp_init(const disp_config_t *config);

// Deinitialize (cleanup)
disp_error_t disp_deinit(void);

// Check if initialized
bool disp_is_initialized(void);
```

### API Configuration Options

```c
typedef struct {
    uint32_t spi_baudrate;    // SPI clock speed (default: 31.25 MHz)
    bool use_dma;             // Enable DMA transfers (default: true)
    uint32_t dma_timeout_ms;  // DMA timeout (default: 1000 ms)
    bool enable_backlight;    // Turn on backlight at init (default: true)
} disp_config_t;
```

### API Drawing Functions

```c
// Clear entire screen
disp_error_t disp_clear(uint16_t color);

// Fill rectangle
disp_error_t disp_fill_rect(uint16_t x, uint16_t y, 
                            uint16_t w, uint16_t h, 
                            uint16_t color);

// Draw single pixel
disp_error_t disp_draw_pixel(uint16_t x, uint16_t y, uint16_t color);

// Draw horizontal line
disp_error_t disp_draw_hline(uint16_t x, uint16_t y, 
                             uint16_t w, uint16_t color);

// Draw vertical line
disp_error_t disp_draw_vline(uint16_t x, uint16_t y, 
                             uint16_t h, uint16_t color);

// Blit pixel buffer to screen
disp_error_t disp_blit(uint16_t x, uint16_t y, 
                       uint16_t w, uint16_t h, 
                       const uint16_t *pixels);
```

### API Text Functions

```c
// Draw single character
disp_error_t disp_draw_char(uint16_t x, uint16_t y, 
                            char c, 
                            uint16_t fg, uint16_t bg);

// Draw text string
disp_error_t disp_draw_text(uint16_t x, uint16_t y, 
                            const char *text, 
                            uint16_t fg, uint16_t bg);
```

### API Control Functions

```c
// Control backlight
disp_error_t disp_set_backlight(bool enabled);

// Wait for pending operations to complete
disp_error_t disp_wait_complete(uint32_t timeout_ms);
```



### Pattern 1: Check Every Operation

```c
disp_error_t err;

if ((err = disp_init(NULL)) != DISP_OK) {
    handle_error(err);
    return;
}

if ((err = disp_clear(COLOR_BLACK)) != DISP_OK) {
    handle_error(err);
    return;
}

if ((err = disp_draw_text(10, 10, "Hello", COLOR_WHITE, COLOR_BLACK)) != DISP_OK) {
    handle_error(err);
    return;
}
```


### Pattern 2: Fail-Fast with Context

```c
#define CHECK_ERROR(call) do { \
    disp_error_t _err = (call); \
    if (_err != DISP_OK) { \
        disp_error_context_t ctx = disp_get_last_error(); \
        printf("ERROR at %s:%d: %s\n", ctx.function, ctx.line, ctx.message); \
        return _err; \
    } \
} while(0)

void my_draw_function(void) {
    CHECK_ERROR(disp_init(NULL));
    CHECK_ERROR(disp_clear(COLOR_BLACK));
    CHECK_ERROR(disp_draw_text(10, 10, "Test", COLOR_WHITE, COLOR_BLACK));
}
```


### Pattern 3: Graceful Degradation

```c
disp_config_t config = disp_get_default_config();
config.use_dma = true;

disp_error_t err = disp_init(&config);
if (err == DISP_ERR_DMA_NOT_AVAILABLE) {
    // Fallback: retry without DMA
    printf("DMA not available, using blocking mode\n");
    config.use_dma = false;
    err = disp_init(&config);
}

if (err != DISP_OK) {
    printf("Failed to initialize: %s\n", disp_error_string(err));
    return -1;
}
```


### Pattern 4: Batch Operations with Error Log

```c
typedef struct {
    disp_error_context_t errors[10];
    int count;
} error_log_t;

error_log_t log = {0};

void log_error(disp_error_t err) {
    if (err != DISP_OK && log.count < 10) {
        log.errors[log.count++] = disp_get_last_error();
    }
}

// Perform batch operations
for (int i = 0; i < 100; i++) {
    disp_error_t err = disp_fill_rect(i*3, i*2, 10, 10, COLOR_RED);
    if (err != DISP_OK) {
        log_error(err);
        // Continue with next operation
        disp_clear_error();
    }
}

// Review errors after batch
print_error_log(&log);
```


### Safety Features

#### 1. State Validation
- Prevents operations before initialization
- Detects double initialization
- Validates state after deinitialization

#### 2. Parameter Validation
- NULL pointer checks on all buffers
- Coordinate bounds checking
- Dimension validation
- Automatic clamping where appropriate

#### 3. Timeout Protection
- All DMA operations have configurable timeouts
- Automatic abort on timeout
- Resource cleanup after timeout

#### 4. Resource Management
- Automatic DMA channel cleanup
- Safe interrupt handler removal
- SPI deinitialization on shutdown

#### 5. Bounds Checking
```c
// Automatically clamps to display bounds
disp_fill_rect(300, 200, 100, 100, COLOR_RED);
// Draws only 20x40 pixels (clamped to 320x240 display)
```



## Examples Included

### 1. `simple_test.c`
Minimal working example - just initializes display and draws basic shapes.

### 2. `example_basic.c`
Demonstrates:
- Basic initialization and drawing
- Error detection before init
- Invalid parameter handling
- Custom configuration
- Pattern drawing with error checking

### 3. `example_advanced.c`
Demonstrates:
- Robust initialization with fallback
- Batch operations with error recovery
- Safe buffer operations
- Timeout handling
- State validation
- Error logging system


## Performance Notes

- **With DMA**: ~40ms for full-screen update (320x240x2 = 153,600 bytes)
- **Without DMA**: ~200ms for full-screen update
- **Text rendering**: ~1-2ms per character
- **Small rectangles (<64 pixels)**: Use blocking SPI (faster than DMA setup)



### Issue: "Display not initialised"
```c
// Solution: Check initialization
if (!disp_is_initialized()) {
    disp_error_t err = disp_init(NULL);
    if (err != DISP_OK) {
        printf("Init failed: %s\n", disp_error_string(err));
    }
}
```

### Issue: "DMA timeout"
```c
// Solution: Increase timeout or disable DMA
disp_config_t config = disp_get_default_config();
config.dma_timeout_ms = 5000;  // 5 seconds
// OR
config.use_dma = false;  // Use blocking mode
```

### Issue: "Invalid coordinates"
```c
// Solution: Validate before drawing
if (x < DISPLAY_WIDTH && y < DISPLAY_HEIGHT) {
    disp_draw_pixel(x, y, color);
}
// OR let the driver clamp automatically with fill_rect
```

### Issue: "NULL pointer" error
```c
// Solution: Always validate buffers
const char *text = get_text();
if (text != NULL) {
    disp_draw_text(10, 10, text, COLOR_WHITE, COLOR_BLACK);
} else {
    disp_draw_text(10, 10, "(null)", COLOR_RED, COLOR_BLACK);
}
```



### Enable Verbose Error Reporting
```c
void print_detailed_error(disp_error_t err) {
    if (err == DISP_OK) return;
    
    disp_error_context_t ctx = disp_get_last_error();
    printf("\n=== ERROR ===\n");
    printf("Code: %d\n", err);
    printf("String: %s\n", disp_error_string(err));
    printf("Function: %s\n", ctx.function ? ctx.function : "unknown");
    printf("Line: %d\n", ctx.line);
    printf("Message: %s\n", ctx.message ? ctx.message : "no details");
    printf("=============\n\n");
}
```

### Track All Errors During Development
```c
#ifdef DEBUG
#define DISP_CALL(x) do { \
    disp_error_t _err = (x); \
    if (_err != DISP_OK) { \
        print_detailed_error(_err); \
    } \
} while(0)
#else
#define DISP_CALL(x) (x)
#endif

// Use in code
DISP_CALL(disp_clear(COLOR_BLACK));
DISP_CALL(disp_draw_text(10, 10, "Test", COLOR_WHITE, COLOR_BLACK));
```

### Color Format

Colors are in RGB565 format (16-bit):
- 5 bits red (bits 11-15)
- 6 bits green (bits 5-10)
- 5 bits blue (bits 0-4)

```c
// Predefined colors
COLOR_BLACK     0x0000
COLOR_WHITE     0xFFFF
COLOR_RED       0xF800
COLOR_GREEN     0x07E0
COLOR_BLUE      0x001F
COLOR_YELLOW    0xFFE0
COLOR_CYAN      0x07FF
COLOR_MAGENTA   0xF81F

// Custom colors
uint16_t custom = (red << 11) | (green << 5) | blue;
```


### Contributing

When contributing, please maintain the error-focused design:
1. Every new function must return `disp_error_t`
2. Use `DISP_ERROR()` macro to set error context
3. Validate all parameters at function entry
4. Add new error codes to the enum as needed
5. Update error strings array
6. Document error conditions in comments

### Further Reading

- [Pico SDK Documentation](https://www.raspberrypi.com/documentation/pico-sdk/)
- [ST7789 Datasheet](https://www.displayfuture.com/Display/datasheet/controller/ST7789.pdf)
- [RGB565 Color Format](https://en.wikipedia.org/wiki/High_color)

