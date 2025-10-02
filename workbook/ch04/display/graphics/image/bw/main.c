#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "pico/sem.h"
#include "hardware/spi.h"
#include "hardware/dma.h"
#include "sd_card.h"
#include "ff.h"
#include "displaybw.h"
#include <string.h>
#include <stdio.h>  // For sprintf

// SD card SPI pins (SPI1) --> check!
#define SD_SPI spi1
#define SD_SCK_PIN 10
#define SD_MOSI_PIN 11
#define SD_MISO_PIN 8
#define SD_CS_PIN 9

// 1-bit frame size (9.6 KB)
#define BIT_FRAME_SIZE (DISPLAY_WIDTH * DISPLAY_HEIGHT / 8)  // 9600 bytes

// BMP offset for 1-bit data (54 header + 8 palette)
#define BMP_PIXEL_OFFSET 62

// Buffers and sync
uint8_t bit_buffer_a[BIT_FRAME_SIZE];
uint8_t bit_buffer_b[BIT_FRAME_SIZE];
volatile bool buffer_ready = false;
sem_t buffer_sem;

// Fast BMP load: Seek to pixel data, read directly
bool load_bw_bmp(const char *filename, uint8_t *buffer) {
    FIL fil;
    FRESULT fr;
    UINT br;

    fr = f_open(&fil, filename, FA_READ);
    if (fr != FR_OK) return false;

    // Seek to pixel data
    fr = f_lseek(&fil, BMP_PIXEL_OFFSET);
    if (fr != FR_OK) {
        f_close(&fil);
        return false;
    }

    // Read 1-bit pixels
    fr = f_read(&fil, buffer, BIT_FRAME_SIZE, &br);
    f_close(&fil);
    if (fr != FR_OK || br != BIT_FRAME_SIZE) return false;

    return true;
}

// Core 1: Display task
void core1_display_task() {
    // Init display
    if (display_pack_init() != DISPLAY_OK) {
        while (true) tight_loop_contents();
    }
    display_set_backlight(true);

    while (true) {
        // Wait for buffer ready
        sem_acquire_blocking(&buffer_sem);

        // Blit using driver (expands and DMAs internally)
        display_blit_full_bw(bit_buffer_a);
        display_wait_for_dma();

        // Signal Core 0
        buffer_ready = true;
    }
}

// Core 0: SD loader
int main() {
    stdio_init_all();

    // Init SD SPI
    spi_init(SD_SPI, 25000000);  // 25 MHz
    gpio_set_function(SD_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SD_MOSI_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SD_MISO_PIN, GPIO_FUNC_SPI);
    gpio_init(SD_CS_PIN);
    gpio_set_dir(SD_CS_PIN, GPIO_OUT);
    gpio_put(SD_CS_PIN, 1);

    // Mount SD
    FATFS fs;
    FRESULT fr = f_mount(&fs, "", 1);
    if (fr != FR_OK) {
        printf("SD mount failed: %d\n", fr);
        while (true) tight_loop_contents();
    }

    // Start Core 1
    sem_init(&buffer_sem, 0, 1);
    multicore_launch_core1(core1_display_task);

    // List BMP files in /images/ using f_findfirst/next
    char *bmp_files[1000];  // Max 1000 files ~ but we actually have more.. cache in separate SD
    int num_files = 0;
    FILINFO fno;
    fr = f_findfirst(&fno, "/images", "*.bmp");
    while (fr == FR_OK && fno.fname[0] && num_files < 1000) {
        bmp_files[num_files] = malloc(strlen(fno.fname) + 10);
        sprintf(bmp_files[num_files], "/images/%s", fno.fname);
        num_files++;
        fr = f_findnext(&fno);
    }

    if (num_files == 0) {
        printf("No BMP files found\n");
        while (true) tight_loop_contents();
    }

    // Main loop
    int current_file = 0;
    uint8_t *current_bit_buffer = bit_buffer_b;
    while (true) {
        // Load next BMP into inactive buffer
        if (load_bw_bmp(bmp_files[current_file], current_bit_buffer)) {
            // Wait for display to finish
            while (!buffer_ready) tight_loop_contents();
            buffer_ready = false;

            // Swap buffers
            bit_buffer_a = current_bit_buffer;
            current_bit_buffer = (current_bit_buffer == bit_buffer_b) ? bit_buffer_a : bit_buffer_b;

            // Signal Core 1
            sem_release(&buffer_sem);
        }

        current_file = (current_file + 1) % num_files;
        sleep_ms(33);  // ~30 FPS
    }
}

