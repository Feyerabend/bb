
### File: `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.13)

# Pull in SDK (must be before project)
include(pico_sdk_import.cmake)

project(display_examples C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Pico SDK
pico_sdk_init()

# Display driver library
add_library(display STATIC
    display.c
)

target_link_libraries(display
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_dma
    hardware_irq
)

target_include_directories(display PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)

# Basic example
add_executable(example_basic
    example_basic.c
)

target_link_libraries(example_basic
    display
    pico_stdlib
)

pico_enable_stdio_usb(example_basic 1)
pico_enable_stdio_uart(example_basic 0)
pico_add_extra_outputs(example_basic)

# Advanced example
add_executable(example_advanced
    example_advanced.c
)

target_link_libraries(example_advanced
    display
    pico_stdlib
)

pico_enable_stdio_usb(example_advanced 1)
pico_enable_stdio_uart(example_advanced 0)
pico_add_extra_outputs(example_advanced)

# Simple test (minimal example)
add_executable(simple_test
    simple_test.c
)

target_link_libraries(simple_test
    display
    pico_stdlib
)

pico_enable_stdio_usb(simple_test 1)
pico_enable_stdio_uart(simple_test 0)
pico_add_extra_outputs(simple_test)
```



### File: `simple_test.c`

```c
#include "display.h"
#include "pico/stdlib.h"
#include <stdio.h>

int main(void) {
    // Initialize USB serial (for error messages)
    stdio_init_all();
    sleep_ms(2000);
    
    printf("\n=== Simple Display Test ===\n");
    
    // Initialize display with default config
    disp_error_t err = disp_init(NULL);  // NULL uses defaults
    
    if (err != DISP_OK) {
        printf("ERROR: Failed to initialize display\n");
        printf("  Code: %d\n", err);
        printf("  Message: %s\n", disp_error_string(err));
        
        disp_error_context_t ctx = disp_get_last_error();
        if (ctx.function) {
            printf("  Location: %s:%d\n", ctx.function, ctx.line);
        }
        if (ctx.message) {
            printf("  Details: %s\n", ctx.message);
        }
        
        // Halt on init failure
        while (true) {
            sleep_ms(1000);
        }
    }
    
    printf("Display initialized successfully!\n");
    
    // Clear screen to black
    err = disp_clear(COLOR_BLACK);
    if (err != DISP_OK) {
        printf("ERROR: Clear failed - %s\n", disp_error_string(err));
    }
    
    // Draw red rectangle
    err = disp_fill_rect(50, 50, 100, 80, COLOR_RED);
    if (err != DISP_OK) {
        printf("ERROR: Rectangle failed - %s\n", disp_error_string(err));
    }
    
    // Draw some text
    err = disp_draw_text(60, 100, "Hello!", COLOR_WHITE, COLOR_BLACK);
    if (err != DISP_OK) {
        printf("ERROR: Text failed - %s\n", disp_error_string(err));
    }
    
    printf("Display test complete!\n");
    printf("You should see:\n");
    printf("  - Black background\n");
    printf("  - Red rectangle at (50,50)\n");
    printf("  - White text saying 'Hello!'\n");
    
    // Keep running
    while (true) {
        sleep_ms(1000);
    }
    
    return 0;
}
```



### File: `example_basic.c`

```c
#include "display.h"
#include "pico/stdlib.h"
#include <stdio.h>

// Helper function to print errors
static void print_error(const char *context, disp_error_t err) {
    if (err != DISP_OK) {
        disp_error_context_t ctx = disp_get_last_error();
        printf("ERROR in %s: %s\n", context, disp_error_string(err));
        if (ctx.function) {
            printf("  Location: %s:%d\n", ctx.function, ctx.line);
            if (ctx.message) {
                printf("  Details: %s\n", ctx.message);
            }
        }
    }
}

// Example 1: Basic initialization and drawing
void example_basic_init_and_draw(void) {
    printf("\n=== Example 1: Basic Init and Draw ===\n");
    
    // Get default configuration
    disp_config_t config = disp_get_default_config();
    
    // Initialize display
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        print_error("disp_init", err);
        return;
    }
    printf("Display initialized successfully\n");
    
    // Clear screen to black
    err = disp_clear(COLOR_BLACK);
    if (err != DISP_OK) {
        print_error("disp_clear", err);
        return;
    }
    printf("Screen cleared\n");
    
    // Draw some colored rectangles
    err = disp_fill_rect(10, 10, 100, 50, COLOR_RED);
    if (err != DISP_OK) {
        print_error("draw red rect", err);
        return;
    }
    
    err = disp_fill_rect(120, 10, 100, 50, COLOR_GREEN);
    if (err != DISP_OK) {
        print_error("draw green rect", err);
        return;
    }
    
    err = disp_fill_rect(230, 10, 80, 50, COLOR_BLUE);
    if (err != DISP_OK) {
        print_error("draw blue rect", err);
        return;
    }
    
    printf("Rectangles drawn successfully\n");
    
    // Draw text
    err = disp_draw_text(10, 80, "Hello, Display!", COLOR_WHITE, COLOR_BLACK);
    if (err != DISP_OK) {
        print_error("draw text", err);
        return;
    }
    
    printf("Text drawn successfully\n");
    printf("All operations completed successfully!\n");
}

// Example 2: Error handling - trying to use before init
void example_error_not_initialized(void) {
    printf("\n=== Example 2: Error - Not Initialized ===\n");
    
    // Try to draw without initializing
    disp_error_t err = disp_clear(COLOR_BLACK);
    
    if (err != DISP_OK) {
        print_error("attempting to clear before init", err);
        printf("This error was expected - we tried to use display before init\n");
    }
}

// Example 3: Error handling - invalid parameters
void example_error_invalid_params(void) {
    printf("\n=== Example 3: Error - Invalid Parameters ===\n");
    
    disp_config_t config = disp_get_default_config();
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        print_error("disp_init", err);
        return;
    }
    
    // Try to draw outside bounds
    err = disp_draw_pixel(500, 500, COLOR_RED);
    if (err != DISP_OK) {
        print_error("drawing pixel out of bounds", err);
        printf("This error was expected - coordinates were out of bounds\n");
    }
    
    // Try to draw text with NULL pointer
    err = disp_draw_text(10, 10, NULL, COLOR_WHITE, COLOR_BLACK);
    if (err != DISP_OK) {
        print_error("drawing NULL text", err);
        printf("This error was expected - text pointer was NULL\n");
    }
    
    disp_deinit();
}

// Example 4: Custom configuration
void example_custom_config(void) {
    printf("\n=== Example 4: Custom Configuration ===\n");
    
    // Create custom configuration
    disp_config_t config = {
        .spi_baudrate = 20000000,    // Slower speed
        .use_dma = false,            // Disable DMA
        .dma_timeout_ms = 500,       // Shorter timeout
        .enable_backlight = false    // Start with backlight off
    };
    
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        print_error("disp_init with custom config", err);
        return;
    }
    printf("Display initialized with custom config\n");
    
    // Clear screen
    err = disp_clear(COLOR_BLUE);
    if (err != DISP_OK) {
        print_error("disp_clear", err);
        return;
    }
    
    // Manually enable backlight
    err = disp_set_backlight(true);
    if (err != DISP_OK) {
        print_error("enabling backlight", err);
        return;
    }
    printf("Backlight enabled\n");
    
    sleep_ms(2000);
    
    // Disable backlight
    err = disp_set_backlight(false);
    if (err != DISP_OK) {
        print_error("disabling backlight", err);
        return;
    }
    printf("Backlight disabled\n");
    
    disp_deinit();
}

// Example 5: Drawing patterns with error checking
void example_draw_pattern(void) {
    printf("\n=== Example 5: Drawing Pattern ===\n");
    
    disp_config_t config = disp_get_default_config();
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        print_error("disp_init", err);
        return;
    }
    
    // Clear to black
    err = disp_clear(COLOR_BLACK);
    if (err != DISP_OK) {
        print_error("clear", err);
        disp_deinit();
        return;
    }
    
    // Draw a gradient pattern
    printf("Drawing gradient pattern...\n");
    for (int y = 0; y < 240; y += 10) {
        // Create color gradient (red to blue)
        uint16_t color = ((y * 31 / 240) << 11) | ((31 - y * 31 / 240));
        
        err = disp_draw_hline(0, y, 320, color);
        if (err != DISP_OK) {
            print_error("drawing horizontal line", err);
            disp_deinit();
            return;
        }
    }
    printf("Pattern drawn successfully\n");
    
    // Add some text on top
    err = disp_draw_text(80, 110, "GRADIENT TEST", COLOR_WHITE, COLOR_BLACK);
    if (err != DISP_OK) {
        print_error("drawing text", err);
        disp_deinit();
        return;
    }
    
    printf("All operations completed successfully\n");
    
    disp_deinit();
}

// Main function
int main(void) {
    // Initialize stdio for printf
    stdio_init_all();
    sleep_ms(2000);  // Wait for USB serial
    
    printf("\n");
    printf("Display Driver Error Handling Examples\n");
    
    // Run examples
    example_error_not_initialized();
    sleep_ms(1000);
    
    example_error_invalid_params();
    sleep_ms(1000);
    
    example_basic_init_and_draw();
    sleep_ms(3000);
    
    example_custom_config();
    sleep_ms(1000);
    
    example_draw_pattern();
    
    printf("\n");
    printf("All examples completed!\n");
    
    // Keep display showing final result
    while (true) {
        sleep_ms(1000);
    }
    
    return 0;
}
```



### File: `example_advanced.c`

```c
#include "display.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include <string.h>

// Error logging system
#define MAX_ERROR_LOG 10
static struct {
    disp_error_context_t errors[MAX_ERROR_LOG];
    int count;
} error_log = {0};

static void log_error(disp_error_t err) {
    if (err == DISP_OK) return;
    
    if (error_log.count < MAX_ERROR_LOG) {
        error_log.errors[error_log.count++] = disp_get_last_error();
    }
}

static void print_error_log(void) {
    printf("\n=== Error Log (%d errors) ===\n", error_log.count);
    for (int i = 0; i < error_log.count; i++) {
        disp_error_context_t *e = &error_log.errors[i];
        printf("[%d] %s\n", i + 1, disp_error_string(e->code));
        if (e->function) {
            printf("    at %s:%d\n", e->function, e->line);
        }
        if (e->message) {
            printf("    %s\n", e->message);
        }
    }
}

// Example 1: Robust initialization with fallback
void example_robust_init(void) {
    printf("\n=== Example 1: Robust Initialization ===\n");
    
    // Try with DMA first
    disp_config_t config = disp_get_default_config();
    config.use_dma = true;
    
    disp_error_t err = disp_init(&config);
    
    if (err != DISP_OK) {
        printf("Failed to init with DMA, trying without...\n");
        log_error(err);
        
        // Fallback: try without DMA
        config.use_dma = false;
        err = disp_init(&config);
        
        if (err != DISP_OK) {
            printf("Initialization failed completely!\n");
            log_error(err);
            return;
        }
        printf("Initialized successfully without DMA\n");
    } else {
        printf("Initialized successfully with DMA\n");
    }
    
    // Test the display
    err = disp_clear(COLOR_GREEN);
    if (err != DISP_OK) {
        printf("Failed to clear display\n");
        log_error(err);
        return;
    }
    
    err = disp_draw_text(10, 10, "Init OK!", COLOR_BLACK, COLOR_GREEN);
    log_error(err);
    
    sleep_ms(2000);
    disp_deinit();
}

// Example 2: Batch operations with error recovery
void example_batch_operations(void) {
    printf("\n=== Example 2: Batch Operations with Recovery ===\n");
    
    disp_config_t config = disp_get_default_config();
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        log_error(err);
        return;
    }
    
    err = disp_clear(COLOR_BLACK);
    if (err != DISP_OK) {
        log_error(err);
        disp_deinit();
        return;
    }
    
    // Batch draw operation with error tracking
    int success_count = 0;
    int error_count = 0;
    
    printf("Drawing 50 random rectangles...\n");
    for (int i = 0; i < 50; i++) {
        uint16_t x = (rand() % 300);
        uint16_t y = (rand() % 220);
        uint16_t w = 20;
        uint16_t h = 20;
        uint16_t color = rand() & 0xFFFF;
        
        err = disp_fill_rect(x, y, w, h, color);
        if (err != DISP_OK) {
            error_count++;
            log_error(err);
            
            // Try to recover by skipping this one
            printf("  Skipped rectangle %d due to error\n", i);
            disp_clear_error();
            continue;
        }
        success_count++;
    }
    
    printf("Results: %d successful, %d errors\n", success_count, error_count);
    
    // Add status text
    char status[50];
    snprintf(status, sizeof(status), "OK:%d ERR:%d", success_count, error_count);
    err = disp_draw_text(10, 10, status, COLOR_YELLOW, COLOR_BLACK);
    log_error(err);
    
    sleep_ms(3000);
    disp_deinit();
}

// Example 3: Safe buffer operations
void example_safe_buffer_blit(void) {
    printf("\n=== Example 3: Safe Buffer Operations ===\n");
    
    disp_config_t config = disp_get_default_config();
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        log_error(err);
        return;
    }
    
    err = disp_clear(COLOR_BLACK);
    if (err != DISP_OK) {
        log_error(err);
        disp_deinit();
        return;
    }
    
    // Create a small buffer (100x100 pixels)
    const int buf_w = 100;
    const int buf_h = 100;
    uint16_t *buffer = malloc(buf_w * buf_h * sizeof(uint16_t));
    
    if (!buffer) {
        printf("Failed to allocate buffer\n");
        disp_deinit();
        return;
    }
    
    // Fill buffer with gradient
    for (int y = 0; y < buf_h; y++) {
        for (int x = 0; x < buf_w; x++) {
            uint8_t r = (x * 31) / buf_w;
            uint8_t g = (y * 63) / buf_h;
            uint8_t b = 31 - ((x + y) * 31) / (buf_w + buf_h);
            buffer[y * buf_w + x] = (r << 11) | (g << 5) | b;
        }
    }
    
    printf("Blitting buffer to display...\n");
    
    // Test blitting to various positions
    struct { int x; int y; } positions[] = {
        {0, 0},      // Top-left
        {220, 0},    // Top-right
        {0, 140},    // Bottom-left
        {220, 140},  // Bottom-right
        {110, 70}    // Center
    };
    
    for (int i = 0; i < 5; i++) {
        err = disp_blit(positions[i].x, positions[i].y, buf_w, buf_h, buffer);
        if (err != DISP_OK) {
            printf("  Failed to blit at position %d (%d, %d)\n", 
                   i, positions[i].x, positions[i].y);
            log_error(err);
        } else {
            printf("  Blit %d successful\n", i);
        }
    }
    
    free(buffer);
    
    err = disp_draw_text(10, 10, "Buffer Test", COLOR_WHITE, COLOR_BLACK);
    log_error(err);
    
    sleep_ms(3000);
    disp_deinit();
}

// Example 4: Timeout handling
void example_timeout_handling(void) {
    printf("\n=== Example 4: Timeout Handling ===\n");
    
    disp_config_t config = disp_get_default_config();
    config.dma_timeout_ms = 100;  // Very short timeout for testing
    
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        log_error(err);
        return;
    }
    
    printf("Testing with short timeout...\n");
    
    // Try a large operation that might timeout
    err = disp_clear(COLOR_BLUE);
    if (err == DISP_ERR_DMA_TIMEOUT) {
        printf("Timeout detected (expected with very short timeout)\n");
        log_error(err);
        
        // Try to recover by waiting
        printf("Attempting recovery...\n");
        err = disp_wait_complete(1000);
        if (err == DISP_OK) {
            printf("Recovery successful\n");
        } else {
            printf("Recovery failed\n");
            log_error(err);
        }
    } else if (err != DISP_OK) {
        printf("Other error occurred\n");
        log_error(err);
    } else {
        printf("Operation completed within timeout\n");
    }
    
    disp_deinit();
}

// Example 5: State validation
void example_state_validation(void) {
    printf("\n=== Example 5: State Validation ===\n");
    
    // Test 1: Check state before init
    printf("Test 1: Is initialized? %s\n", 
           disp_is_initialized() ? "Yes" : "No");
    
    // Test 2: Initialize
    disp_config_t config = disp_get_default_config();
    disp_error_t err = disp_init(&config);
    if (err != DISP_OK) {
        log_error(err);
        return;
    }
    
    printf("Test 2: Is initialized? %s\n", 
           disp_is_initialized() ? "Yes" : "No");
    
    // Test 3: Try to init again (should fail)
    err = disp_init(&config);
    if (err == DISP_ERR_ALREADY_INIT) {
        printf("Test 3: Double init correctly rejected\n");
        log_error(err);
        disp_clear_error();  // Clear since this was expected
    } else {
        printf("Test 3: Unexpected result from double init\n");
    }
    
    // Test 4: Deinit
    err = disp_deinit();
    if (err != DISP_OK) {
        printf("Test 4: Deinit failed\n");
        log_error(err);
    } else {
        printf("Test 4: Deinit successful\n");
    }
    
    // Test 5: Check state after deinit
    printf("Test 5: Is initialized? %s\n", 
           disp_is_initialized() ? "Yes" : "No");
    
    // Test 6: Try to use after deinit
    err = disp_clear(COLOR_BLACK);
    if (err == DISP_ERR_NOT_INIT) {
        printf("Test 6: Use after deinit correctly rejected\n");
        log_error(err);
    }
}

int main(void) {
    stdio_init_all();
    sleep_ms(2000);
    
    printf("\n");
    printf("Advanced Display Error Handling Examples\n");
    
    // Run advanced examples
    example_robust_init();
    sleep_ms(500);
    
    example_batch_operations();
    sleep_ms(500);
    
    example_safe_buffer_blit();
    sleep_ms(500);
    
    example_timeout_handling();
    sleep_ms(500);
    
    example_state_validation();
    
    // Print accumulated errors
    print_error_log();
    
    printf("\n");
    printf("All advanced examples completed!\n");
    
    while (true) {
        sleep_ms(1000);
    }
    
    return 0;
}
```



### Quick Start Guide

1. **Create project structure:**
```bash
mkdir display_driver
cd display_driver
```

2. **Copy files:**
   - Copy `display.h` and `display.c` from the first two artifacts
   - Copy all the files above into your project directory

3. **Add Pico SDK:**
   - Copy `pico_sdk_import.cmake` from your Pico SDK

4. **Build:**
```bash
mkdir build
cd build
cmake ..
make
```

5. **Flash to Pico:**
```bash
# Copy the UF2 file you want to test
cp simple_test.uf2 /media/RPI-RP2/
```
