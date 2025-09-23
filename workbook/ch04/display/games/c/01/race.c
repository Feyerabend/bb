#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"

// Display Pack 2.0 Pin Definitions
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
#define ST7789_WIDTH  240
#define ST7789_HEIGHT 240
#define ST7789_ROTATION 2

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

// Colors (RGB565)
#define BLACK   0x0000
#define GREEN   0x07E0
#define WHITE   0xFFFF

// Game constants
#define SCREEN_SIZE 240
#define MAP_SCALE 40
#define OFFSET_X 10
#define OFFSET_Y 30

// Game state
int theta = 0;
int x = 70;
int y = 70;
int speed_x = 0;
int speed_y = 0;

// Previous car position for dirty region tracking
int prev_car_x = 70;
int prev_car_y = 70;
int prev_theta = 0;

// Track dirty flag
bool track_dirty = true;

// Button sensitivity controls
int steering_counter = 0;
int accel_counter = 0;
int brake_counter = 0;

#define STEERING_RATE 3  // Frames between steering changes
#define ACCEL_RATE 2     // Frames between acceleration increments
#define BRAKE_RATE 1     // Frames between brake applications

// Map data (same as JavaScript from Mitxela)
int map[5][6] = {
    {2,1,2,5,5,1},
    {6,6,6,2,1,6},
    {6,6,6,6,3,4},
    {6,3,4,3,5,1},
    {3,5,5,5,5,4}
};

// Sin/Cos lookup tables for performance, usual in game programming
int sin_table[256];
int cos_table[256];

// Button states
bool btn_a = false, btn_b = false, btn_x = false, btn_y = false;
bool prev_btn_x = false; // For reset detection

// ST7789 Functions
void st7789_write_cmd(uint8_t cmd) {
    gpio_put(LCD_DC, 0);
    gpio_put(LCD_CS, 0);
    spi_write_blocking(spi0, &cmd, 1);
    gpio_put(LCD_CS, 1);
}

void st7789_write_data(uint8_t *data, size_t len) {
    gpio_put(LCD_DC, 1);
    gpio_put(LCD_CS, 0);
    spi_write_blocking(spi0, data, len);
    gpio_put(LCD_CS, 1);
}

void st7789_write_data_byte(uint8_t data) {
    st7789_write_data(&data, 1);
}

void st7789_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    uint8_t data[4];
    
    st7789_write_cmd(ST7789_CASET);
    data[0] = x0 >> 8;
    data[1] = x0 & 0xFF;
    data[2] = x1 >> 8;
    data[3] = x1 & 0xFF;
    st7789_write_data(data, 4);
    
    st7789_write_cmd(ST7789_RASET);
    data[0] = y0 >> 8;
    data[1] = y0 & 0xFF;
    data[2] = y1 >> 8;
    data[3] = y1 & 0xFF;
    st7789_write_data(data, 4);
}

void st7789_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
    st7789_set_window(x, y, x + w - 1, y + h - 1);
    st7789_write_cmd(ST7789_RAMWR);
    
    uint8_t color_bytes[2] = {color >> 8, color & 0xFF};
    gpio_put(LCD_DC, 1);
    gpio_put(LCD_CS, 0);
    
    for (int i = 0; i < w * h; i++) {
        spi_write_blocking(spi0, color_bytes, 2);
    }
    gpio_put(LCD_CS, 1);
}

void st7789_draw_pixel(uint16_t x, uint16_t y, uint16_t color) {
    if (x >= ST7789_WIDTH || y >= ST7789_HEIGHT) return;
    st7789_fill_rect(x, y, 1, 1, color);
}

void st7789_draw_line(int x0, int y0, int x1, int y1, uint16_t color) {
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = x0 < x1 ? 1 : -1;
    int sy = y0 < y1 ? 1 : -1;
    int err = dx - dy;
    
    while (true) {
        st7789_draw_pixel(x0, y0, color);
        if (x0 == x1 && y0 == y1) break;
        
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
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
    st7789_write_data_byte(0x55); // 16-bit color
    
    st7789_write_cmd(ST7789_MADCTL);
    st7789_write_data_byte(0x00);
    
    st7789_write_cmd(ST7789_INVON);
    
    st7789_write_cmd(ST7789_DISPON);
    sleep_ms(10);
    
    // Set backlight
    gpio_set_function(LCD_BL, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(LCD_BL);
    pwm_set_wrap(slice_num, 255);
    pwm_set_chan_level(slice_num, PWM_CHAN_A, 128); // 50% brightness
    pwm_set_enabled(slice_num, true);
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

// Math functions
int my_sin(int angle) {
    return sin_table[angle & 0xFF];
}

int my_cos(int angle) {
    return cos_table[angle & 0xFF];
}

void init_trig_tables() {
    for (int i = 0; i < 256; i++) {
        sin_table[i] = (int)(sin(2.0 * M_PI * i / 256.0) * 127.0);
        cos_table[i] = (int)(cos(2.0 * M_PI * i / 256.0) * 127.0);
    }
}

// Game functions
void read_buttons() {
    btn_a = !gpio_get(BTN_A);
    btn_b = !gpio_get(BTN_B);
    btn_x = !gpio_get(BTN_X);
    btn_y = !gpio_get(BTN_Y);
}

void reset_game() {
    x = 70;
    y = 70;
    theta = 0;
    speed_x = 0;
    speed_y = 0;
    track_dirty = true;
    
    // Reset counters
    steering_counter = 0;
    accel_counter = 0;
    brake_counter = 0;
    
    set_led(0, 0, 0); // Turn off LED
}

void update_led() {
    int total_speed = abs(speed_x) + abs(speed_y);
    
    if (btn_a && btn_b) { // Accelerating
        int intensity = (total_speed > 255) ? 255 : total_speed;
        set_led(0, intensity, 0); // Green with intensity based on speed
    } else if (btn_y) { // Braking
        int intensity = (total_speed > 255) ? 255 : total_speed;
        set_led(intensity, 0, 0); // Red with intensity based on speed
    } else {
        // Gradually fade based on current speed
        int intensity = (total_speed > 255) ? 255 : total_speed;
        intensity = intensity / 4; // Dimmer when coasting
        set_led(0, intensity / 2, 0); // Dim green when coasting
    }
}

void apply_friction() {
    speed_x -= (speed_x >> 4);
    speed_y -= (speed_y >> 4);
}

void collide_corner(int x1, int y1) {
    int dist, i = 10, r = 32;
    
    while (i-- > 0) {
        dist = (x - x1) * (x - x1) + (y - y1) * (y - y1);
        if (dist <= r * r) break;
        x -= (x - x1) / r;
        y -= (y - y1) / r;
        apply_friction();
    }
    
    i = 10;
    r = 8;
    while (i-- > 0) {
        dist = (x - x1) * (x - x1) + (y - y1) * (y - y1);
        if (dist >= r * r) break;
        x += (x - x1) / r;
        y += (y - y1) / r;
        apply_friction();
    }
}

void collide_vert(int x1, int y1, int s) {
    int i = 10;
    while (x < x1 + 8 && i-- > 0) {
        x++;
        apply_friction();
    }
    i = 10;
    while (x > x1 + s - 8 && i-- > 0) {
        x--;
        apply_friction();
    }
}

void collide_horiz(int x1, int y1, int s) {
    int i = 10;
    while (y < y1 + 8 && i-- > 0) {
        y++;
        apply_friction();
    }
    i = 10;
    while (y > y1 + s - 8 && i-- > 0) {
        y--;
        apply_friction();
    }
}

void draw_horiz(int px, int py, int s) {
    st7789_draw_line(px, py + 4, px + s, py + 4, GREEN);
    st7789_draw_line(px, py + s - 4, px + s, py + s - 4, GREEN);
}

void draw_vert(int px, int py, int s) {
    st7789_draw_line(px + s - 4, py, px + s - 4, py + s, GREEN);
    st7789_draw_line(px + 4, py, px + 4, py + s, GREEN);
}

void draw_curve(int px, int py, int r, int quadrant) {
    int cx = px, cy = py;
    
    if (quadrant == 1) cy += r;
    if (quadrant == 2) { cx += r; cy += r; }
    if (quadrant == 3) cx += r;
    
    // Draw curve approximation with lines
    int start_angle = -quadrant * 64;
    int end_angle = (1 - quadrant) * 64;
    
    for (int a = start_angle; a < end_angle; a += 2) {
        int x1 = cx + ((r - 4) * my_cos(a)) / 127;
        int y1 = cy + ((r - 4) * my_sin(a)) / 127;
        int x2 = cx + ((r - 4) * my_cos(a + 2)) / 127;
        int y2 = cy + ((r - 4) * my_sin(a + 2)) / 127;
        st7789_draw_line(x1, y1, x2, y2, GREEN);
        
        x1 = cx + (4 * my_cos(a)) / 127;
        y1 = cy + (4 * my_sin(a)) / 127;
        x2 = cx + (4 * my_cos(a + 2)) / 127;
        y2 = cy + (4 * my_sin(a + 2)) / 127;
        st7789_draw_line(x1, y1, x2, y2, GREEN);
    }
}

void draw_car() {
    // Clear previous car position and redraw any road underneath
    if (!track_dirty) {
        int prev_costheta = my_cos(prev_theta) / 20;
        int prev_sintheta = my_sin(prev_theta) / 20;
        int prev_halfcos = prev_costheta / 2;
        int prev_halfsin = prev_sintheta / 2;
        
        int prev_car_px = prev_car_x + OFFSET_X;
        int prev_car_py = prev_car_y + OFFSET_Y;
        
        int px1 = prev_car_px + prev_halfcos + prev_halfsin;
        int py1 = prev_car_py + prev_halfsin - prev_halfcos;
        int px2 = prev_car_px - prev_costheta + prev_halfsin;
        int py2 = prev_car_py - prev_sintheta - prev_halfcos;
        int px3 = prev_car_px - prev_costheta - prev_halfsin;
        int py3 = prev_car_py - prev_sintheta + prev_halfcos;
        int px4 = prev_car_px + prev_halfcos - prev_halfsin;
        int py4 = prev_car_py + prev_halfsin + prev_halfcos;
        
        // Draw over previous car with black
        st7789_draw_line(px1, py1, px2, py2, BLACK);
        st7789_draw_line(px2, py2, px3, py3, BLACK);
        st7789_draw_line(px3, py3, px4, py4, BLACK);
        st7789_draw_line(px4, py4, px1, py1, BLACK);
        
        // Redraw road elements that might be under the previous car position
        // Check which map cells the previous car was overlapping
        int prev_grid_x = (prev_car_x - OFFSET_X) / MAP_SCALE;
        int prev_grid_y = (prev_car_y - OFFSET_Y) / MAP_SCALE;
        
        // Redraw the current cell and adjacent cells to handle car spanning multiple cells
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                int grid_x = prev_grid_x + dx;
                int grid_y = prev_grid_y + dy;
                
                if (grid_x >= 0 && grid_x < 6 && grid_y >= 0 && grid_y < 5) {
                    int map_value = map[grid_y][grid_x];
                    if (map_value < 5) {
                        draw_curve(OFFSET_X + grid_x * MAP_SCALE, OFFSET_Y + grid_y * MAP_SCALE, MAP_SCALE, map_value);
                    } else if (map_value == 5) {
                        draw_horiz(OFFSET_X + grid_x * MAP_SCALE, OFFSET_Y + grid_y * MAP_SCALE, MAP_SCALE);
                    } else if (map_value == 6) {
                        draw_vert(OFFSET_X + grid_x * MAP_SCALE, OFFSET_Y + grid_y * MAP_SCALE, MAP_SCALE);
                    }
                }
            }
        }
    }
    
    // Draw current car
    int costheta = my_cos(theta) / 20;
    int sintheta = my_sin(theta) / 20;
    int halfcos = costheta / 2;
    int halfsin = sintheta / 2;
    
    int car_x = x + OFFSET_X;
    int car_y = y + OFFSET_Y;
    
    int x1 = car_x + halfcos + halfsin;
    int y1 = car_y + halfsin - halfcos;
    int x2 = car_x - costheta + halfsin;
    int y2 = car_y - sintheta - halfcos;
    int x3 = car_x - costheta - halfsin;
    int y3 = car_y - sintheta + halfcos;
    int x4 = car_x + halfcos - halfsin;
    int y4 = car_y + halfsin + halfcos;
    
    st7789_draw_line(x1, y1, x2, y2, GREEN);
    st7789_draw_line(x2, y2, x3, y3, GREEN);
    st7789_draw_line(x3, y3, x4, y4, GREEN);
    st7789_draw_line(x4, y4, x1, y1, GREEN);
    
    // Store current position for next frame
    prev_car_x = x;
    prev_car_y = y;
    prev_theta = theta;
}

void draw_track() {
    for (int j = 0; j < 5; j++) {
        for (int i = 0; i < 6; i++) {
            // Draw track elements
            if (map[j][i] < 5) {
                draw_curve(OFFSET_X + i * MAP_SCALE, OFFSET_Y + j * MAP_SCALE, MAP_SCALE, map[j][i]);
            } else if (map[j][i] == 5) {
                draw_horiz(OFFSET_X + i * MAP_SCALE, OFFSET_Y + j * MAP_SCALE, MAP_SCALE);
            } else if (map[j][i] == 6) {
                draw_vert(OFFSET_X + i * MAP_SCALE, OFFSET_Y + j * MAP_SCALE, MAP_SCALE);
            }
        }
    }
}

void game_loop() {
    // Handle reset button
    if (btn_x && !prev_btn_x) {
        reset_game();
    }
    prev_btn_x = btn_x;
    
    // Clear screen only when needed
    if (track_dirty) {
        st7789_fill_rect(0, 0, ST7789_WIDTH, ST7789_HEIGHT, BLACK);
        draw_track();
        track_dirty = false;
    }
    
    // Update player rotation - A=left, B=right
    if (btn_a && !btn_b) {
        theta = (theta - 2 + 256) % 256;
    } else if (btn_b && !btn_a) {
        theta = (theta + 2) % 256;
    }
    
    // Acceleration - both A and B pressed
    if (btn_a && btn_b) {
        speed_x += my_cos(theta) / 8;
        speed_y += my_sin(theta) / 8;
    }
    
    // Braking with Y
    if (btn_y) {
        apply_friction();
    }
    
    // Update position
    x = (256 + x + speed_x / 256) % 256;
    y = (256 + y + speed_y / 256) % 256;
    
    // The car gets stuck, so we have to fix this
    // Collision detection
    for (int j = 0; j < 5; j++) {
        for (int i = 0; i < 6; i++) {
            if (x >= i * MAP_SCALE && y >= j * MAP_SCALE && 
                x < (i + 1) * MAP_SCALE && y < (j + 1) * MAP_SCALE) {
                
                switch (map[j][i]) {
                    case 1: collide_corner(i * MAP_SCALE, (j + 1) * MAP_SCALE); break;
                    case 2: collide_corner((i + 1) * MAP_SCALE, (j + 1) * MAP_SCALE); break;
                    case 3: collide_corner((i + 1) * MAP_SCALE, j * MAP_SCALE); break;
                    case 4: collide_corner(i * MAP_SCALE, j * MAP_SCALE); break;
                    case 5: collide_horiz(i * MAP_SCALE, j * MAP_SCALE, MAP_SCALE); break;
                    case 6: collide_vert(i * MAP_SCALE, j * MAP_SCALE, MAP_SCALE); break;
                }
            }
        }
    }
    
    // Update LED based on current state
    update_led();
    
    // Draw car (with dirty region optimisation)
    draw_car();
}

int main() {
    stdio_init_all();
    
    // Init SPI for display
    spi_init(spi0, 32000000); // 32MHz
    gpio_set_function(LCD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(LCD_MOSI, GPIO_FUNC_SPI);
    
    // Init GPIO pins
    gpio_init(LCD_DC);
    gpio_init(LCD_CS);
    gpio_init(LCD_RST);
    gpio_set_dir(LCD_DC, GPIO_OUT);
    gpio_set_dir(LCD_CS, GPIO_OUT);
    gpio_set_dir(LCD_RST, GPIO_OUT);
    
    // Init button pins
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
    
    // Init lookup tables, LED, and display
    init_trig_tables();
    init_led();
    st7789_init();
    
    printf("Racing game started!\n");
    printf("Controls: A=Left, B=Right, A+B=Accelerate, Y=Brake, X=Reset\n");
    
    while (true) {
        read_buttons();
        game_loop();
        sleep_ms(16); // ~60 FPS
    }
    
    return 0;
}
