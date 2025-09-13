#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "drivers/st7789/st7789.hpp"
#include "libraries/pico_graphics/pico_graphics.hpp"
#include "libraries/pico_display_2/pico_display_2.hpp"


using namespace pimoroni;


// Create display and graphics objects
ST7789 st7789(320, 240, ROTATE_0, false, get_spi_pins(BG_SPI_FRONT));
PicoGraphics_PenRGB565 graphics(st7789.width, st7789.height, nullptr);

PicoDisplay2 pico_display;


int main() {
    stdio_init_all();
    
    // Initialize the display
    st7789.set_backlight(255);  // Full brightness
    
    // Create some colors
    Pen BLACK = graphics.create_pen(0, 0, 0);
    Pen WHITE = graphics.create_pen(255, 255, 255);
    Pen RED = graphics.create_pen(255, 0, 0);
    Pen GREEN = graphics.create_pen(0, 255, 0);
    Pen BLUE = graphics.create_pen(0, 0, 255);
    Pen YELLOW = graphics.create_pen(255, 255, 0);
    Pen CYAN = graphics.create_pen(0, 255, 255);
    Pen MAGENTA = graphics.create_pen(255, 0, 255);
    
    // Animation variables
    int frame = 0;
    float time = 0.0f;
    
    printf("Pimoroni Pico Display Pack 2.0 Example Started!\n");
    
    while (true) {
        // Clear screen
        graphics.set_pen(BLACK);
        graphics.clear();
        
        // Title
        graphics.set_pen(WHITE);
        graphics.text("Pimoroni Display Pack 2.0", Point(10, 10), 320);
        
        // Show button states
        graphics.set_pen(pico_display.is_pressed(PicoDisplay2::A) ? RED : WHITE);
        graphics.text("A", Point(10, 40), 320);
        
        graphics.set_pen(pico_display.is_pressed(PicoDisplay2::B) ? GREEN : WHITE);
        graphics.text("B", Point(30, 40), 320);
        
        graphics.set_pen(pico_display.is_pressed(PicoDisplay2::X) ? BLUE : WHITE);
        graphics.text("X", Point(50, 40), 320);
        
        graphics.set_pen(pico_display.is_pressed(PicoDisplay2::Y) ? YELLOW : WHITE);
        graphics.text("Y", Point(70, 40), 320);
        
        // Draw some animated graphics
        
        // Bouncing rectangle
        int rect_x = (int)(160 + 100 * sin(time * 2.0f));
        graphics.set_pen(RED);
        graphics.rectangle(Rect(rect_x, 70, 40, 30));
        
        // Rotating circle
        int circle_x = (int)(160 + 80 * cos(time));
        int circle_y = (int)(120 + 40 * sin(time * 1.5f));
        graphics.set_pen(GREEN);
        graphics.circle(Point(circle_x, circle_y), 20);
        
        // Color bars
        for (int i = 0; i < 8; i++) {
            Pen color;
            switch (i) {
                case 0: color = RED; break;
                case 1: color = GREEN; break;
                case 2: color = BLUE; break;
                case 3: color = YELLOW; break;
                case 4: color = CYAN; break;
                case 5: color = MAGENTA; break;
                case 6: color = WHITE; break;
                default: color = BLACK; break;
            }
            graphics.set_pen(color);
            graphics.rectangle(Rect(i * 40, 180, 35, 20));
        }
        
        // Frame counter
        graphics.set_pen(WHITE);
        char frame_text[32];
        sprintf(frame_text, "Frame: %d", frame);
        graphics.text(frame_text, Point(10, 210), 320);
        
        // Instructions
        graphics.set_pen(CYAN);
        graphics.text("Press buttons to see colors!", Point(10, 60), 320);
        
        // Update the display
        st7789.update(&graphics);
        
        // Button actions
        if (pico_display.is_pressed(PicoDisplay2::A)) {
            // Fill screen with red
            graphics.set_pen(RED);
            graphics.clear();
            graphics.set_pen(WHITE);
            graphics.text("Button A Pressed!", Point(50, 100), 320);
            st7789.update(&graphics);
            sleep_ms(200);
        }
        
        if (pico_display.is_pressed(PicoDisplay2::B)) {
            // Fill screen with green
            graphics.set_pen(GREEN);
            graphics.clear();
            graphics.set_pen(WHITE);
            graphics.text("Button B Pressed!", Point(50, 100), 320);
            st7789.update(&graphics);
            sleep_ms(200);
        }
        
        if (pico_display.is_pressed(PicoDisplay2::X)) {
            // Fill screen with blue
            graphics.set_pen(BLUE);
            graphics.clear();
            graphics.set_pen(WHITE);
            graphics.text("Button X Pressed!", Point(50, 100), 320);
            st7789.update(&graphics);
            sleep_ms(200);
        }
        
        if (pico_display.is_pressed(PicoDisplay2::Y)) {
            // Fill screen with yellow
            graphics.set_pen(YELLOW);
            graphics.clear();
            graphics.set_pen(BLACK);
            graphics.text("Button Y Pressed!", Point(50, 100), 320);
            st7789.update(&graphics);
            sleep_ms(200);
        }
        
        // Update animation
        frame++;
        time += 0.05f;
        
        sleep_ms(50);
    }
    
    return 0;
}

