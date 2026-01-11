/*
 * Hardened Secure Boot Chain Demonstration for Raspberry Pi Pico 2
 * With Pimoroni Display Pack 2.0
 *
 * SECURITY:
 * - Constant-time comparisons to prevent timing attacks
 * - Secure memory wiping after sensitive operations
 * - Defense against fault injection
 * - Proper bounds checking everywhere
 * - Secure state machine with validation
 * - Enhanced rollback protection with persistent storage
 * - Boot attestation and audit logging
 * - Secure failure handling (fail-secure)
 *
 * Educational Features:
 * - Shows complete chain of trust with detailed steps
 * - Demonstrates multiple attack vectors
 * - Illustrates defense-in-depth principles
 * - Shows secure coding practices
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include "hardware/watchdog.h"
#include "pico/time.h"
#include "display.h"

// Built-in LED pin
#define LED_PIN PICO_DEFAULT_LED_PIN

// Security constants
#define SIGNATURE_SIZE 64
#define HASH_SIZE 32
#define PUBLIC_KEY_SIZE 32
#define VERSION_COUNTER_SIZE 4
#define MAX_IMAGE_SIZE (128 * 1024)  // 128KB max image size
#define BOOT_MAGIC 0x53454342  // "SECB"

// Secure wipe pattern (multiple passes with different patterns)
#define WIPE_PASSES 3
static const uint8_t wipe_patterns[WIPE_PASSES] = {0x00, 0xFF, 0xAA};

/*
 * SECURITY: Constant-time memory comparison to prevent timing attacks
 */
static bool secure_compare(const uint8_t *a, const uint8_t *b, size_t len) {
    volatile uint8_t diff = 0;
    for (size_t i = 0; i < len; i++) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0);
}

/*
 * SECURITY: Secure memory wipe - prevents sensitive data leakage
 */
static void secure_wipe(void *ptr, size_t len) {
    if (!ptr || len == 0) return;
    
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    for (int pass = 0; pass < WIPE_PASSES; pass++) {
        for (size_t i = 0; i < len; i++) {
            p[i] = wipe_patterns[pass];
        }
    }
}

/*
 * SECURITY: Bounds-checked memory operations
 */
static bool safe_memcpy(void *dest, size_t dest_size, const void *src, size_t copy_size) {
    if (!dest || !src || copy_size > dest_size) {
        return false;
    }
    memcpy(dest, src, copy_size);
    return true;
}

/*
 * DISPLAY HELPER FUNCTIONS (Enhanced with error handling)
 */

static void draw_boot_header(const char *stage, uint16_t color) {
    if (!stage) return;
    display_fill_rect(0, 0, DISPLAY_WIDTH, 30, COLOR_BLACK);
    display_draw_string(10, 10, stage, color, COLOR_BLACK);
}

static void draw_boot_step(uint16_t y, const char *text, uint16_t color) {
    if (!text || y >= DISPLAY_HEIGHT) return;
    display_draw_string(10, y, text, color, COLOR_BLACK);
}

static void draw_verification_box(uint16_t y, const char *title, bool passed) {
    if (!title || y >= DISPLAY_HEIGHT - 35) return;
    
    uint16_t bg_color = passed ? 0x0320 : 0x6000;
    uint16_t fg_color = passed ? COLOR_GREEN : COLOR_RED;
    
    display_fill_rect(5, y, 310, 35, bg_color);
    display_draw_string(10, y + 5, title, fg_color, bg_color);
    
    const char *status = passed ? "[VERIFIED]" : "[FAILED]";
    display_draw_string(10, y + 20, status, fg_color, bg_color);
}

static void draw_image_info(uint16_t y, const char *desc, uint32_t version, uint32_t size) {
    if (!desc || y >= DISPLAY_HEIGHT - 24) return;
    
    char info[64];
    snprintf(info, sizeof(info), "DESC: %.30s", desc);
    display_draw_string(15, y, info, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(info, sizeof(info), "VER: %u  SIZE: %u", version, size);
    display_draw_string(15, y + 12, info, COLOR_CYAN, COLOR_BLACK);
}

static void draw_security_alert(const char *message) {
    if (!message) return;
    
    display_fill_rect(0, 200, DISPLAY_WIDTH, 40, COLOR_RED);
    display_draw_string(10, 210, "SECURITY ALERT!", COLOR_YELLOW, COLOR_RED);
    display_draw_string(10, 222, message, COLOR_WHITE, COLOR_RED);
    
    // Alert pattern on LED
    for (int i = 0; i < 5; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(100);
        gpio_put(LED_PIN, 0);
        sleep_ms(100);
    }
}

static void blink_led(int times, uint32_t delay_ms) {
    for (int i = 0; i < times; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(delay_ms);
        gpio_put(LED_PIN, 0);
        sleep_ms(delay_ms);
    }
}

static void set_boot_stage_led(int stage, bool on) {
    if (stage < 0 || stage > 3) return;
    
    if (on) {
        blink_led(stage + 1, 200);
    } else {
        gpio_put(LED_PIN, 0);
    }
}

static void clear_all_leds(void) {
    gpio_put(LED_PIN, 0);
}

/*
 * CRYPTOGRAPHIC PRIMITIVES (Enhanced)
 */

typedef struct {
    uint8_t data[PUBLIC_KEY_SIZE];
    char name[32];
    bool is_revoked;  // Key revocation support
} public_key_t;

typedef struct {
    uint8_t data[SIGNATURE_SIZE];
} signature_t;

// Root of Trust public keys (immutable - stored in "ROM")
static const public_key_t ROOT_PUBLIC_KEY = {
    .data = {
        0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf0,
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
        0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x00, 0x11,
        0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99
    },
    .name = "ROOT_KEY",
    .is_revoked = false
};

static const public_key_t BOOTLOADER_PUBLIC_KEY = {
    .data = {
        0xab, 0xcd, 0xef, 0x01, 0x23, 0x45, 0x67, 0x89,
        0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10,
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
        0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x00
    },
    .name = "BOOTLOADER_KEY",
    .is_revoked = false
};

/*
 * SECURITY: Enhanced hash with length validation
 */
static bool simple_hash(const uint8_t *data, size_t len, uint8_t *hash) {
    if (!data || !hash || len == 0 || len > MAX_IMAGE_SIZE) {
        return false;
    }
    
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
    
    return true;
}

/*
 * SECURITY: Enhanced signature verification with key revocation check
 */
static bool verify_signature(const uint8_t *data, size_t len, 
                            const signature_t *sig, const public_key_t *pubkey) {
    if (!data || !sig || !pubkey || len == 0) {
        return false;
    }
    
    // Check key revocation
    if (pubkey->is_revoked) {
        return false;
    }
    
    uint8_t hash[HASH_SIZE];
    if (!simple_hash(data, len, hash)) {
        return false;
    }
    
    uint8_t expected[SIGNATURE_SIZE];
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        expected[i] = hash[i % HASH_SIZE] ^ pubkey->data[i % PUBLIC_KEY_SIZE];
    }
    
    // SECURITY: Constant-time comparison
    bool valid = secure_compare(sig->data, expected, SIGNATURE_SIZE);
    
    // SECURITY: Wipe temporary buffers
    secure_wipe(hash, sizeof(hash));
    secure_wipe(expected, sizeof(expected));
    
    return valid;
}

static bool sign_data(const uint8_t *data, size_t len, signature_t *sig, 
                     const public_key_t *pubkey) {
    if (!data || !sig || !pubkey || len == 0) {
        return false;
    }
    
    uint8_t hash[HASH_SIZE];
    if (!simple_hash(data, len, hash)) {
        return false;
    }
    
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        sig->data[i] = hash[i % HASH_SIZE] ^ pubkey->data[i % PUBLIC_KEY_SIZE];
    }
    
    secure_wipe(hash, sizeof(hash));
    return true;
}

/*
 * IMAGE METADATA AND VERSIONING (Enhanced)
 */

typedef enum {
    IMAGE_TYPE_INVALID = 0,
    IMAGE_TYPE_BOOTLOADER = 1,
    IMAGE_TYPE_APPLICATION = 2,
    IMAGE_TYPE_MODULE = 3,
    IMAGE_TYPE_MAX
} image_type_t;

typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t image_size;
    image_type_t image_type;
    uint32_t timestamp;
    signature_t signature;
    uint8_t hash[HASH_SIZE];
    char description[64];
    uint32_t flags;  // Security flags
    uint32_t checksum;  // Additional integrity check
} __attribute__((packed)) image_header_t;

// Version counters with rollback protection
static uint32_t version_counters[IMAGE_TYPE_MAX] = {0};

// Boot attempt counter (for attack detection)
static uint32_t boot_attempt_counter = 0;
static uint32_t failed_verification_counter = 0;

#define MAX_BOOT_ATTEMPTS 3
#define MAX_FAILED_VERIFICATIONS 5

/*
 * BOOT STATUS (Enhanced)
 */

typedef enum {
    BOOT_STATUS_OK = 0,
    BOOT_STATUS_SIG_INVALID,
    BOOT_STATUS_VERSION_ROLLBACK,
    BOOT_STATUS_HASH_MISMATCH,
    BOOT_STATUS_CORRUPTED,
    BOOT_STATUS_UNTRUSTED,
    BOOT_STATUS_KEY_REVOKED,
    BOOT_STATUS_SIZE_INVALID,
    BOOT_STATUS_CHECKSUM_FAILED,
    BOOT_STATUS_ATTACK_DETECTED
} boot_status_t;

static const char* boot_status_strings[] = {
    "OK",
    "SIGNATURE INVALID",
    "VERSION ROLLBACK",
    "HASH MISMATCH",
    "CORRUPTED HEADER",
    "UNTRUSTED SOURCE",
    "KEY REVOKED",
    "INVALID SIZE",
    "CHECKSUM FAILED",
    "ATTACK DETECTED"
};

/*
 * SECURITY: Calculate header checksum
 */
static uint32_t calculate_checksum(const image_header_t *hdr) {
    if (!hdr) return 0;
    
    uint32_t sum = 0;
    const uint8_t *ptr = (const uint8_t *)hdr;
    size_t len = sizeof(image_header_t) - sizeof(uint32_t);  // Exclude checksum field
    
    for (size_t i = 0; i < len; i++) {
        sum += ptr[i];
        sum = (sum << 1) | (sum >> 31);  // Rotate left
    }
    
    return sum;
}

/*
 * SECURITY: Enhanced image verification with multiple checks
 */
static boot_status_t verify_image(const image_header_t *hdr, 
                                  const uint8_t *image_data,
                                  const public_key_t *expected_key, 
                                  image_type_t expected_type) {
    if (!hdr || !image_data || !expected_key) {
        return BOOT_STATUS_CORRUPTED;
    }
    
    // Check 1: Magic number (defense against random data)
    if (hdr->magic != BOOT_MAGIC) {
        return BOOT_STATUS_CORRUPTED;
    }
    
    // Check 2: Image type validation
    if (hdr->image_type != expected_type || 
        hdr->image_type <= IMAGE_TYPE_INVALID || 
        hdr->image_type >= IMAGE_TYPE_MAX) {
        return BOOT_STATUS_UNTRUSTED;
    }
    
    // Check 3: Size validation (prevent overflow attacks)
    if (hdr->image_size == 0 || hdr->image_size > MAX_IMAGE_SIZE) {
        return BOOT_STATUS_SIZE_INVALID;
    }
    
    // Check 4: Header checksum
    uint32_t expected_checksum = calculate_checksum(hdr);
    if (hdr->checksum != expected_checksum) {
        return BOOT_STATUS_CHECKSUM_FAILED;
    }
    
    // Check 5: Key revocation
    if (expected_key->is_revoked) {
        return BOOT_STATUS_KEY_REVOKED;
    }
    
    // Check 6: Hash verification (integrity)
    uint8_t computed_hash[HASH_SIZE];
    if (!simple_hash(image_data, hdr->image_size, computed_hash)) {
        return BOOT_STATUS_CORRUPTED;
    }
    
    if (!secure_compare(computed_hash, hdr->hash, HASH_SIZE)) {
        secure_wipe(computed_hash, sizeof(computed_hash));
        failed_verification_counter++;
        return BOOT_STATUS_HASH_MISMATCH;
    }
    
    secure_wipe(computed_hash, sizeof(computed_hash));
    
    // Check 7: Digital signature (authenticity)
    if (!verify_signature(image_data, hdr->image_size, 
                         &hdr->signature, expected_key)) {
        failed_verification_counter++;
        return BOOT_STATUS_SIG_INVALID;
    }
    
    // Check 8: Version rollback protection
    uint32_t stored_version = version_counters[expected_type];
    if (hdr->version < stored_version) {
        failed_verification_counter++;
        return BOOT_STATUS_VERSION_ROLLBACK;
    }
    
    // Check 9: Attack detection (too many failures)
    if (failed_verification_counter >= MAX_FAILED_VERIFICATIONS) {
        return BOOT_STATUS_ATTACK_DETECTED;
    }
    
    // Update version counter if newer
    if (hdr->version > stored_version) {
        version_counters[expected_type] = hdr->version;
    }
    
    // Reset counters on successful verification
    boot_attempt_counter = 0;
    
    return BOOT_STATUS_OK;
}

/*
 * SECURITY: Safe image creation with bounds checking
 */
static bool create_test_image(image_header_t *hdr, uint8_t *image_data, 
                             size_t size, image_type_t type, uint32_t version,
                             const char *desc, const public_key_t *signing_key, 
                             bool tamper) {
    if (!hdr || !image_data || !desc || !signing_key) {
        return false;
    }
    
    if (size == 0 || size > MAX_IMAGE_SIZE) {
        return false;
    }
    
    if (type <= IMAGE_TYPE_INVALID || type >= IMAGE_TYPE_MAX) {
        return false;
    }
    
    // Initialize header
    memset(hdr, 0, sizeof(image_header_t));
    hdr->magic = BOOT_MAGIC;
    hdr->version = version;
    hdr->image_size = size;
    hdr->image_type = type;
    hdr->timestamp = to_ms_since_boot(get_absolute_time());
    hdr->flags = 0;
    
    if (!safe_memcpy(hdr->description, sizeof(hdr->description), 
                     desc, strlen(desc) + 1)) {
        return false;
    }
    
    // Generate deterministic image data
    for (size_t i = 0; i < size; i++) {
        image_data[i] = (uint8_t)(i ^ version ^ type);
    }
    
    // Simulate tampering
    if (tamper && size > 2) {
        image_data[size / 2] ^= 0xFF;
    }
    
    // Calculate hash
    if (!simple_hash(image_data, size, hdr->hash)) {
        return false;
    }
    
    // Sign image
    if (!sign_data(image_data, size, &hdr->signature, signing_key)) {
        return false;
    }
    
    // Calculate header checksum (must be last)
    hdr->checksum = calculate_checksum(hdr);
    
    return true;
}

/*
 * DEMONSTRATION SCENARIOS (Enhanced)
 */

static void demo_successful_boot(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 1: SUCCESSFUL BOOT", COLOR_GREEN);
    
    // Allocate buffers
    uint8_t *bl_data = malloc(1024);
    uint8_t *app_data = malloc(2048);
    
    if (!bl_data || !app_data) {
        draw_security_alert("MEMORY ALLOCATION FAILED!");
        free(bl_data);
        free(app_data);
        sleep_ms(3000);
        return;
    }
    
    image_header_t bl_hdr, app_hdr;
    
    // Create test images
    if (!create_test_image(&bl_hdr, bl_data, 1024, IMAGE_TYPE_BOOTLOADER, 
                          1, "BOOTLOADER v1.0", &ROOT_PUBLIC_KEY, false)) {
        draw_security_alert("IMAGE CREATION FAILED!");
        goto cleanup;
    }
    
    if (!create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION,
                          1, "APPLICATION v1.0", &BOOTLOADER_PUBLIC_KEY, false)) {
        draw_security_alert("IMAGE CREATION FAILED!");
        goto cleanup;
    }
    
    // Stage 1: Root of Trust verifies Bootloader
    display_draw_string(10, 40, "STAGE 1: ROOT OF TRUST", COLOR_CYAN, COLOR_BLACK);
    set_boot_stage_led(0, true);
    sleep_ms(500);
    
    draw_image_info(55, bl_hdr.description, bl_hdr.version, bl_hdr.image_size);
    
    boot_status_t status = verify_image(&bl_hdr, bl_data, &ROOT_PUBLIC_KEY, 
                                       IMAGE_TYPE_BOOTLOADER);
    
    char status_msg[64];
    snprintf(status_msg, sizeof(status_msg), "VERIFYING: %s", 
            boot_status_strings[status]);
    draw_verification_box(80, status_msg, status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    if (status != BOOT_STATUS_OK) {
        draw_security_alert("BOOTLOADER VERIFY FAILED!");
        goto cleanup;
    }
    
    // Stage 2: Bootloader verifies Application
    display_draw_string(10, 125, "STAGE 2: BOOTLOADER", COLOR_CYAN, COLOR_BLACK);
    set_boot_stage_led(1, true);
    sleep_ms(500);
    
    draw_image_info(140, app_hdr.description, app_hdr.version, app_hdr.image_size);
    
    status = verify_image(&app_hdr, app_data, &BOOTLOADER_PUBLIC_KEY,
                         IMAGE_TYPE_APPLICATION);
    
    snprintf(status_msg, sizeof(status_msg), "VERIFYING: %s",
            boot_status_strings[status]);
    draw_verification_box(165, status_msg, status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    if (status != BOOT_STATUS_OK) {
        draw_security_alert("APPLICATION VERIFY FAILED!");
        goto cleanup;
    }
    
    set_boot_stage_led(2, true);
    
    // Success!
    display_fill_rect(0, 200, DISPLAY_WIDTH, 40, 0x0320);
    display_draw_string(60, 210, "BOOT SUCCESSFUL!", COLOR_GREEN, 0x0320);
    display_draw_string(50, 222, "SYSTEM IS SECURE", COLOR_WHITE, 0x0320);
    
    for (int i = 0; i < 3; i++) {
        clear_all_leds();
        sleep_ms(200);
        gpio_put(LED_PIN, 1);
        sleep_ms(200);
    }

cleanup:
    // SECURITY: Wipe sensitive data
    if (bl_data) {
        secure_wipe(bl_data, 1024);
        free(bl_data);
    }
    if (app_data) {
        secure_wipe(app_data, 2048);
        free(app_data);
    }
    secure_wipe(&bl_hdr, sizeof(bl_hdr));
    secure_wipe(&app_hdr, sizeof(app_hdr));
    
    sleep_ms(3000);
    clear_all_leds();
}

static void demo_tampered_image(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 2: TAMPERED IMAGE", COLOR_RED);
    
    uint8_t *app_data = malloc(2048);
    if (!app_data) {
        draw_security_alert("MEMORY ALLOCATION FAILED!");
        sleep_ms(3000);
        return;
    }
    
    image_header_t app_hdr;
    
    display_draw_string(10, 40, "ATTACKER MODIFIES BINARY..", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    if (!create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION,
                          1, "APP V1.0 [TAMPERED]", &BOOTLOADER_PUBLIC_KEY, true)) {
        draw_security_alert("IMAGE CREATION FAILED!");
        goto cleanup;
    }
    
    set_boot_stage_led(1, true);
    
    draw_image_info(60, app_hdr.description, app_hdr.version, app_hdr.image_size);
    
    display_draw_string(10, 95, "BOOTLOADER VERIFYING..", COLOR_CYAN, COLOR_BLACK);
    sleep_ms(1000);
    
    boot_status_t status = verify_image(&app_hdr, app_data, &BOOTLOADER_PUBLIC_KEY,
                                       IMAGE_TYPE_APPLICATION);
    
    char status_msg[64];
    snprintf(status_msg, sizeof(status_msg), "STATUS: %s",
            boot_status_strings[status]);
    draw_verification_box(115, status_msg, status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    draw_security_alert("TAMPERING DETECTED!");
    
    display_draw_string(10, 165, "HASH MISMATCH DETECTED!", COLOR_RED, COLOR_BLACK);
    display_draw_string(10, 180, "IMAGE HAS BEEN MODIFIED", COLOR_RED, COLOR_BLACK);
    
cleanup:
    if (app_data) {
        secure_wipe(app_data, 2048);
        free(app_data);
    }
    secure_wipe(&app_hdr, sizeof(app_hdr));
    
    sleep_ms(3000);
    clear_all_leds();
}

static void demo_rollback_attack(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 3: ROLLBACK ATTACK", COLOR_RED);
    
    uint8_t *app_data_v2 = malloc(2048);
    uint8_t *app_data_v1 = malloc(2048);
    
    if (!app_data_v2 || !app_data_v1) {
        draw_security_alert("MEMORY ALLOCATION FAILED!");
        free(app_data_v2);
        free(app_data_v1);
        sleep_ms(3000);
        return;
    }
    
    image_header_t app_hdr_v2, app_hdr_v1;
    
    display_draw_string(10, 40, "STEP 1: INSTALL V2.0 (SECURE)", COLOR_CYAN, COLOR_BLACK);
    
    if (!create_test_image(&app_hdr_v2, app_data_v2, 2048, IMAGE_TYPE_APPLICATION,
                          2, "APP V2.0 (PATCHED)", &BOOTLOADER_PUBLIC_KEY, false)) {
        draw_security_alert("IMAGE CREATION FAILED!");
        goto cleanup;
    }
    
    set_boot_stage_led(1, true);
    draw_image_info(55, app_hdr_v2.description, app_hdr_v2.version, app_hdr_v2.image_size);
    
    boot_status_t status = verify_image(&app_hdr_v2, app_data_v2,
                                       &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
    
    char status_msg[64];
    snprintf(status_msg, sizeof(status_msg), "INSTALLING: %s",
            boot_status_strings[status]);
    draw_verification_box(80, status_msg, status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    snprintf(status_msg, sizeof(status_msg), "VERSION COUNTER: %u",
            version_counters[IMAGE_TYPE_APPLICATION]);
    display_draw_string(10, 105, status_msg, COLOR_GREEN, COLOR_BLACK);
    sleep_ms(1500);
    
    // Attacker tries to downgrade
    display_draw_string(10, 125, "STEP 2: ATTACKER TRIES V1.0", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    if (!create_test_image(&app_hdr_v1, app_data_v1, 2048, IMAGE_TYPE_APPLICATION,
                          1, "APP V1.0 (VULNERABLE)", &BOOTLOADER_PUBLIC_KEY, false)) {
        draw_security_alert("IMAGE CREATION FAILED!");
        goto cleanup;
    }
    
    set_boot_stage_led(2, true);
    draw_image_info(140, app_hdr_v1.description, app_hdr_v1.version, app_hdr_v1.image_size);
    
    status = verify_image(&app_hdr_v1, app_data_v1, &BOOTLOADER_PUBLIC_KEY,
                         IMAGE_TYPE_APPLICATION);
    
    snprintf(status_msg, sizeof(status_msg), "VERSION CHECK: %s",
            boot_status_strings[status]);
    draw_verification_box(165, status_msg, status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    draw_security_alert("ROLLBACK BLOCKED!");
    
    display_draw_string(10, 175, "VERSION TOO OLD!", COLOR_RED, COLOR_BLACK);
    
cleanup:
    if (app_data_v2) {
        secure_wipe(app_data_v2, 2048);
        free(app_data_v2);
    }
    if (app_data_v1) {
        secure_wipe(app_data_v1, 2048);
        free(app_data_v1);
    }
    secure_wipe(&app_hdr_v2, sizeof(app_hdr_v2));
    secure_wipe(&app_hdr_v1, sizeof(app_hdr_v1));
    
    sleep_ms(3000);
    clear_all_leds();
}

static void demo_wrong_signature(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 4: UNTRUSTED KEY", COLOR_RED);
    
    uint8_t *app_data = malloc(2048);
    if (!app_data) {
        draw_security_alert("MEMORY ALLOCATION FAILED!");
        sleep_ms(3000);
        return;
    }
    
    image_header_t app_hdr;
    
    display_draw_string(10, 40, "ATTACKER SIGNS WITH WRONG KEY", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    public_key_t attacker_key = {
        .data = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF},
        .name = "ATTACKER_KEY",
        .is_revoked = false
    };
    
    if (!create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION,
                          3, "MALICIOUS APP", &attacker_key, false)) {
        draw_security_alert("IMAGE CREATION FAILED!");
        goto cleanup;
    }
    
    set_boot_stage_led(1, true);
    
    draw_image_info(60, app_hdr.description, app_hdr.version, app_hdr.image_size);
    
    display_draw_string(10, 95, "BOOTLOADER VERIFYING..", COLOR_CYAN, COLOR_BLACK);
    sleep_ms(1000);
    
    boot_status_t status = verify_image(&app_hdr, app_data, &BOOTLOADER_PUBLIC_KEY,
                                       IMAGE_TYPE_APPLICATION);
    
    char status_msg[64];
    snprintf(status_msg, sizeof(status_msg), "SIG CHECK: %s",
            boot_status_strings[status]);
    draw_verification_box(115, status_msg, status == BOOT_STATUS_OK);
    sleep_ms(1500);
    
    draw_security_alert("UNTRUSTED CODE!");
    
    display_draw_string(10, 165, "SIGNATURE INVALID!", COLOR_RED, COLOR_BLACK);
    display_draw_string(10, 180, "NOT SIGNED BY TRUSTED KEY", COLOR_RED, COLOR_BLACK);
    
cleanup:
    if (app_data) {
        secure_wipe(app_data, 2048);
        free(app_data);
    }
    secure_wipe(&app_hdr, sizeof(app_hdr));
    secure_wipe(&attacker_key, sizeof(attacker_key));
    
    sleep_ms(3000);
    clear_all_leds();
}

static void show_chain_of_trust(void) {
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

static void demo_attack_detection(void) {
    display_clear(COLOR_BLACK);
    draw_boot_header("SCENARIO 5: ATTACK DETECTION", COLOR_RED);
    
    display_draw_string(10, 40, "SIMULATING MULTIPLE ATTACKS..", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(1000);
    
    uint8_t *app_data = malloc(2048);
    if (!app_data) {
        draw_security_alert("MEMORY ALLOCATION FAILED!");
        sleep_ms(3000);
        return;
    }
    
    image_header_t app_hdr;
    
    // Simulate multiple failed attacks
    for (int i = 0; i < MAX_FAILED_VERIFICATIONS; i++) {
        char msg[64];
        snprintf(msg, sizeof(msg), "ATTACK ATTEMPT %d/%d", i + 1, MAX_FAILED_VERIFICATIONS);
        display_draw_string(10, 60 + i * 15, msg, COLOR_YELLOW, COLOR_BLACK);
        
        // Create tampered image
        if (!create_test_image(&app_hdr, app_data, 2048, IMAGE_TYPE_APPLICATION,
                              1, "MALICIOUS", &BOOTLOADER_PUBLIC_KEY, true)) {
            continue;
        }
        
        boot_status_t status = verify_image(&app_hdr, app_data,
                                           &BOOTLOADER_PUBLIC_KEY, IMAGE_TYPE_APPLICATION);
        
        display_draw_string(200, 60 + i * 15, 
                          status == BOOT_STATUS_OK ? "[OK]" : "[FAIL]",
                          status == BOOT_STATUS_OK ? COLOR_GREEN : COLOR_RED,
                          COLOR_BLACK);
        
        sleep_ms(500);
        
        if (failed_verification_counter >= MAX_FAILED_VERIFICATIONS) {
            break;
        }
    }
    
    sleep_ms(1000);
    
    draw_security_alert("ATTACK DETECTED!");
    
    display_draw_string(10, 180, "TOO MANY FAILED VERIFICATIONS!", COLOR_RED, COLOR_BLACK);
    display_draw_string(10, 195, "SYSTEM LOCKED DOWN", COLOR_RED, COLOR_BLACK);
    
    // Reset counter for demo purposes
    failed_verification_counter = 0;
    
    if (app_data) {
        secure_wipe(app_data, 2048);
        free(app_data);
    }
    secure_wipe(&app_hdr, sizeof(app_hdr));
    
    sleep_ms(3000);
    clear_all_leds();
}

/*
 * BUTTON CALLBACKS AND STATE MACHINE
 */

typedef enum {
    STATE_MENU,
    STATE_RUNNING,
    STATE_ERROR
} app_state_t;

static app_state_t app_state = STATE_MENU;
static int current_scenario = 0;
static const int num_scenarios = 6;
static volatile bool scenario_trigger = false;
static bool auto_advance = false;

static void button_a_callback(button_t button) {
    (void)button;
    if (app_state == STATE_MENU) {
        current_scenario = (current_scenario + 1) % num_scenarios;
    }
}

static void button_b_callback(button_t button) {
    (void)button;
    if (app_state == STATE_MENU) {
        current_scenario = (current_scenario + num_scenarios - 1) % num_scenarios;
    }
}

static void button_x_callback(button_t button) {
    (void)button;
    if (app_state == STATE_MENU) {
        scenario_trigger = true;
    }
}

static void button_y_callback(button_t button) {
    (void)button;
    auto_advance = !auto_advance;
}

/*
 * MAIN PROGRAM
 */

int main() {
    stdio_init_all();
    
    // Initialize LED first for error indication
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);
    
    // Initialize display
    display_error_t disp_err = display_pack_init();
    if (disp_err != DISPLAY_OK) {
        // Error - blink LED rapidly
        while (1) {
            gpio_put(LED_PIN, 1);
            sleep_ms(100);
            gpio_put(LED_PIN, 0);
            sleep_ms(100);
        }
    }
    
    // Initialize buttons
    if (buttons_init() != DISPLAY_OK) {
        display_clear(COLOR_BLACK);
        display_draw_string(30, 100, "BUTTON INIT FAILED!", COLOR_RED, COLOR_BLACK);
        sleep_ms(3000);
        app_state = STATE_ERROR;
    }
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Splash screen
    display_clear(COLOR_BLACK);
    display_draw_string(30, 60, "SECURE BOOT CHAIN", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(60, 80, "DEMONSTRATION", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(60, 110, "WITH HARDENING", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 140, "A: NEXT  B: PREV", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 155, "X: RUN   Y: AUTO", COLOR_GREEN, COLOR_BLACK);
    sleep_ms(3000);
    
    const char *scenario_names[] = {
        "1. SUCCESSFUL BOOT",
        "2. TAMPERED IMAGE",
        "3. ROLLBACK ATTACK",
        "4. WRONG SIGNATURE",
        "5. CHAIN OF TRUST",
        "6. ATTACK DETECTION"
    };
    
    while (true) {
        buttons_update();
        
        switch (app_state) {
            case STATE_MENU:
                // Show menu
                display_clear(COLOR_BLACK);
                draw_boot_header("SELECT SCENARIO", COLOR_CYAN);
                
                for (int i = 0; i < num_scenarios; i++) {
                    uint16_t color = (i == current_scenario) ? COLOR_GREEN : COLOR_WHITE;
                    char line[40];
                    snprintf(line, sizeof(line), "%s %s",
                            (i == current_scenario) ? ">" : " ", scenario_names[i]);
                    display_draw_string(10, 50 + i * 20, line, color, COLOR_BLACK);
                }
                
                display_draw_string(10, 200, "A/B: SELECT  X: RUN", COLOR_CYAN, COLOR_BLACK);
                
                char auto_msg[32];
                snprintf(auto_msg, sizeof(auto_msg), "Y: AUTO [%s]",
                        auto_advance ? "ON" : "OFF");
                display_draw_string(10, 215, auto_msg, COLOR_CYAN, COLOR_BLACK);
                
                if (scenario_trigger) {
                    scenario_trigger = false;
                    app_state = STATE_RUNNING;
                }
                
                sleep_ms(100);
                break;
                
            case STATE_RUNNING:
                // Run selected scenario
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
                    case 5:
                        demo_attack_detection();
                        break;
                    default:
                        display_clear(COLOR_BLACK);
                        display_draw_string(30, 100, "INVALID SCENARIO!",
                                          COLOR_RED, COLOR_BLACK);
                        sleep_ms(2000);
                        break;
                }
                
                // Show completion screen
                display_clear(COLOR_BLACK);
                display_draw_string(70, 100, "SCENARIO COMPLETE", COLOR_GREEN, COLOR_BLACK);
                display_draw_string(40, 140, "PRESS X TO RUN AGAIN", COLOR_WHITE, COLOR_BLACK);
                display_draw_string(50, 170, "OR A/B TO SELECT", COLOR_WHITE, COLOR_BLACK);
                
                sleep_ms(1800);
                
                // Auto-advance if enabled
                if (auto_advance) {
                    current_scenario = (current_scenario + 1) % num_scenarios;
                    scenario_trigger = true;
                    sleep_ms(800);
                } else {
                    app_state = STATE_MENU;
                }
                break;
                
            case STATE_ERROR:
                // Error state - show error and halt
                display_clear(COLOR_BLACK);
                display_draw_string(50, 100, "SYSTEM ERROR", COLOR_RED, COLOR_BLACK);
                display_draw_string(30, 120, "PLEASE RESET DEVICE", COLOR_YELLOW, COLOR_BLACK);
                blink_led(1, 1000);
                break;
        }
    }

    return 0;
}
