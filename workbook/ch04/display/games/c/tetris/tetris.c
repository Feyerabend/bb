#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"
#include "hardware/dma.h"

// Display Pack 2.0 Pin Definitions ~ check again?
#define LCD_DC      16
#define LCD_CS      17
#define LCD_SCK     18
#define LCD_MOSI    19
#define LCD_RST     21
#define LCD_BL      20

// Button pins
#define BTN_A       12
#define BTN_B       13
#define BTN_X       14
#define BTN_Y       15

// RGB LED pins
#define LED_R       6
#define LED_G       7
#define LED_B       8

// ST7789 Display constants
#define ST7789_WIDTH  320
#define ST7789_HEIGHT 240

// ST7789 Commands
#define ST7789_SWRESET    0x01
#define ST7789_SLPOUT     0x11
#define ST7789_COLMOD     0x3A
#define ST7789_MADCTL     0x36
#define ST7789_CASET      0x2A
#define ST7789_RASET      0x2B
#define ST7789_RAMWR      0x2C
#define ST7789_DISPON     0x29
#define ST7789_INVON      0x21

// Game constants
#define BOARD_WIDTH     10
#define BOARD_HEIGHT    20
#define BLOCK_SIZE      12
#define BOARD_OFFSET_X  50
#define BOARD_OFFSET_Y  10

// Buffer constants
#define GAME_AREA_WIDTH  (BOARD_WIDTH * BLOCK_SIZE + 4)  // +4 for border
#define GAME_AREA_HEIGHT (BOARD_HEIGHT * BLOCK_SIZE + 4)
#define BUFFER_SIZE (GAME_AREA_WIDTH * GAME_AREA_HEIGHT * 2) // 2 bytes per pixel

// Colours (RGB565)
#define BLACK       0x0000
#define WHITE       0xFFFF
#define RED         0xF800
#define GREEN       0x07E0
#define BLUE        0x001F
#define YELLOW      0xFFE0
#define CYAN        0x07FF
#define MAGENTA     0xF81F
#define ORANGE      0xFD20
#define GRAY        0x8410

// DMA channels
static int dma_chan = -1;
static int dma_chan_ctrl = -1;

// Frame buffers - double buffering
static uint16_t frame_buffer[GAME_AREA_WIDTH * GAME_AREA_HEIGHT];
static uint16_t back_buffer[GAME_AREA_WIDTH * GAME_AREA_HEIGHT];
static uint8_t dma_buffer[BUFFER_SIZE]; // DMA buffer in correct byte order

// Dirty region tracking
typedef struct {
    int min_x, min_y, max_x, max_y;
    bool dirty;
} DirtyRegion;

static DirtyRegion dirty_region = {0, 0, 0, 0, false};

// Tetris piece colors
uint16_t piece_colors[7] = { CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED };

// Game board - 0 = empty, 1-7 = filled with color index
uint8_t board[BOARD_HEIGHT][BOARD_WIDTH];
uint8_t prev_board[BOARD_HEIGHT][BOARD_WIDTH]; // For change detection

// Current piece state
typedef struct {
    int x, y;           // Position
    int type;           // Piece type (0-6)
    int rotation;       // Rotation state (0-3)
} Piece;

Piece current_piece;
Piece prev_piece; // For change detection
Piece next_piece;

// Game state
int score = 0;
int level = 1;
int lines_cleared = 0;
int drop_timer = 0;
int drop_speed = 48;
bool game_over = false;
bool need_new_piece = true;
bool force_full_redraw = false;

// Button states
bool btn_a = false, btn_b = false, btn_x = false, btn_y = false;
bool prev_btn_a = false, prev_btn_b = false, prev_btn_x = false, prev_btn_y = false;

// Tetris piece definitions
const uint8_t tetris_pieces[7][4][4][4] = {
    // I piece
    {
        {{0,0,0,0},{1,1,1,1},{0,0,0,0},{0,0,0,0}},
        {{0,0,1,0},{0,0,1,0},{0,0,1,0},{0,0,1,0}},
        {{0,0,0,0},{0,0,0,0},{1,1,1,1},{0,0,0,0}},
        {{0,1,0,0},{0,1,0,0},{0,1,0,0},{0,1,0,0}}
    },
    // O piece
    {
        {{0,1,1,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,1,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,1,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,1,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}}
    },
    // T piece
    {
        {{0,1,0,0},{1,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,0,0},{0,1,1,0},{0,1,0,0},{0,0,0,0}},
        {{0,0,0,0},{1,1,1,0},{0,1,0,0},{0,0,0,0}},
        {{0,1,0,0},{1,1,0,0},{0,1,0,0},{0,0,0,0}}
    },
    // S piece
    {
        {{0,1,1,0},{1,1,0,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,0,0},{0,1,1,0},{0,0,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,1,0},{1,1,0,0},{0,0,0,0}},
        {{1,0,0,0},{1,1,0,0},{0,1,0,0},{0,0,0,0}}
    },
    // Z piece
    {
        {{1,1,0,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,0,1,0},{0,1,1,0},{0,1,0,0},{0,0,0,0}},
        {{0,0,0,0},{1,1,0,0},{0,1,1,0},{0,0,0,0}},
        {{0,1,0,0},{1,1,0,0},{1,0,0,0},{0,0,0,0}}
    },
    // J piece
    {
        {{1,0,0,0},{1,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,1,0},{0,1,0,0},{0,1,0,0},{0,0,0,0}},
        {{0,0,0,0},{1,1,1,0},{0,0,1,0},{0,0,0,0}},
        {{0,1,0,0},{0,1,0,0},{1,1,0,0},{0,0,0,0}}
    },
    // L piece
    {
        {{0,0,1,0},{1,1,1,0},{0,0,0,0},{0,0,0,0}},
        {{0,1,0,0},{0,1,0,0},{0,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{1,1,1,0},{1,0,0,0},{0,0,0,0}},
        {{1,1,0,0},{0,1,0,0},{0,1,0,0},{0,0,0,0}}
    }
};

// DMA Functions
void init_dma() {
    dma_chan = dma_claim_unused_channel(true);
    
    // Configure DMA channel for data transfer
    dma_channel_config c = dma_channel_get_default_config(dma_chan);
    channel_config_set_transfer_data_size(&c, DMA_SIZE_8);
    channel_config_set_dreq(&c, spi_get_dreq(spi0, true));
    channel_config_set_write_increment(&c, false);
    channel_config_set_read_increment(&c, true);
    
    dma_channel_configure(
        dma_chan,
        &c,
        &spi_get_hw(spi0)->dr,  // Write to SPI data register
        NULL,                   // Read address (set later)
        0,                      // Transfer count (set later)
        false                   // Don't start yet
    );
}

void dma_wait_for_completion() {
    dma_channel_wait_for_finish_blocking(dma_chan);
}

// Enhanced ST7789 Functions with DMA
void st7789_write_cmd(uint8_t cmd) {
    gpio_put(LCD_DC, 0);
    gpio_put(LCD_CS, 0);
    spi_write_blocking(spi0, &cmd, 1);
    gpio_put(LCD_CS, 1);
}

void st7789_write_data_dma(uint8_t *data, size_t len) {
    gpio_put(LCD_DC, 1);
    gpio_put(LCD_CS, 0);
    
    // Use DMA for large transfers
    if (len > 64) {
        dma_channel_set_read_addr(dma_chan, data, false);
        dma_channel_set_trans_count(dma_chan, len, true);
        dma_wait_for_completion();
    } else { // single SPI write for small transfers
        spi_write_blocking(spi0, data, len);
    }
    
    gpio_put(LCD_CS, 1);
}

void st7789_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    uint8_t data[4];
    
    st7789_write_cmd(ST7789_CASET);
    data[0] = x0 >> 8;
    data[1] = x0 & 0xFF;
    data[2] = x1 >> 8;
    data[3] = x1 & 0xFF;
    st7789_write_data_dma(data, 4);
    
    st7789_write_cmd(ST7789_RASET);
    data[0] = y0 >> 8;
    data[1] = y0 & 0xFF;
    data[2] = y1 >> 8;
    data[3] = y1 & 0xFF;
    st7789_write_data_dma(data, 4);
}

void prepare_dma_buffer(uint16_t *pixels, int pixel_count) {
    // Convert 16-bit pixels to byte buffer with proper endianness
    for (int i = 0; i < pixel_count; i++) {
        dma_buffer[i * 2] = pixels[i] >> 8;
        dma_buffer[i * 2 + 1] = pixels[i] & 0xFF;
    }
}

void st7789_write_region_dma(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t *pixels) {
    st7789_set_window(x, y, x + w - 1, y + h - 1);
    st7789_write_cmd(ST7789_RAMWR);
    
    int pixel_count = w * h;
    prepare_dma_buffer(pixels, pixel_count);
    st7789_write_data_dma(dma_buffer, pixel_count * 2);
}

void st7789_clear_screen() {
    st7789_set_window(0, 0, ST7789_WIDTH - 1, ST7789_HEIGHT - 1);
    st7789_write_cmd(ST7789_RAMWR);
    
    uint32_t pixel_count = (uint32_t)ST7789_WIDTH * ST7789_HEIGHT;
    
    // Prepare colour data (black)
    uint8_t color_bytes[2] = {BLACK >> 8, BLACK & 0xFF};
    
    gpio_put(LCD_DC, 1);
    gpio_put(LCD_CS, 0);
    
    if (pixel_count > 32 && dma_chan >= 0) {
        // Use DMA for large fills - prepare buffer with repeated black pixels
        static uint8_t dma_fill_buffer[2048]; // Larger buffer for efficiency
        size_t buffer_pixels = sizeof(dma_fill_buffer) / 2;
        
        // Fill buffer with black pixels
        for (size_t i = 0; i < buffer_pixels; i++) {
            dma_fill_buffer[i * 2] = color_bytes[0];
            dma_fill_buffer[i * 2 + 1] = color_bytes[1];
        }
        
        // Send full buffer chunks
        uint32_t full_chunks = pixel_count / buffer_pixels;
        for (uint32_t i = 0; i < full_chunks; i++) {
            dma_channel_set_read_addr(dma_chan, dma_fill_buffer, false);
            dma_channel_set_trans_count(dma_chan, sizeof(dma_fill_buffer), true);
            dma_wait_for_completion();
        }
        
        // Send remaining pixels
        uint32_t remaining = pixel_count % buffer_pixels;
        if (remaining > 0) {
            dma_channel_set_read_addr(dma_chan, dma_fill_buffer, false);
            dma_channel_set_trans_count(dma_chan, remaining * 2, true);
            dma_wait_for_completion();
        }
    } else {

        // Fallback to blocking SPI for small fills or if DMA not available
        for (uint32_t i = 0; i < pixel_count; i++) {
            spi_write_blocking(spi0, color_bytes, 2);
        }
    }
    
    gpio_put(LCD_CS, 1);
}

void st7789_init() {
    // Reset display
    gpio_put(LCD_RST, 0);
    sleep_ms(100);
    gpio_put(LCD_RST, 1);
    sleep_ms(100);
    
    // Init ST7789
    st7789_write_cmd(ST7789_SWRESET);
    sleep_ms(150);
    
    st7789_write_cmd(ST7789_SLPOUT);
    sleep_ms(10);
    
    st7789_write_cmd(ST7789_COLMOD);
    uint8_t colmod = 0x55;
    st7789_write_data_dma(&colmod, 1);
    
    st7789_write_cmd(ST7789_MADCTL);
    uint8_t madctl = 0x00;
    st7789_write_data_dma(&madctl, 1);
    
    st7789_write_cmd(ST7789_INVON);
    st7789_write_cmd(ST7789_DISPON);
    sleep_ms(10);
    
    // Set backlight
    gpio_set_function(LCD_BL, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(LCD_BL);
    pwm_set_wrap(slice_num, 255);
    pwm_set_chan_level(slice_num, PWM_CHAN_A, 128);
    pwm_set_enabled(slice_num, true);
}

// Dirty Region Management
void mark_dirty_region(int x, int y, int w, int h) {
    if (!dirty_region.dirty) {
        dirty_region.min_x = x;
        dirty_region.min_y = y;
        dirty_region.max_x = x + w - 1;
        dirty_region.max_y = y + h - 1;
        dirty_region.dirty = true;
    } else {
        if (x < dirty_region.min_x) dirty_region.min_x = x;
        if (y < dirty_region.min_y) dirty_region.min_y = y;
        if (x + w - 1 > dirty_region.max_x) dirty_region.max_x = x + w - 1;
        if (y + h - 1 > dirty_region.max_y) dirty_region.max_y = y + h - 1;
    }
}

void clear_dirty_region() {
    dirty_region.dirty = false;
}

// Buffer Management
void set_pixel(uint16_t *buffer, int x, int y, uint16_t color) {
    if (x >= 0 && x < GAME_AREA_WIDTH && y >= 0 && y < GAME_AREA_HEIGHT) {
        buffer[y * GAME_AREA_WIDTH + x] = color;
    }
}

// Replace to DMA? 32 bit check?
void fill_rect_buffer(uint16_t *buffer, int x, int y, int w, int h, uint16_t color) {
    for (int dy = 0; dy < h; dy++) {
        for (int dx = 0; dx < w; dx++) {
            set_pixel(buffer, x + dx, y + dy, color);
        }
    }
    mark_dirty_region(x, y, w, h);
}

void draw_block_buffer(uint16_t *buffer, int x, int y, uint16_t color) {
    fill_rect_buffer(buffer, x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1, color);
}

// Game rendering functions (modified for double buffering)
void render_board_to_buffer(uint16_t *buffer) {
    // Clear game area
    fill_rect_buffer(buffer, 0, 0, GAME_AREA_WIDTH, GAME_AREA_HEIGHT, BLACK);
    
    // Draw border
    fill_rect_buffer(buffer, 0, 0, GAME_AREA_WIDTH, 2, WHITE);
    fill_rect_buffer(buffer, 0, GAME_AREA_HEIGHT - 2, GAME_AREA_WIDTH, 2, WHITE);
    fill_rect_buffer(buffer, 0, 0, 2, GAME_AREA_HEIGHT, WHITE);
    fill_rect_buffer(buffer, GAME_AREA_WIDTH - 2, 0, 2, GAME_AREA_HEIGHT, WHITE);
    
    // Draw placed pieces
    for (int y = 0; y < BOARD_HEIGHT; y++) {
        for (int x = 0; x < BOARD_WIDTH; x++) {
            if (board[y][x] != 0) {
                int screen_x = 2 + x * BLOCK_SIZE;
                int screen_y = 2 + y * BLOCK_SIZE;
                draw_block_buffer(buffer, screen_x, screen_y, piece_colors[board[y][x] - 1]);
            }
        }
    }
}

void render_piece_to_buffer(uint16_t *buffer, Piece *piece, uint16_t color) {
    for (int y = 0; y < 4; y++) {
        for (int x = 0; x < 4; x++) {
            if (tetris_pieces[piece->type][piece->rotation][y][x]) {
                int board_x = piece->x + x;
                int board_y = piece->y + y;
                
                // Draw all pieces within board bounds (including partially visible ones)
                if (board_x >= 0 && board_x < BOARD_WIDTH && 
                    board_y >= 0 && board_y < BOARD_HEIGHT) {
                    int screen_x = 2 + board_x * BLOCK_SIZE;
                    int screen_y = 2 + board_y * BLOCK_SIZE;
                    
                    // Bounds check for buffer safety
                    if (screen_x >= 2 && screen_x <= GAME_AREA_WIDTH - BLOCK_SIZE &&
                        screen_y >= 2 && screen_y <= GAME_AREA_HEIGHT - BLOCK_SIZE) {
                        draw_block_buffer(buffer, screen_x, screen_y, color);
                    }
                }
            }
        }
    }
}

bool has_board_changed() {
    return memcmp(board, prev_board, sizeof(board)) != 0;
}

bool has_piece_changed() {
    return memcmp(&current_piece, &prev_piece, sizeof(Piece)) != 0;
}

void update_display() {
    bool board_changed = has_board_changed();
    bool piece_changed = has_piece_changed();
    
    // Force update on first piece or when game state changes significantly
    if (force_full_redraw || board_changed || piece_changed || game_over || need_new_piece) {

        // Clear back buffer completely
        memset(back_buffer, 0, sizeof(back_buffer));
        clear_dirty_region();
        
        // Always render board first
        render_board_to_buffer(back_buffer);
        
        // Then render current piece if game is active
        if (!game_over && current_piece.type >= 0 && current_piece.type < 7) {
            render_piece_to_buffer(back_buffer, &current_piece, piece_colors[current_piece.type]);
        }
        
        // Show game over message
        if (game_over) {

            // Draw game over directly to back buffer
            int msg_x = (GAME_AREA_WIDTH - 80) / 2;  // Center horizontally
            int msg_y = (GAME_AREA_HEIGHT - 40) / 2; // Center vertically
            
            // Game over background
            fill_rect_buffer(back_buffer, msg_x, msg_y, 80, 40, RED);
            fill_rect_buffer(back_buffer, msg_x + 2, msg_y + 2, 76, 36, BLACK);
            
            // Simple "GAME OVER" blocks
            for (int i = 0; i < 10; i++) {
                fill_rect_buffer(back_buffer, msg_x + 10 + i * 6, msg_y + 10, 4, 6, WHITE);
                fill_rect_buffer(back_buffer, msg_x + 10 + i * 6, msg_y + 20, 4, 6, WHITE);
            }
        }
        
        // Copy to front buffer
        memcpy(frame_buffer, back_buffer, sizeof(frame_buffer));
        
        // Always send full game area to display on significant changes
        st7789_write_region_dma(BOARD_OFFSET_X - 2, BOARD_OFFSET_Y - 2, 
                               GAME_AREA_WIDTH, GAME_AREA_HEIGHT, frame_buffer);
        
        // Update comparison state
        memcpy(prev_board, board, sizeof(board));
        prev_piece = current_piece;
        
        force_full_redraw = false;
        clear_dirty_region();
    }
}

// UI functions that don't cause flicker?
void draw_static_ui() {
    static bool ui_initialized = false;
    static int last_score = -1;
    static int last_level = -1;
    static int last_lines = -1;
    static int last_next_piece = -1;
    
    // Init UI area once and force all elements to redraw
    if (!ui_initialized) {

        // Clear entire right side of screen
        st7789_set_window(BOARD_OFFSET_X + GAME_AREA_WIDTH + 5, BOARD_OFFSET_Y, 
                         ST7789_WIDTH - 1, ST7789_HEIGHT - 1);
        st7789_write_cmd(ST7789_RAMWR);
        
        uint8_t black_bytes[2] = {BLACK >> 8, BLACK & 0xFF};
        gpio_put(LCD_DC, 1);
        gpio_put(LCD_CS, 0);
        
        int clear_pixels = (ST7789_WIDTH - (BOARD_OFFSET_X + GAME_AREA_WIDTH + 5)) * 
                          (ST7789_HEIGHT - BOARD_OFFSET_Y);
        for (int i = 0; i < clear_pixels; i++) {
            spi_write_blocking(spi0, black_bytes, 2);
        }
        gpio_put(LCD_CS, 1);
        
        ui_initialized = true;
        // Force all UI elements to redraw ~magic
        last_next_piece = -999;
        last_score = -999;
        last_level = -999;
        last_lines = -999;
    }
    
    // Update next piece display - always when piece type changes or first time
    if (next_piece.type != last_next_piece) {
        int preview_x = BOARD_OFFSET_X + GAME_AREA_WIDTH + 20;
        int preview_y = BOARD_OFFSET_Y + 20;
        
        st7789_set_window(preview_x, preview_y, preview_x + 59, preview_y + 59);
        st7789_write_cmd(ST7789_RAMWR);
        
        uint16_t preview_buffer[60 * 60];
        memset(preview_buffer, 0, sizeof(preview_buffer));
        
        // Draw gray border
        for (int i = 0; i < 60; i++) {
            preview_buffer[i] = GRAY;               // Top
            preview_buffer[(59 * 60) + i] = GRAY;   // Bottom  
            preview_buffer[i * 60] = GRAY;          // Left
            preview_buffer[i * 60 + 59] = GRAY;     // Right
        }
        
        // Draw next piece if valid
        if (next_piece.type >= 0 && next_piece.type < 7) {
            for (int y = 0; y < 4; y++) {
                for (int x = 0; x < 4; x++) {
                    if (tetris_pieces[next_piece.type][0][y][x]) {
                        int px = 15 + x * 10;
                        int py = 15 + y * 10;
                        for (int dy = 0; dy < 8 && (py + dy) < 60; dy++) {
                            for (int dx = 0; dx < 8 && (px + dx) < 60; dx++) {
                                if (px + dx > 0 && py + dy > 0) {
                                    preview_buffer[(py + dy) * 60 + (px + dx)] = piece_colors[next_piece.type];
                                }
                            }
                        }
                    }
                }
            }
        }
        
        prepare_dma_buffer(preview_buffer, 60 * 60);
        st7789_write_data_dma(dma_buffer, 60 * 60 * 2);
        
        last_next_piece = next_piece.type;
    }
    
    // Update score display - always when values change or first time
    if (score != last_score || level != last_level || lines_cleared != last_lines) {
        int info_x = BOARD_OFFSET_X + GAME_AREA_WIDTH + 20;
        int info_y = BOARD_OFFSET_Y + 100;
        
        st7789_set_window(info_x, info_y, info_x + 99, info_y + 99);
        st7789_write_cmd(ST7789_RAMWR);
        
        uint16_t info_buffer[100 * 100];
        memset(info_buffer, 0, sizeof(info_buffer));
        
        // Score bar (vertical, properly clamped) ~do not work out
        int score_height = (score / 100) + 1;
        if (score_height > 50) score_height = 50;
        if (score_height < 1) score_height = 1;
        
        for (int y = (50 - score_height); y < 50 && y < 100; y++) {
            for (int x = 0; x < 10 && x < 100; x++) {
                if (y >= 0) {
                    info_buffer[y * 100 + x] = GREEN;
                }
            }
        }
        
        // Level indicators (horizontal dots, properly clamped) ~do not work 
        int display_level = (level > 10) ? 10 : level;
        for (int i = 0; i < display_level; i++) {
            for (int y = 10; y < 16 && y < 100; y++) {
                for (int x = 20 + i * 8; x < (26 + i * 8) && x < 100; x++) {
                    if (x >= 0 && y >= 0) {
                        info_buffer[y * 100 + x] = YELLOW;
                    }
                }
            }
        }
        
        // Lines cleared bar (horizontal, properly clamped)
        int lines_width = (lines_cleared * 2) % 80;
        if (lines_width > 80) lines_width = 80;
        
        for (int y = 60; y < 68 && y < 100; y++) {
            for (int x = 0; x < lines_width && x < 100; x++) {
                if (x >= 0 && y >= 0) {
                    info_buffer[y * 100 + x] = CYAN;
                }
            }
        }
        
        prepare_dma_buffer(info_buffer, 100 * 100);
        st7789_write_data_dma(dma_buffer, 100 * 100 * 2);
        
        last_score = score;
        last_level = level; 
        last_lines = lines_cleared;
    }
}

// LED Control Functions
void init_led() {
    gpio_set_function(LED_R, GPIO_FUNC_PWM);
    gpio_set_function(LED_G, GPIO_FUNC_PWM);
    gpio_set_function(LED_B, GPIO_FUNC_PWM);
    
    uint slice_r = pwm_gpio_to_slice_num(LED_R);
    uint slice_g = pwm_gpio_to_slice_num(LED_G);
    uint slice_b = pwm_gpio_to_slice_num(LED_B);
    
    pwm_set_wrap(slice_r, 255);
    pwm_set_wrap(slice_g, 255);
    pwm_set_wrap(slice_b, 255);
    
    pwm_set_enabled(slice_r, true);
    pwm_set_enabled(slice_g, true);
    pwm_set_enabled(slice_b, true);
}

void set_led(uint8_t r, uint8_t g, uint8_t b) {
    uint slice_r = pwm_gpio_to_slice_num(LED_R);
    uint slice_g = pwm_gpio_to_slice_num(LED_G);
    uint slice_b = pwm_gpio_to_slice_num(LED_B);
    
    pwm_set_chan_level(slice_r, pwm_gpio_to_channel(LED_R), 255 - r);
    pwm_set_chan_level(slice_g, pwm_gpio_to_channel(LED_G), 255 - g);
    pwm_set_chan_level(slice_b, pwm_gpio_to_channel(LED_B), 255 - b);
}

// Game Functions
void read_buttons() {
    btn_a = !gpio_get(BTN_A);
    btn_b = !gpio_get(BTN_B);
    btn_x = !gpio_get(BTN_X);
    btn_y = !gpio_get(BTN_Y);
}

void init_game() {
    memset(board, 0, sizeof(board));
    memset(prev_board, 0, sizeof(prev_board));
    
    // Reset piece states to invalid values to force redraw
    memset(&current_piece, -1, sizeof(current_piece));
    memset(&prev_piece, -1, sizeof(prev_piece));
    
    score = 0;
    level = 1;
    lines_cleared = 0;
    drop_timer = 0;
    drop_speed = 48;
    game_over = false;
    need_new_piece = true;
    force_full_redraw = true;
    
    // Clear dirty region
    clear_dirty_region();
    
    // Clear the entire screen ONCE at game start
    st7789_clear_screen();
    
    set_led(0, 255, 0);
}

bool is_valid_position(Piece *piece) {
    for (int y = 0; y < 4; y++) {
        for (int x = 0; x < 4; x++) {
            if (tetris_pieces[piece->type][piece->rotation][y][x]) {
                int board_x = piece->x + x;
                int board_y = piece->y + y;
                
                // Check horizontal bounds and bottom boundary
                if (board_x < 0 || board_x >= BOARD_WIDTH || board_y >= BOARD_HEIGHT) {
                    return false;
                }
                
                // Check collision with placed pieces (allow spawning at top)
                if (board_y >= 0 && board[board_y][board_x] != 0) {
                    return false;
                }
            }
        }
    }
    return true;
}

void place_piece(Piece *piece) {
    for (int y = 0; y < 4; y++) {
        for (int x = 0; x < 4; x++) {
            if (tetris_pieces[piece->type][piece->rotation][y][x]) {
                int board_x = piece->x + x;
                int board_y = piece->y + y;
                
                if (board_y >= 0 && board_y < BOARD_HEIGHT && 
                    board_x >= 0 && board_x < BOARD_WIDTH) {
                    board[board_y][board_x] = piece->type + 1;
                }
            }
        }
    }
}

void generate_piece(Piece *piece) {
    piece->x = BOARD_WIDTH / 2 - 2;
    piece->y = 0;  // Start at visible position instead of -1 ~no flicker
    piece->type = rand() % 7;
    piece->rotation = 0;
}

int clear_full_lines() {
    int cleared_lines = 0;
    
    for (int y = BOARD_HEIGHT - 1; y >= 0; y--) {
        bool full_line = true;
        for (int x = 0; x < BOARD_WIDTH; x++) {
            if (board[y][x] == 0) {
                full_line = false;
                break;
            }
        }
        
        if (full_line) {
            for (int move_y = y; move_y > 0; move_y--) {
                for (int x = 0; x < BOARD_WIDTH; x++) {
                    board[move_y][x] = board[move_y - 1][x];
                }
            }
            for (int x = 0; x < BOARD_WIDTH; x++) {
                board[0][x] = 0;
            }
            
            cleared_lines++;
            y++;
        }
    }
    
    return cleared_lines;
}

void update_score(int lines) {
    if (lines > 0) {
        int points[] = {0, 100, 300, 500, 800};
        score += points[lines] * level;
        lines_cleared += lines;
        
        level = 1 + lines_cleared / 10;
        drop_speed = 48 - (level - 1) * 3;
        if (drop_speed < 3) drop_speed = 3;
        
        set_led(0, 0, 255); // Blue for line clear
    }
}

void game_loop() {
    read_buttons();
    
    if (game_over) {
        if (btn_a && !prev_btn_a) {
            init_game();
        }
        set_led(255, 0, 0);
        prev_btn_a = btn_a;
        prev_btn_b = btn_b;
        prev_btn_x = btn_x;
        prev_btn_y = btn_y;
        return;
    }
    
    if (need_new_piece) {
        current_piece = next_piece;
        generate_piece(&next_piece);
        
        if (!is_valid_position(&current_piece)) {
            game_over = true;
            return;
        }
        need_new_piece = false;
    }
    
    Piece test_piece = current_piece;
    
    // Move left (Y button) - only if X is not pressed
    if (btn_y && !prev_btn_y && !(btn_x && btn_y)) {
        test_piece.x--;
        if (is_valid_position(&test_piece)) {
            current_piece = test_piece;
        }
    }
    
    // Move right (X button) - only if Y is not pressed
    if (btn_x && !prev_btn_x && !(btn_x && btn_y)) {
        test_piece = current_piece;
        test_piece.x++;
        if (is_valid_position(&test_piece)) {
            current_piece = test_piece;
        }
    }
    
    // Rotate (Y + X buttons pressed together)
    if (btn_y && btn_x && (!prev_btn_y || !prev_btn_x)) {
        test_piece = current_piece;
        test_piece.rotation = (test_piece.rotation + 1) % 4;
        if (is_valid_position(&test_piece)) {
            current_piece = test_piece;
        }
    }
    
    // Soft drop (A button)
    bool soft_drop = btn_a;
    
    // Hard drop (B button)
    if (btn_b && !prev_btn_b) {
        while (true) {
            test_piece = current_piece;
            test_piece.y++;
            if (is_valid_position(&test_piece)) {
                current_piece = test_piece;
                score += 2; // Bonus for hard drop
            } else {
                break;
            }
        }
        drop_timer = drop_speed; // Force immediate placement
    }
    
    // Handle piece dropping
    drop_timer++;
    if (drop_timer >= drop_speed || soft_drop) {
        test_piece = current_piece;
        test_piece.y++;
        
        if (is_valid_position(&test_piece)) {
            current_piece = test_piece;
            if (soft_drop) score += 1;
        } else {
            place_piece(&current_piece);
            int cleared = clear_full_lines();
            update_score(cleared);
            need_new_piece = true;
        }
        drop_timer = 0;
    }
    
    prev_btn_a = btn_a;
    prev_btn_b = btn_b;
    prev_btn_x = btn_x;
    prev_btn_y = btn_y;
    
    if (!game_over) {
        uint16_t piece_color = piece_colors[current_piece.type];
        uint8_t r = (piece_color >> 11) << 3;
        uint8_t g = ((piece_color >> 5) & 0x3F) << 2;
        uint8_t b = (piece_color & 0x1F) << 3;
        set_led(r/4, g/4, b/4);
    }
}

int main() {
    stdio_init_all();
    
    // Init hardware
    spi_init(spi0, 40000000);
    gpio_set_function(LCD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(LCD_MOSI, GPIO_FUNC_SPI);
    
    gpio_init(LCD_DC);
    gpio_init(LCD_CS);
    gpio_init(LCD_RST);
    gpio_set_dir(LCD_DC, GPIO_OUT);
    gpio_set_dir(LCD_CS, GPIO_OUT);
    gpio_set_dir(LCD_RST, GPIO_OUT);
    
    gpio_init(BTN_A);
    gpio_init(BTN_B);
    gpio_init(BTN_X);
    gpio_init(BTN_Y);
    gpio_set_dir(BTN_A, GPIO_IN);
    gpio_set_dir(BTN_B, GPIO_IN);
    gpio_set_dir(BTN_X, GPIO_IN);
    gpio_set_dir(BTN_Y, GPIO_IN);
    gpio_pull_up(BTN_A);
    gpio_pull_up(BTN_B);
    gpio_pull_up(BTN_X);
    gpio_pull_up(BTN_Y);
    
    gpio_put(LCD_CS, 1);
    
    // Init DMA, display and LED
    init_dma();
    st7789_init();
    init_led();
    
    srand(time(NULL));
    
    generate_piece(&next_piece);
    init_game();
    
    printf("Tetris game started!\n");
    printf("Controls: Y=Left, X=Right, Y+X=Rotate, A=Soft Drop, B=Hard Drop\n");
    printf("Game Over: A=Restart\n");
    printf("Features: DMA transfers, double buffering, dirty region updates\n");
    
    while (true) {
        game_loop();
        update_display();    // Only updates changed regions
        draw_static_ui();    // Only updates when UI elements change
        sleep_ms(16);        // ~60 FPS
    }
    
    return 0;
}
