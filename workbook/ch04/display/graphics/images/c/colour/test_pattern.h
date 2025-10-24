#ifndef TEST_PATTERN_H
#define TEST_PATTERN_H

#include <stdint.h>

// Test pattern dimensions (64x48 scaled to 320x240)
#define TEST_PATTERN_WIDTH 64
#define TEST_PATTERN_HEIGHT 48

// RGB565 test pattern data - TV test card inspired pattern
// This will be scaled 5x to fill the 320x240 display
const uint16_t test_pattern[TEST_PATTERN_HEIGHT][TEST_PATTERN_WIDTH] = {
    // Top border - alternating black/white checkerboard
    [0 ... 3] = {
        [0 ... 63] = 0xFFFF  // White border top
    },
    
    // Main test bars section (rows 4-35)
    [4 ... 35] = {
        // Color bars: White, Yellow, Cyan, Green, Magenta, Red, Blue, Black
        [0 ... 7] = 0xFFFF,    // White
        [8 ... 15] = 0xFFE0,   // Yellow
        [16 ... 23] = 0x07FF,  // Cyan
        [24 ... 31] = 0x07E0,  // Green
        [32 ... 39] = 0xF81F,  // Magenta
        [40 ... 47] = 0xF800,  // Red
        [48 ... 55] = 0x001F,  // Blue
        [56 ... 63] = 0x0000,  // Black
    },
    
    // Middle section - gradient/pluge pattern
    [36 ... 41] = {
        // Dark gradient
        [0 ... 7] = 0x0841,    // Very dark blue
        [8 ... 15] = 0x0000,   // Black
        [16 ... 23] = 0x18E3,  // Dark cyan
        [24 ... 31] = 0x0000,  // Black
        [32 ... 39] = 0x18E3,  // Dark cyan
        [40 ... 47] = 0x0000,  // Black
        [48 ... 55] = 0x0841,  // Very dark blue
        [56 ... 63] = 0x0000,  // Black
    },
    
    // Bottom section - small color squares
    [42 ... 47] = {
        [0 ... 15] = 0x0861,   // Navy
        [16 ... 31] = 0xFFFF,  // White
        [32 ... 47] = 0x0861,  // Navy
        [48 ... 63] = 0x0000,  // Black
    },
};

// Color palette definitions for button cycling
typedef struct {
    const char* name;
    uint16_t color;
    uint8_t r_bits;  // Red component (5 bits)
    uint8_t g_bits;  // Green component (6 bits)
    uint8_t b_bits;  // Blue component (5 bits)
} color_info_t;

#define NUM_COLORS 16

const color_info_t color_palette[NUM_COLORS] = {
    {"Black",   0x0000, 0,  0,  0},
    {"White",   0xFFFF, 31, 63, 31},
    {"Red",     0xF800, 31, 0,  0},
    {"Green",   0x07E0, 0,  63, 0},
    {"Blue",    0x001F, 0,  0,  31},
    {"Yellow",  0xFFE0, 31, 63, 0},
    {"Cyan",    0x07FF, 0,  63, 31},
    {"Magenta", 0xF81F, 31, 0,  31},
    {"Orange",  0xFC00, 31, 32, 0},
    {"Purple",  0x8010, 16, 0,  16},
    {"Pink",    0xFE19, 31, 48, 25},
    {"Lime",    0x87E0, 16, 63, 0},
    {"Navy",    0x0010, 0,  0,  16},
    {"Teal",    0x0410, 0,  32, 16},
    {"Maroon",  0x7800, 15, 0,  0},
    {"Gray",    0x8410, 16, 32, 16},
};

// Helper function to convert RGB888 to RGB565
static inline uint16_t rgb888_to_rgb565(uint8_t r, uint8_t g, uint8_t b) {
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

// Helper function to extract RGB components from RGB565
static inline void rgb565_to_components(uint16_t color, uint8_t *r, uint8_t *g, uint8_t *b) {
    *r = (color >> 11) & 0x1F;  // 5 bits
    *g = (color >> 5) & 0x3F;   // 6 bits
    *b = color & 0x1F;           // 5 bits
}

// Helper to convert 5/6 bit components back to 8-bit for display
static inline uint8_t scale_5bit_to_8bit(uint8_t val) {
    return (val << 3) | (val >> 2);
}

static inline uint8_t scale_6bit_to_8bit(uint8_t val) {
    return (val << 2) | (val >> 4);
}

#endif // TEST_PATTERN_H