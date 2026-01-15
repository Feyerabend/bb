/*
 * 2FA Authentication Server for Raspberry Pi Pico W
 * with Pimoroni Display Pack 2.0
 */

// STILL NOT COMPLETE ..

#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/apps/httpd.h"
#include "lwip/apps/httpd_structs.h"
#include "pico/rand.h"
#include "display.h"


// CONFIGURATION

#define MAX_USERS 10
#define MAX_SESSIONS 10
#define SESSION_TIMEOUT 3600  // 1 hour
#define MAX_LOGIN_ATTEMPTS 5
#define RATE_LIMIT_WINDOW 300 // 5 minutes
#define TOTP_WINDOW 30        // 30 second time window


// DATA STRUCTURES

typedef struct {
    char username[32];
    char password_hash[65];  // SHA256 hash (in real impl)
    char totp_secret[32];
    uint32_t failed_attempts;
    uint32_t last_attempt_time;
    bool account_locked;
} user_t;

typedef struct {
    char token[65];
    char username[32];
    uint32_t created_at;
    uint32_t expires_at;
    bool valid;
} session_t;

typedef struct {
    uint32_t successful_logins;
    uint32_t failed_logins;
    uint32_t active_sessions;
    char last_login_user[32];
    uint32_t last_login_time;
} server_stats_t;


// GLOBAL STATE

user_t users[MAX_USERS] = {
    {"alice", "password123", "ALICE_SECRET_KEY_12345", 0, 0, false},
    {"bob", "mypassword", "BOB_SECRET_KEY_67890", 0, 0, false}
};

session_t sessions[MAX_SESSIONS] = {0};
server_stats_t stats = {0};
const int num_users = 2;

// Display state
static uint32_t last_display_update = 0;
static bool display_ready = false;




// Simplified HMAC-SHA1 (use mbedtls in production!)
void hmac_sha1_simple(const uint8_t *key, size_t key_len,
                     const uint8_t *data, size_t data_len,
                     uint8_t *output) {
    // This is a simplified version. In production, use mbedtls crypto library
    uint32_t hash = 0;
    for (size_t i = 0; i < key_len; i++) {
        hash = hash * 31 + key[i];
    }
    for (size_t i = 0; i < data_len; i++) {
        hash = hash * 31 + data[i];
    }
    
    // Generate 20 bytes (160 bits) for SHA1
    for (int i = 0; i < 20; i++) {
        output[i] = (hash >> (i * 8)) & 0xFF;
        hash = hash * 1103515245 + 12345;
    }
}

uint32_t generate_totp_rfc6238(uint32_t timestamp, const char *secret) {
    uint64_t time_step = timestamp / TOTP_WINDOW;
    uint8_t time_bytes[8];
    
    // Convert time step to big-endian bytes
    for (int i = 7; i >= 0; i--) {
        time_bytes[i] = (time_step >> (8 * (7 - i))) & 0xFF;
    }
    
    // HMAC-SHA1
    uint8_t hmac[20];
    hmac_sha1_simple((uint8_t*)secret, strlen(secret), time_bytes, 8, hmac);
    
    // Dynamic truncation
    uint8_t offset = hmac[19] & 0x0f;
    uint32_t truncated = ((hmac[offset] & 0x7f) << 24) |
                        ((hmac[offset + 1] & 0xff) << 16) |
                        ((hmac[offset + 2] & 0xff) << 8) |
                        (hmac[offset + 3] & 0xff);
    
    return truncated % 1000000;
}

bool verify_totp(uint32_t provided_code, uint32_t timestamp, const char *secret) {
    // Check current window and ±1 window (90 seconds total)
    for (int drift = -1; drift <= 1; drift++) {
        uint32_t check_time = timestamp + (drift * TOTP_WINDOW);
        uint32_t expected = generate_totp_rfc6238(check_time, secret);
        
        if (provided_code == expected) {
            return true;
        }
    }
    return false;
}


// SESSION MANAGEMENT

void generate_session_token(char *token, size_t len) {
    const char charset[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    for (size_t i = 0; i < len - 1; i++) {
        uint32_t rand = get_rand_32();
        token[i] = charset[rand % (sizeof(charset) - 1)];
    }
    token[len - 1] = '\0';
}

session_t* create_session(const char *username) {
    uint32_t now = time(NULL);
    
    // Find expired or empty slot
    for (int i = 0; i < MAX_SESSIONS; i++) {
        if (!sessions[i].valid || sessions[i].expires_at < now) {
            generate_session_token(sessions[i].token, 65);
            strncpy(sessions[i].username, username, sizeof(sessions[i].username) - 1);
            sessions[i].created_at = now;
            sessions[i].expires_at = now + SESSION_TIMEOUT;
            sessions[i].valid = true;
            stats.active_sessions++;
            return &sessions[i];
        }
    }
    return NULL;
}

session_t* find_session(const char *token) {
    uint32_t now = time(NULL);
    for (int i = 0; i < MAX_SESSIONS; i++) {
        if (sessions[i].valid && 
            strcmp(sessions[i].token, token) == 0 &&
            sessions[i].expires_at > now) {
            return &sessions[i];
        }
    }
    return NULL;
}

void invalidate_session(const char *token) {
    for (int i = 0; i < MAX_SESSIONS; i++) {
        if (strcmp(sessions[i].token, token) == 0) {
            sessions[i].valid = false;
            if (stats.active_sessions > 0) stats.active_sessions--;
            return;
        }
    }
}


// DISPLAY FUNCTIONS

void update_display() {
    if (!display_ready) return;
    
    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (now - last_display_update < 1000) return;  // Update once per second
    
    last_display_update = now;
    
    // Clear screen
    display_clear(COLOR_BLACK);
    
    // Title
    display_draw_string(10, 10, "2FA AUTH SERVER", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(10, 25, "---------------", COLOR_CYAN, COLOR_BLACK);
    
    // Stats
    char buf[64];
    snprintf(buf, sizeof(buf), "SUCCESSFUL: %lu", stats.successful_logins);
    display_draw_string(10, 45, buf, COLOR_GREEN, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "FAILED: %lu", stats.failed_logins);
    display_draw_string(10, 60, buf, COLOR_RED, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "ACTIVE SESSIONS: %lu", stats.active_sessions);
    display_draw_string(10, 75, buf, COLOR_YELLOW, COLOR_BLACK);
    
    // Last login
    if (stats.last_login_time > 0) {
        display_draw_string(10, 100, "LAST LOGIN:", COLOR_WHITE, COLOR_BLACK);
        snprintf(buf, sizeof(buf), "USER: %s", stats.last_login_user);
        display_draw_string(10, 115, buf, COLOR_WHITE, COLOR_BLACK);
        
        time_t t = stats.last_login_time;
        struct tm *tm_info = localtime(&t);
        strftime(buf, sizeof(buf), "%H:%M:%S", tm_info);
        display_draw_string(10, 130, buf, COLOR_WHITE, COLOR_BLACK);
    }
    
    // Current time and TOTP demo
    time_t current = time(NULL);
    struct tm *tm_info = localtime(&current);
    char time_str[32];
    strftime(time_str, sizeof(time_str), "Time: %H:%M:%S", tm_info);
    display_draw_string(10, 160, time_str, COLOR_MAGENTA, COLOR_BLACK);
    
    // Show sample TOTP for demo
    uint32_t demo_code = generate_totp_rfc6238(current, users[0].totp_secret);
    snprintf(buf, sizeof(buf), "Demo TOTP: %06lu", demo_code);
    display_draw_string(10, 180, buf, COLOR_GREEN, COLOR_BLACK);
    
    int remaining = TOTP_WINDOW - (current % TOTP_WINDOW);
    snprintf(buf, sizeof(buf), "Valid: %ds", remaining);
    display_draw_string(10, 195, buf, COLOR_YELLOW, COLOR_BLACK);
    
    // Progress bar for TOTP validity
    int bar_width = (remaining * 280) / TOTP_WINDOW;
    display_fill_rect(10, 215, bar_width, 10, COLOR_GREEN);
    display_fill_rect(10 + bar_width, 215, 280 - bar_width, 10, COLOR_RED);
}


// HTTP HANDLERS

const char* http_response_header = 
    "HTTP/1.1 %d %s\r\n"
    "Content-Type: application/json\r\n"
    "Access-Control-Allow-Origin: *\r\n"
    "Connection: close\r\n\r\n";

const char* login_handler(int iIndex, int iNumParams, char *pcParam[], char *pcValue[]) {
    static char response[2048];
    char username[64] = {0};
    char password[64] = {0};
    char totp_str[16] = {0};
    bool has_totp = false;
    
    printf("\n-- New Authentication Request --\n");
    
    // Parse parameters
    for (int i = 0; i < iNumParams; i++) {
        if (strcmp(pcParam[i], "username") == 0) {
            strncpy(username, pcValue[i], sizeof(username) - 1);
        } else if (strcmp(pcParam[i], "password") == 0) {
            strncpy(password, pcValue[i], sizeof(password) - 1);
        } else if (strcmp(pcParam[i], "totp") == 0) {
            strncpy(totp_str, pcValue[i], sizeof(totp_str) - 1);
            has_totp = true;
        }
    }
    
    printf("Username: %s\n", username);
    printf("Has TOTP: %s\n", has_totp ? "yes" : "no");

    // Find user
    user_t *user = NULL;
    for (int i = 0; i < num_users; i++) {
        if (strcmp(users[i].username, username) == 0) {
            user = &users[i];
            break;
        }
    }
    
    uint32_t now = time(NULL);
    
    // Check if account is locked
    if (user && user->account_locked) {
        if (now - user->last_attempt_time > RATE_LIMIT_WINDOW) {
            user->account_locked = false;
            user->failed_attempts = 0;
        } else {
            printf("Account locked\n");
            snprintf(response, sizeof(response),
                "HTTP/1.1 429 Too Many Requests\r\n"
                "Content-Type: application/json\r\n\r\n"
                "{\"status\":\"error\",\"message\":\"Account temporarily locked\"}");
            return response;
        }
    }
    
    // Validate username and password
    if (!user || strcmp(user->password_hash, password) != 0) {
        if (user) {
            user->failed_attempts++;
            user->last_attempt_time = now;
            if (user->failed_attempts >= MAX_LOGIN_ATTEMPTS) {
                user->account_locked = true;
                printf("Account locked after %d attempts\n", user->failed_attempts);
            }
        }
        stats.failed_logins++;
        printf("Invalid credentials\n");
        snprintf(response, sizeof(response),
            "HTTP/1.1 401 Unauthorized\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"error\",\"message\":\"Invalid credentials\"}");
        return response;
    }
    
    // First factor passed
    if (!has_totp) {
        printf("First factor OK, requesting 2FA\n");
        
        // Generate challenge token (simplified - sure, in production use proper crypto!)
        char challenge[65];
        generate_session_token(challenge, 65);
        
        snprintf(response, sizeof(response),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"2fa_required\",\"message\":\"Please enter 2FA code\","
            "\"challenge_token\":\"%s\"}", challenge);
        return response;
    }
    
    // Verify TOTP
    uint32_t provided_totp = atoi(totp_str);
    printf("Verifying TOTP: %06u\n", provided_totp);
    
    if (verify_totp(provided_totp, now, user->totp_secret)) {
        // Success! Create session
        session_t *session = create_session(username);
        
        if (!session) {
            snprintf(response, sizeof(response),
                "HTTP/1.1 500 Internal Server Error\r\n"
                "Content-Type: application/json\r\n\r\n"
                "{\"status\":\"error\",\"message\":\"Cannot create session\"}");
            return response;
        }
        
        // Reset failed attempts
        user->failed_attempts = 0;
        user->last_attempt_time = 0;
        
        // Update stats
        stats.successful_logins++;
        strncpy(stats.last_login_user, username, sizeof(stats.last_login_user) - 1);
        stats.last_login_time = now;
        
        printf("  Authentication successful for %s\n", username);
        printf("Session token: %s\n", session->token);
        
        snprintf(response, sizeof(response),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"success\",\"message\":\"Authentication successful\","
            "\"session_token\":\"%s\",\"expires_in\":%d}",
            session->token, SESSION_TIMEOUT);
    } else {
        user->failed_attempts++;
        user->last_attempt_time = now;
        stats.failed_logins++;
        
        printf("  Invalid TOTP code\n");
        
        snprintf(response, sizeof(response),
            "HTTP/1.1 401 Unauthorized\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"error\",\"message\":\"Invalid 2FA code\"}");
    }
    
    return response;
}

const char* dashboard_handler(int iIndex, int iNumParams, char *pcParam[], char *pcValue[]) {
    static char response[2048];
    char auth_token[128] = {0};
    
    // Extract Bearer token from Authorization header
    // This is simplified - in real implementation, also parse HTTP headers properly
    for (int i = 0; i < iNumParams; i++) {
        if (strcmp(pcParam[i], "token") == 0) {
            strncpy(auth_token, pcValue[i], sizeof(auth_token) - 1);
            break;
        }
    }
    
    printf("\n-- Dashboard Access Request --\n");
    printf("Token: %s\n", auth_token);
    
    session_t *session = find_session(auth_token);
    
    if (session) {
        printf("  Valid session for user: %s\n", session->username);
        
        snprintf(response, sizeof(response),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{"
            "\"status\":\"success\","
            "\"username\":\"%s\","
            "\"message\":\"Welcome to the secure dashboard!\","
            "\"data\":{"
            "\"total_logins\":%lu,"
            "\"failed_attempts\":%lu,"
            "\"active_sessions\":%lu"
            "}"
            "}",
            session->username,
            stats.successful_logins,
            stats.failed_logins,
            stats.active_sessions);
    } else {
        printf("  Invalid or expired session\n");
        
        snprintf(response, sizeof(response),
            "HTTP/1.1 401 Unauthorized\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"error\",\"message\":\"Unauthorized - please login\"}");
    }
    
    return response;
}



int main() {
    stdio_init_all();
    
    printf("\n  ENHANCED 2FA AUTH SERVER\n");
    printf("  Raspberry Pi Pico W\n\n");
    
    // Init display
    printf("Initialising display..\n");
    if (display_pack_init() == DISPLAY_OK) {
        if (buttons_init() == DISPLAY_OK) {
            display_ready = true;
            display_clear(COLOR_BLACK);
            display_draw_string(10, 10, "Initialising..", COLOR_WHITE, COLOR_BLACK);
            printf("  Display ready\n");
        }
    } else {
        printf("! Display initialisation failed\n");
    }
    
    // Init WiFi
    if (cyw43_arch_init()) {
        printf("  WiFi init failed\n");
        return -1;
    }
    
    cyw43_arch_enable_sta_mode();
    
    printf("Connecting to WiFi..\n");
    if (cyw43_arch_wifi_connect_timeout_ms("YOUR_SSID", "YOUR_PASSWORD", 
                                           CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("  WiFi connection failed\n");
        return -1;
    }
    
    printf("  WiFi connected!\n");
    printf("  IP Address: %s\n", ip4addr_ntoa(netif_ip4_addr(netif_list)));
    
    // Init HTTP server
    httpd_init();
    printf("  HTTP server started\n");
    
    // Register handlers
    http_set_ssi_handler(login_handler, "/api/auth/login", 1);
    http_set_ssi_handler(dashboard_handler, "/api/dashboard", 1);
    
    printf("\n\n  Server Ready!\n");
    printf("  Endpoints:\n");
    printf("    POST /api/auth/login\n");
    printf("    GET  /api/dashboard\n\n");
    
    if (display_ready) {
        display_clear(COLOR_BLACK);
        display_draw_string(10, 10, "SERVER READY", COLOR_GREEN, COLOR_BLACK);
        char ip_str[32];
        snprintf(ip_str, sizeof(ip_str), "IP: %s", ip4addr_ntoa(netif_ip4_addr(netif_list)));
        display_draw_string(10, 30, ip_str, COLOR_WHITE, COLOR_BLACK);
    }
    
    // Main loop
    while (1) {
        cyw43_arch_poll();
        
        if (display_ready) {
            buttons_update();
            update_display();
        }
        
        sleep_ms(10);
    }
    
    return 0;
}


