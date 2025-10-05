#include <stdio.h>
#include "pico/stdlib.h"
#include "displaybw.h"
#include "horse.h"


// Function to create a centered 320x240 buffer from 240x240 image
void create_centered_buffer(const uint8_t *img_240x240, uint8_t *buf_320x240) {
    // Clear the entire buffer (white background)
    for (int i = 0; i < (320 * 240) / 8; i++) {
        buf_320x240[i] = 0xFF;
    }
    
    // Center horizontally: (320 - 240) / 2 = 40 pixels offset
    const int x_offset = 40;
    const int img_width = 240;
    const int img_height = 240;
    
    // Copy image data row by row
    for (int y = 0; y < img_height; y++) {
        // Source: 240x240 image, 30 bytes per row (240/8)
        const uint8_t *src_row = img_240x240 + (y * (img_width / 8));
        
        // Destination: 320x240 buffer, 40 bytes per row (320/8)
        uint8_t *dst_row = buf_320x240 + (y * (320 / 8));
        
        // Calculate byte offset for 40 pixel shift
        int byte_offset = x_offset / 8;  // 40/8 = 5 bytes
        int bit_offset = x_offset % 8;   // 40%8 = 0 bits
        
        if (bit_offset == 0) {
            // Perfect byte alignment - direct copy
            for (int x = 0; x < img_width / 8; x++) {
                dst_row[byte_offset + x] = src_row[x];
            }
        } else {
            // Need to shift bits (shouldn't happen with 40px offset, but here for completeness)
            for (int x = 0; x < img_width / 8; x++) {
                uint8_t byte = src_row[x];
                dst_row[byte_offset + x] |= (byte >> bit_offset);
                if (byte_offset + x + 1 < 320 / 8) {
                    dst_row[byte_offset + x + 1] |= (byte << (8 - bit_offset));
                }
            }
        }
    }
}


int main() {
    // Init stdio
    stdio_init_all();

    // Small delay for USB serial to stabilize
    sleep_ms(1000);

    printf("Display BW Test: Centered 240x240 Horse Image\n");

    // Init display
    display_error_t err = display_pack_init();
    if (err != DISPLAY_OK) {
        printf("Display init failed: %s\n", display_error_string(err));
        return 1;
    }
    printf("Display init successfully\n");

    // Init buttons
    err = buttons_init();
    if (err != DISPLAY_OK) {
        printf("Button init failed: %s\n", display_error_string(err));
    }

    // Allocate buffer for 320x240 (9600 bytes)
    static uint8_t centered_buffer[320 * 240 / 8];

    // Create centered image
    printf("Creating centered image buffer..\n");
    create_centered_buffer(horse_data, centered_buffer);

    // Clear display to white
    printf("Clearing display..\n");
    display_clear(true);
    sleep_ms(500);

    // Display the centered image
    printf("Displaying centered horse image..\n");
    err = display_blit_full_bw(centered_buffer);
    if (err != DISPLAY_OK) {
        printf("Blit failed: %s\n", display_error_string(err));
        return 1;
    }

    printf("Image displayed successfully!\n");
    printf("Press BUTTON_A to refresh display\n");
    printf("Press BUTTON_B to clear display\n");

    // Main loop
    while (true) {
        buttons_update();

        if (button_just_pressed(BUTTON_A)) {
            printf("Refreshing display..\n");
            display_blit_full_bw(centered_buffer);
        }

        if (button_just_pressed(BUTTON_B)) {
            printf("Clearing display..\n");
            display_clear(true);
        }

        if (button_just_pressed(BUTTON_X)) {
            printf("Redisplaying image..\n");
            display_blit_full_bw(centered_buffer);
        }

        if (button_just_pressed(BUTTON_Y)) {
            printf("Inverting: showing original (non-centered)..\n");
            display_blit_full_bw(horse_data);
            sleep_ms(2000);
            printf("Showing centered version again..\n");
            display_blit_full_bw(centered_buffer);
        }

        sleep_ms(10);
    }

    return 0;
}

