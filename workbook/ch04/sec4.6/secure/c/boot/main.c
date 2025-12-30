/*
 * Secure Boot Chain Demonstration for Raspberry Pi Pico 2
 * 
 * This demonstrates a complete secure boot implementation showing:
 * - Root of Trust (RoT) in "ROM" (simulated)
 * - Digital signature verification (Ed25519)
 * - Chain of trust: Bootloader -> Application -> Module
 * - Rollback protection with version monotonic counters
 * - Flash write protection
 * - Secure upgrade mechanism
 * - Anti-downgrade protection
 * 
 * Educational Features:
 * - Shows why each stage verifies the next
 * - Demonstrates what happens when signatures fail
 * - Shows rollback attack prevention
 * - Illustrates defense-in-depth
 * 
 * Hardware Setup:
 * - LED on GPIO 25 (boot status)
 * - LED on GPIO 15 (security alert)
 * - Button on GPIO 14 (trigger updates/attacks)
 * - UART for detailed logging
 * 
 * Memory Layout (simulated):
 * 0x00000000 - 0x00003FFF: Root of Trust (RoT) - immutable
 * 0x00004000 - 0x0000BFFF: Bootloader
 * 0x0000C000 - 0x0001FFFF: Application
 * 0x00020000 - 0x0002FFFF: Module/Plugin
 * 0x00030000 - 0x00031FFF: Configuration/Metadata
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include "pico/time.h"

// GPIO Configuration
#define STATUS_LED_PIN 25
#define ALERT_LED_PIN 15
#define BUTTON_PIN 14

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
 * CRYPTOGRAPHIC PRIMITIVES (Simplified Ed25519-style)
 */

// Simplified public key structure
typedef struct {
    uint8_t data[PUBLIC_KEY_SIZE];
    char name[32];
} public_key_t;

// Simplified signature structure
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

// Simple hash function (educational - use SHA256 in production)
void simple_hash(const uint8_t *data, size_t len, uint8_t *hash) {
    // Initialize hash with constant
    uint32_t h[8] = {
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    };
    
    // Very simplified hash (for demo only!)
    for (size_t i = 0; i < len; i++) {
        h[i % 8] ^= data[i];
        h[i % 8] = (h[i % 8] << 7) | (h[i % 8] >> 25);
        h[i % 8] += data[i] * 31;
    }
    
    // Output hash
    for (int i = 0; i < 8; i++) {
        hash[i*4 + 0] = (h[i] >> 24) & 0xFF;
        hash[i*4 + 1] = (h[i] >> 16) & 0xFF;
        hash[i*4 + 2] = (h[i] >> 8) & 0xFF;
        hash[i*4 + 3] = h[i] & 0xFF;
    }
}

// Simplified signature verification (educational)
bool verify_signature(const uint8_t *data, size_t len, 
                     const signature_t *sig, 
                     const public_key_t *pubkey) {
    uint8_t hash[HASH_SIZE];
    simple_hash(data, len, hash);
    
    // Simplified verification: check if signature matches hash XOR pubkey
    // (In real Ed25519, this is complex elliptic curve math)
    uint8_t expected[SIGNATURE_SIZE];
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        expected[i] = hash[i % HASH_SIZE] ^ pubkey->data[i % PUBLIC_KEY_SIZE];
    }
    
    // Constant-time comparison
    uint8_t diff = 0;
    for (int i = 0; i < SIGNATURE_SIZE; i++) {
        diff |= (sig->data[i] ^ expected[i]);
    }
    
    return (diff == 0);
}

// Generate signature (for creating test images)
void sign_data(const uint8_t *data, size_t len, 
               signature_t *sig, 
               const public_key_t *pubkey) {
    uint8_t hash[HASH_SIZE];
    simple_hash(data, len, hash);
    
    // Create signature
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

// Version counter storage (simulated NVM)
static uint32_t version_counters[3] = {0, 0, 0};  // BL, APP, MOD

// PENDING :::::
