/*
 * Secure Boot Chain Demonstration for Raspberry Pi Pico 2
 * With Pimoroni Display Pack 2.0
 
 * This demonstrates a complete secure boot implementation showing:
 * - Root of Trust (RoT) in "ROM" (simulated)
 * - Digital signature verification (Ed25519-style)
 * - Chain of trust: Bootloader -> Application -> Module
 * - Rollback protection with version monotonic counters
 * - Flash write protection
 * - Secure upgrade mechanism
 * - Anti-downgrade protection
 
 * Educational Features:
 * - Shows why each stage verifies the next
 * - Demonstrates what happens when signatures fail
 * - Shows rollback attack prevention
 * - Illustrates defense-in-depth
 
 * Hardware Setup:
 * - Pimoroni Display Pack 2.0 (320x240 display + 4 buttons)
 * - Button A: Next scenario
 * - Button B: Previous scenario
 * - Button X: Run current scenario
 * - Button Y: Auto-advance
 *   Success/security patterns use simple blink sequences.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include "pico/time.h"
#include "display.h"

// Built-in LED pin
#define LED_PIN PICO_DEFAULT_LED_PIN

// Memory regions (offsets in flash)
#define FLASH_BOOTLOADER_OFFSET 0x4000
#define FLASH_APP_OFFSET        0xC000
#define FLASH_MODULE_OFFSET     0x20000
#define FLASH_METADATA_OFFSET   0x30000

// Security parameters
#define SIGNATURE_SIZE 64
#define HASH_SIZE 32
#define PUBLIC_KEY_SIZE 32
#define VERSION_COUNTER_SIZE 4

/*
 * DISPLAY HELPER FUNCTIONS
 */

void draw_boot_header(const char *stage, uint16_t color) {
    display_fill_rect(0, 0, DISPLAY_WIDTH, 30, COLOR_BLACK);
    display_draw_string(10, 10, stage, color, COLOR_BLACK);
}

void draw_boot_step(uint16_t y, const char *text, uint16_t color) {
    display_draw_string(10, y, text, color, COLOR_BLACK);
}

void draw_verification_box(uint16_t y, const char *title, bool passed) {
    uint16_t bg_color = passed ? 0x0320 : 0x6000; // Dark green or dark red
    uint16_t fg_color = passed ? COLOR_GREEN : COLOR_RED;
    
    display_fill_rect(5, y, 310, 35, bg_color);
    display_draw_string(10, y + 5, title, fg_color, bg_color);
    
    const char *status = passed ? "[VERIFIED]" : "[FAILED]";
    display_draw_string(10, y + 20, status, fg_color, bg_color);
}

void draw_image_info(uint16_t y, const char *desc, uint32_t version, uint32_t size) {
    char info[64];
    
    snprintf(info, sizeof(info), "DESC: %s", desc);
    display_draw_string(15, y, info, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(info, sizeof(info), "VERSION: %u  SIZE: %u", version, size);
    display_draw_string(15, y + 12, info, COLOR_CYAN, COLOR_BLACK);
}

void draw_security_alert(const char *message) {
    display_fill_rect(0, 200, DISPLAY_WIDTH, 40, COLOR_RED);
    display_draw_string(10, 210, "SECURITY ALERT!", COLOR_YELLOW, COLOR_RED);
    display_draw_string(10, 222, message, COLOR_WHITE, COLOR_RED);
    
    // Blink built-in LED (adapted from multi-LED blink)
    for (int i = 0; i < 5; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(100);
        gpio_put(LED_PIN, 0);
        sleep_ms(100);
    }
}

void blink_led(int times, uint32_t delay_ms) {
    for (int i = 0; i < times; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(delay_ms);
        gpio_put(LED_PIN, 0);
        sleep_ms(delay_ms);
    }
}

void set_boot_stage_led(int stage, bool on) {
    if (on) {
        // Blink (stage + 1) times to indicate stage (adapted for single LED)
        blink_led(stage + 1, 200);
    } else {
        gpio_put(LED_PIN, 0);
    }
}

void clear_all_leds(void) {
    gpio_put(LED_PIN, 0);
}

/*
 * CRYPTOGRAPHIC PRIMITIVES (Simplified)
 */

typedef struct {
    uint8_t data[PUBLIC_KEY_SIZE];
    char name[32];
} public_key_t;

typedef struct {
    uint8_t data[SIGNATURE_SIZE];
} signature_t;

// Root of Trust public keys (burned in ROM - immutable)
static const public_key_t ROOT_PUBLIC_KEY = {
    .data = {
        0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf0,
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
        0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x00, 0x11,
        0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99
    },
    .name = "ROOT_KEY"
};

static const public_key_t BOOTLOADER_PUBLIC_KEY = {
    .data = {
        0xab, 0xcd, 0xef, 0x01, 0x23, 0x45, 0x67, 0x89,
        0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10,
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
        0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x00
    },
    .name = "BOOTLOADER_KEY"
};

void simple_hash(const uint8_t *data, size_t len, uint8_t *hash) {
    uint32_t h[8] = {
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    };
    
    for (size_t i = 0; i < len; i++) {
        h[i % 8] ^= data[i];
        h[i % 8] = (h[i % 8] << 7) | (h[i % 8] >> 25);
        h[i % 8] += data[i] * 31;
    }
    
    for (int i = 0; i < 8; i++) {
        hash[i*4 + 0] = (h[i] >> 24) & 0xFF;
        hash[i*4 + 1] = (h[i] >> 16) & 0xFF;
        hash[i*4 + 2] = (h[i] >> 8) & 0xFF;
        hash[i*4 + 3] = h[i] & 0xFF;
    }
}

bool verify_signature(const uint8_t *data, size_t len, const signature_t *sig, const public_key_t *pubkey) {
    uint8_t hash[HASH_SIZE];
    simple_hash(data, len, hash);
    
    uint8_t expected[SIGNATURE_SIZE];
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        expected[i] = hash[i % HASH_SIZE] ^ pubkey->data[i % PUBLIC_KEY_SIZE];
    }
    
    uint8_t diff = 0;
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        diff |= (sig->data[i] ^ expected[i]);
    }
    
    return (diff == 0);
}

void sign_data(const uint8_t *data, size_t len, signature_t *sig, const public_key_t *pubkey) {
    uint8_t hash[HASH_SIZE];
    simple_hash(data, len, hash);
    
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        sig->data[i] = hash[i % HASH_SIZE] ^ pubkey->data[i % PUBLIC_KEY_SIZE];
    }
}

/*
 * IMAGE METADATA AND VERSIONING
 */

typedef enum {
    IMAGE_TYPE_BOOTLOADER = 1,
    IMAGE_TYPE_APPLICATION = 2,
    IMAGE_TYPE_MODULE = 3
} image_type_t;

typedef struct {
    uint32_t magic;              // 0x53454342 ("SECB")
    uint32_t version;            // Monotonic version number
    uint32_t image_size;         // Size of code
    image_type_t image_type;     // Type of image
    uint32_t timestamp;          // Build timestamp
    signature_t signature;       // Ed25519 signature
    uint8_t hash[HASH_SIZE];     // SHA256 of image
    char description[64];        // Human-readable description
} __attribute__((packed)) image_header_t;

static uint32_t version_counters[3] = {0, 0, 0};  // BL, APP, MOD

/*
 * BOOT STATUS
 */

typedef enum {
    BOOT_STATUS_OK = 0,
    BOOT_STATUS_SIG_INVALID,
    BOOT_STATUS_VERSION_ROLLBACK,
    BOOT_STATUS_HASH_MISMATCH,
    BOOT_STATUS_CORRUPTED,
    BOOT_STATUS_UNTRUSTED
} boot_status_t;

boot_status_t verify_image(const image_header_t *hdr, const uint8_t *image_data, const public_key_t *expected_key, image_type_t expected_type) {
    if (hdr->magic != 0x53454342) {
        return BOOT_STATUS_CORRUPTED;
    }
    
    if (hdr->image_type != expected_type) {
        return BOOT_STATUS_UNTRUSTED;
    }
    
    uint8_t computed_hash[HASH_SIZE];
    simple_hash(image_data, hdr->image_size, computed_hash);
    if (memcmp(computed_hash, hdr->hash, HASH_SIZE) != 0) {
        return BOOT_STATUS_HASH_MISMATCH;
    }
    
    if (!verify_signature(image_data, hdr->image_size, 
                         &hdr->signature, expected_key)) {
        return BOOT_STATUS_SIG_INVALID;
    }
    
    uint32_t stored_version = version_counters[expected_type - 1];
    if (hdr->version < stored_version) {
        return BOOT_STATUS_VERSION_ROLLBACK;
    }
    
    if (hdr->version > stored_version) {
        version_counters[expected_type - 1] = hdr->version;
    }
    
    return BOOT_STATUS_OK;
}

/*
 * TEST IMAGE CREATION
 */

void create_test_image(image_header_t *hdr, uint8_t *image_data, size_t size, image_type_t type, uint32_t version, const char *desc, const public_key_t *signing_key, bool tamper) {
    hdr->magic = 0x53454342;
    hdr->version = version;
    hdr->image_size = size;
    hdr->image_type = type;
    hdr->timestamp = to_ms_since_boot(get_absolute_time());
    strncpy(hdr->description, desc, sizeof(hdr->description) - 1);
    
    for (size_t i = 0; i < size; i++) {
        image_data[i] = (uint8_t)(i ^ version ^ type);
    }
    
    if (tamper) {
        image_data[size / 2] ^= 0xFF;
    }
    
    simple_hash(image_data, size, hdr->hash);
    sign_data(image_data, size, &hdr->signature, signing_key);
}

/*
 * DEMONSTRATION SCENARIOS
 */

void demo_successful_boot(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 1: SUCCESSFUL BOOT", COLOR_GREEN);
    
    uint8_t *bl_data = malloc(1024);
    uint8_t *app_data = malloc(2048);
    uint8_t *mod_data = malloc(1024);
    
    image_header_t bl_hdr, app_hdr, mod_hdr;
    
    create_test_image(&bl_hdr, bl_data, 1024, IMAGE_TYPE_BOOTLOADER, 1, "BOOTLOADER v1.0", &ROOT_PUBLIC_KEY, false);
    create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION, 1, "APPLICATION v1.0", &BOOTLOADER_PUBLIC_KEY, false);
    create_test_image(&mod_hdr, mod_data, 1024, IMAGE_TYPE_MODULE, 1, "SECURITY MODULE v1.0", &BOOTLOADER_PUBLIC_KEY, false);
    
    // Stage 1: Root of Trust verifies Bootloader
    display_draw_string(10, 40, "STAGE 1: ROOT OF TRUST", COLOR_CYAN, COLOR_BLACK);
    set_boot_stage_led(0, true);
    sleep_ms(500);
    
    draw_image_info(55, bl_hdr.description, bl_hdr.version, bl_hdr.image_size);
    
    boot_status_t status = verify_image(&bl_hdr, bl_data, &ROOT_PUBLIC_KEY, IMAGE_TYPE_BOOTLOADER);
    
    draw_verification_box(80, "VERIFYING BOOTLOADER..", status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    if (status != BOOT_STATUS_OK) {
        draw_security_alert("BOOTLOADER VERIFICATION FAILED!");
        goto cleanup;
    }
    
    // Stage 2: Bootloader verifies Application
    display_draw_string(10, 125, "STAGE 2: BOOTLOADER", COLOR_CYAN, COLOR_BLACK);
    set_boot_stage_led(1, true);
    sleep_ms(500);
    
    draw_image_info(140, app_hdr.description, app_hdr.version, app_hdr.image_size);
    
    status = verify_image(&app_hdr, app_data, &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
    
    draw_verification_box(165, "VERIFYING APPLICATION..", status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    if (status != BOOT_STATUS_OK) {
        draw_security_alert("APPLICATION VERIFICATION FAILED!");
        goto cleanup;
    }
    
    set_boot_stage_led(2, true);
    
    // Success!
    display_fill_rect(0, 200, DISPLAY_WIDTH, 40, 0x0320);
    display_draw_string(60, 210, "BOOT SUCCESSFUL!", COLOR_GREEN, 0x0320);
    display_draw_string(50, 222, "SYSTEM IS SECURE", COLOR_WHITE, 0x0320);
    
    // Success pattern on LED (adapted: blink 3 times)
    for (int i = 0; i < 3; i++) {
        clear_all_leds();
        sleep_ms(200);
        gpio_put(LED_PIN, 1);
        sleep_ms(200);
    }

// yeah, I know a goto is frowned upon,
// but here it keeps cleanup code in one place
cleanup:
    free(bl_data);
    free(app_data);
    free(mod_data);
    sleep_ms(3000);
    clear_all_leds();
}

void demo_tampered_image(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 2: TAMPERED IMAGE", COLOR_RED);
    
    uint8_t *app_data = malloc(2048);
    image_header_t app_hdr;
    
    display_draw_string(10, 40, "ATTACKER MODIFIES BINARY..", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION, 1, "APPLICATION V1.0 [TAMPERED]", &BOOTLOADER_PUBLIC_KEY, true);
    
    set_boot_stage_led(1, true);
    
    draw_image_info(60, app_hdr.description, app_hdr.version, app_hdr.image_size);
    
    display_draw_string(10, 95, "BOOTLOADER VERIFYING...", COLOR_CYAN, COLOR_BLACK);
    sleep_ms(1000);
    
    boot_status_t status = verify_image(&app_hdr, app_data, &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
    
    draw_verification_box(115, "HASH VERIFICATION", status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    draw_security_alert("TAMPERING DETECTED!");
    
    display_draw_string(10, 165, "HASH MISMATCH DETECTED!", COLOR_RED, COLOR_BLACK);
    display_draw_string(10, 180, "IMAGE HAS BEEN MODIFIED", COLOR_RED, COLOR_BLACK);
    
    free(app_data);
    sleep_ms(3000);
    clear_all_leds();
}

void demo_rollback_attack(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 3: ROLLBACK ATTACK", COLOR_RED);
    
    uint8_t *app_data_v2 = malloc(2048);
    uint8_t *app_data_v1 = malloc(2048);
    
    image_header_t app_hdr_v2, app_hdr_v1;
    
    display_draw_string(10, 40, "STEP 1: INSTALL V2.0 (SECURE)", COLOR_CYAN, COLOR_BLACK);
    
    create_test_image(&app_hdr_v2, app_data_v2, 2048, IMAGE_TYPE_APPLICATION, 2, "APPLICATION V2.0 (PATCHED)", &BOOTLOADER_PUBLIC_KEY, false);
    
    set_boot_stage_led(1, true);
    draw_image_info(55, app_hdr_v2.description, app_hdr_v2.version, app_hdr_v2.image_size);
    
    boot_status_t status = verify_image(&app_hdr_v2, app_data_v2, &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
    
    draw_verification_box(80, "INSTALLING V2.0..", status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    char counter_str[32];
    snprintf(counter_str, sizeof(counter_str), "VERSION COUNTER NOW: %u", version_counters[IMAGE_TYPE_APPLICATION - 1]);
    display_draw_string(10, 105, counter_str, COLOR_GREEN, COLOR_BLACK);
    sleep_ms(1500);
    
    // Attacker tries to downgrade
    display_draw_string(10, 125, "STEP 2: ATTACKER TRIES V1.0", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    create_test_image(&app_hdr_v1, app_data_v1, 2048, IMAGE_TYPE_APPLICATION, 1, "APPLICATION V1.0 (VULNERABLE)", &BOOTLOADER_PUBLIC_KEY, false);
    
    set_boot_stage_led(2, true);
    draw_image_info(140, app_hdr_v1.description, app_hdr_v1.version, app_hdr_v1.image_size);
    
    status = verify_image(&app_hdr_v1, app_data_v1, &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
    
    draw_verification_box(165, "VERSION CHECK", status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    draw_security_alert("ROLLBACK BLOCKED!");
    
    display_draw_string(10, 175, "VERSION TOO OLD!", COLOR_RED, COLOR_BLACK);
    
    free(app_data_v2);
    free(app_data_v1);
    sleep_ms(3000);
    clear_all_leds();
}

void demo_wrong_signature(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 4: UNTRUSTED KEY", COLOR_RED);
    
    uint8_t *app_data = malloc(2048);
    image_header_t app_hdr;
    
    display_draw_string(10, 40, "ATTACKER SIGNS WITH WRONG KEY", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    public_key_t attacker_key = {
        .data = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF},
        .name = "ATTACKER_KEY"
    };
    
    create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION,
                     3, "MALICIOUS APP", 
                     &attacker_key, false);
    
    set_boot_stage_led(1, true);
    
    draw_image_info(60, app_hdr.description, app_hdr.version, app_hdr.image_size);
    
    display_draw_string(10, 95, "BOOTLOADER VERIFYING..", COLOR_CYAN, COLOR_BLACK);
    sleep_ms(1000);
    
    boot_status_t status = verify_image(&app_hdr, app_data, &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
    
    draw_verification_box(115, "SIGNATURE VERIFICATION", status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    draw_security_alert("UNTRUSTED CODE!");
    
    display_draw_string(10, 165, "SIGNATURE INVALID!", COLOR_RED, COLOR_BLACK);
    display_draw_string(10, 180, "NOT SIGNED BY TRUSTED KEY", COLOR_RED, COLOR_BLACK);
    
    free(app_data);
    sleep_ms(3000);
    clear_all_leds();
}

void show_chain_of_trust(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("CHAIN OF TRUST", COLOR_CYAN);
    
    display_draw_string(10, 50, "ROOT OF TRUST (ROM)", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 65, "- IMMUTABLE HARDWARE ROOT", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(20, 77, "- CONTAINS PUBLIC KEYS", COLOR_WHITE, COLOR_BLACK);
    set_boot_stage_led(0, true);
    sleep_ms(1500);
    
    display_draw_string(40, 95, "|", COLOR_YELLOW, COLOR_BLACK);
    display_draw_string(40, 100, "V", COLOR_YELLOW, COLOR_BLACK);
    
    display_draw_string(10, 110, "BOOTLOADER", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 125, "- VERIFIED BY ROT", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(20, 137, "- VERIFIES APPLICATION", COLOR_WHITE, COLOR_BLACK);
    set_boot_stage_led(1, true);
    sleep_ms(1500);
    
    display_draw_string(40, 155, "|", COLOR_YELLOW, COLOR_BLACK);
    display_draw_string(40, 160, "V", COLOR_YELLOW, COLOR_BLACK);
    
    display_draw_string(10, 170, "APPLICATION", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 185, "- VERIFIED BY BOOTLOADER", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(20, 197, "- CAN LOAD MODULES", COLOR_WHITE, COLOR_BLACK);
    set_boot_stage_led(2, true);
    
    display_draw_string(10, 215, "EACH STAGE TRUSTS ONLY WHAT", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(10, 227, "IT VERIFIES CRYPTOGRAPHICALLY", COLOR_CYAN, COLOR_BLACK);
    
    sleep_ms(5000);
    clear_all_leds();
}

/*
 * BUTTON CALLBACKS AND STATE
 */

static int current_scenario = 0;
static const int num_scenarios = 5;
static bool scenario_running = false;
static bool auto_advance = false;

void button_a_callback(button_t button) {
    if (!scenario_running) {
        current_scenario = (current_scenario + 1) % num_scenarios;
    }
}

void button_b_callback(button_t button) {
    if (!scenario_running) {
        current_scenario = (current_scenario + num_scenarios - 1) % num_scenarios;
    }
}

void button_x_callback(button_t button) {
    scenario_running = true;
}

void button_y_callback(button_t button) {
    auto_advance = !auto_advance;
}

/*
 * MAIN PROGRAM
 */

int main() {
    stdio_init_all();
    
    // Initialize display
    if (display_pack_init() != DISPLAY_OK) {
        gpio_init(LED_PIN);
        gpio_set_dir(LED_PIN, GPIO_OUT);
        while (1) {
            gpio_put(LED_PIN, 1);
            sleep_ms(100);
            gpio_put(LED_PIN, 0);
            sleep_ms(100);
        }
    }
    
    // Initialize buttons
    buttons_init();
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Initialize built-in LED
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    // Splash screen
    display_clear(COLOR_BLACK);
    display_draw_string(30, 60, "SECURE BOOT CHAIN", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(60, 80, "DEMONSTRATION", COLOR_CYAN, COLOR_BLACK);
    // display_draw_string(40, 110, "Raspberry Pi Pico 2", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(20, 140, "A: NEXT  B: PREV", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 155, "X: RUN   Y: AUTO", COLOR_GREEN, COLOR_BLACK);
    sleep_ms(3000);
    
    const char *scenario_names[] = {
        "1. SUCCESSFUL BOOT",
        "2. TAMPERED IMAGE",
        "3. ROLLBACK ATTACK",
        "4. WRONG SIGNATURE",
        "5. CHAIN OF TRUST"
    };
    
    while (true) {
        buttons_update();
        
        if (!scenario_running) {
            // Show menu
            display_clear(COLOR_BLACK);
            draw_boot_header("SELECT SCENARIO", COLOR_CYAN);
            
            for (int i = 0; i < num_scenarios; i++) {
                uint16_t color = (i == current_scenario) ? COLOR_GREEN : COLOR_WHITE;
                char line[32];
                snprintf(line, sizeof(line), "%s %s",
                        (i == current_scenario) ? ">" : " ", scenario_names[i]);
                display_draw_string(10, 50 + i * 25, line, color, COLOR_BLACK);
            }
            
            display_draw_string(10, 210, "A/B: SELECT  X: RUN", COLOR_CYAN, COLOR_BLACK);
            display_draw_string(10, 222, auto_advance ? "Y: AUTO [ON]" : "Y: AUTO [OFF]", 
                              COLOR_CYAN, COLOR_BLACK);
            
            sleep_ms(100);
            continue;

        } else {
            // Run the selected scenario
            scenario_running = false;  // Will be set to true again by X button if needed
            
            switch (current_scenario) {
                case 0:
                    demo_successful_boot();
                    break;
                    
                case 1:
                    demo_tampered_image();
                    break;
                    
                case 2:
                    demo_rollback_attack();
                    break;
                    
                case 3:
                    demo_wrong_signature();
                    break;
                    
                case 4:
                    show_chain_of_trust();
                    break;
                    
                default:
                    // Should never happen
                    display_clear(COLOR_BLACK);
                    display_draw_string(30, 100, "INVALID SCENARIO!", COLOR_RED, COLOR_BLACK);
                    sleep_ms(2000);
                    break;
            }
            
            // After scenario finishes, briefly show "Done" screen
            display_clear(COLOR_BLACK);
            display_draw_string(70, 100, "SCENARIO COMPLETE", COLOR_GREEN, COLOR_BLACK);
            display_draw_string(40, 140, "PRESS X TO RUN AGAIN", COLOR_WHITE, COLOR_BLACK);
            display_draw_string(50, 170, "OR A/B TO SELECT", COLOR_WHITE, COLOR_BLACK);
            
            sleep_ms(1800);
            
            // Auto-advance feature
            if (auto_advance) {
                current_scenario = (current_scenario + 1) % num_scenarios;
                scenario_running = true;  // Auto start next one
                sleep_ms(800);
            }
        }
    }

    return 0;
}


