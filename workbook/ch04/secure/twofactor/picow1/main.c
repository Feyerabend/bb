#include <stdio.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/apps/httpd.h"

// Simple XOR encryption for demonstration
void xor_encrypt_decrypt(char *data, const char *key, size_t len) {
    size_t key_len = strlen(key);
    for (size_t i = 0; i < len; i++) {
        data[i] ^= key[i % key_len];
    }
}

// Time-based token generator (shared secret with Token Generator)
uint32_t generate_totp(uint32_t timestamp, const char *secret) {
    // Simplified TOTP - real implementation would use HMAC-SHA1
    uint32_t time_step = timestamp / 30; // 30-second intervals
    uint32_t hash = 0;
    for (int i = 0; secret[i]; i++) {
        hash = hash * 31 + secret[i] + time_step;
    }
    return (hash % 900000) + 100000; // 6-digit code
}

// User database (in practice, use secure storage)
typedef struct {
    char username[32];
    char password[32];
    char totp_secret[32];
    bool logged_in;
} user_t;

user_t users[] = {
    {"alice", "password123", "SECRET_KEY_ALICE", false},
    {"bob", "mypassword", "SECRET_KEY_BOB", false}
};

const int num_users = sizeof(users) / sizeof(users[0]);

// HTTP handler for login attempts
const char* login_handler(int iIndex, int iNumParams, char *pcParam[], char *pcValue[]) {
    static char response[1024];
    char username[64] = {0};
    char password[64] = {0};
    char totp_code[16] = {0};
    bool has_totp = false;
    
    // Parse encrypted parameters
    for (int i = 0; i < iNumParams; i++) {
        if (strcmp(pcParam[i], "user") == 0) {
            strcpy(username, pcValue[i]);
            xor_encrypt_decrypt(username, "SHARED_KEY", strlen(username));
        } else if (strcmp(pcParam[i], "pass") == 0) {
            strcpy(password, pcValue[i]);
            xor_encrypt_decrypt(password, "SHARED_KEY", strlen(password));
        } else if (strcmp(pcParam[i], "totp") == 0) {
            strcpy(totp_code, pcValue[i]);
            has_totp = true;
        }
    }
    
    printf("Login attempt: user=%s\n", username);
    
    // Find user and validate first factor (password)
    user_t *user = NULL;
    for (int i = 0; i < num_users; i++) {
        if (strcmp(users[i].username, username) == 0) {
            user = &users[i];
            break;
        }
    }
    
    if (!user || strcmp(user->password, password) != 0) {
        snprintf(response, sizeof(response),
            "HTTP/1.1 401 Unauthorized\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"error\",\"message\":\"Invalid credentials\"}");
        return response;
    }
    
    // First factor passed - check if 2FA is required
    if (!has_totp) {
        snprintf(response, sizeof(response),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"2fa_required\",\"message\":\"Please enter 2FA code\"}");
        return response;
    }
    
    // Validate 2FA token
    uint32_t current_time = time(NULL);
    uint32_t expected_totp = generate_totp(current_time, user->totp_secret);
    uint32_t provided_totp = atoi(totp_code);
    
    // Allow some time drift (±30 seconds)
    bool totp_valid = (provided_totp == expected_totp) ||
                      (provided_totp == generate_totp(current_time - 30, user->totp_secret)) ||
                      (provided_totp == generate_totp(current_time + 30, user->totp_secret));
    
    if (totp_valid) {
        user->logged_in = true;
        snprintf(response, sizeof(response),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"success\",\"message\":\"Authentication successful!\"}");
        printf("User %s authenticated successfully\n", username);
    } else {
        snprintf(response, sizeof(response),
            "HTTP/1.1 401 Unauthorized\r\n"
            "Content-Type: application/json\r\n\r\n"
            "{\"status\":\"error\",\"message\":\"Invalid 2FA code\"}");
        printf("Invalid 2FA code for user %s: got %u, expected %u\n", 
               username, provided_totp, expected_totp);
    }
    
    return response;
}

// HTTP handler for protected resource
const char* dashboard_handler(int iIndex, int iNumParams, char *pcParam[], char *pcValue[]) {
    static char response[2048];
    
    // Check if any user is logged in (simplified session management)
    bool authenticated = false;
    for (int i = 0; i < num_users; i++) {
        if (users[i].logged_in) {
            authenticated = true;
            break;
        }
    }
    
    if (authenticated) {
        snprintf(response, sizeof(response),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n\r\n"
            "<html><body>"
            "<h1>Secure Dashboard</h1>"
            "<p>Welcome! You have successfully authenticated with 2FA.</p>"
            "<p>This is a protected resource only accessible after two-factor authentication.</p>"
            "<button onclick='logout()'>Logout</button>"
            "</body></html>");
    } else {
        snprintf(response, sizeof(response),
            "HTTP/1.1 401 Unauthorized\r\n"
            "Content-Type: text/html\r\n\r\n"
            "<html><body>"
            "<h1>Access Denied</h1>"
            "<p>Please log in with valid credentials and 2FA token.</p>"
            "<a href='/'>Login</a>"
            "</body></html>");
    }
    
    return response;
}

int main() {
    stdio_init_all();
    
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return -1;
    }
    
    cyw43_arch_enable_sta_mode();
    
    // Connect to WiFi
    printf("Connecting to WiFi..\n");
    if (cyw43_arch_wifi_connect_timeout("YOUR_SSID", "YOUR_PASSWORD", CYW43_AUTH_WPA2_AES_PSK, 10000)) {
        printf("WiFi connection failed\n");
        return -1;
    }
    
    printf("WiFi connected! Starting HTTP server..\n");
    printf("Authentication Server ready at: http://%s/\n", ip4addr_ntoa(netif_ip4_addr(netif_list)));
    
    // Init HTTP server
    httpd_init();
    
    // Register HTTP handlers
    http_set_ssi_handler(login_handler, "/login", 1);
    http_set_ssi_handler(dashboard_handler, "/dashboard", 1);
    
    // Main server loop
    while (1) {
        cyw43_arch_poll();
        sleep_ms(10);
    }
    
    return 0;
}

