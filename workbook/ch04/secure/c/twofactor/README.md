
> [!IMPORTANT]
> This examples requires out of the box two Raspberry Pi Pico W and a Pimironi Display
> Pack, or equivalent (you might wire your preferable LCD/OLED display). 


## Two-Factor Authentication with Raspberry Pi Pico W

This section outlines a practical two-factor authentication (2FA) system implemented
using two Raspberry Pi Pico W microcontrollers. The system demonstrates how low-cost
embedded devices can facilitate secure authentication through encrypted communication
and time-based one-time passwords (TOTPs). By combining "something you know" (password)
with "something you have" (hardware token), the system enhances security for user
authentication .. in a cost-effective and educational manner.


The __2FA__ system comprises three main components:

- *Authentication Server (Pico W #1)*: Hosts an HTTP web server that validates user
  credentials and 2FA tokens.

- *2FA Token Generator (Pico W #2)*: Acts as a hardware token, generating time-based
  authentication codes when triggered.

- *Client Device*: Sends encrypted credentials and 2FA codes to the server, typically
  via a user interface (e.g., a Python script running on a computer).



The authentication process follows these steps:

1. The user enters their username and password on the client device.
2. The client encrypts the credentials and sends them to the Authentication Server.
3. The server validates the password (first factor) and requests a 2FA token.
4. The user presses a button on the Token Generator (Pico W #2).
5. The Token Generator produces a time-based code and displays it (e.g., via console
   or an optional display).
6. The user inputs the 2FA code into the client.
7. The server verifies both the password and the 2FA code, granting or denying access
   accordingly.


### Authentication Server (Pico W #1)

The Authentication Server, running on the first Raspberry Pi Pico W, manages HTTP
requests, validates credentials, and verifies 2FA tokens. The code below implements
a simplified server with XOR encryption for demonstration purposes.


```c
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
```


### 2FA Token Generator (Pico W #2)

The second Raspberry Pi Pico W serves as a hardware token, generating TOTP codes
when a button is pressed. The code is displayed on the console (or could be shown
on an LCD/OLED display) -> Pimironi Display .. Later

```c
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/rtc.h"

// Hardware connections
#define BUTTON_PIN 15
#define LED_PIN 25

// Generate TOTP code (must match server implementation)
uint32_t generate_totp(uint32_t timestamp, const char *secret) {
    uint32_t time_step = timestamp / 30; // 30-second intervals
    uint32_t hash = 0;
    for (int i = 0; secret[i]; i++) {
        hash = hash * 31 + secret[i] + time_step;
    }
    return (hash % 900000) + 100000; // 6-digit code
}

// Display 2FA code on console (could use LCD/OLED display) .. drop USB
void display_totp_code(uint32_t code) {
    printf("\n");
    printf("--> 2FA TOKEN\n");
    printf("--> %06u \n", code);
    printf("--> Valid for 30 seconds\n");
    printf("\n");
}

// Blink LED to indicate code generation
void blink_led(int times) {
    for (int i = 0; i < times; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(150);
        gpio_put(LED_PIN, 0);
        sleep_ms(150);
    }
}

int main() {
    stdio_init_all();
    
    // Initialize GPIO
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);
    
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    // Initialize WiFi for time sync (optional)
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return -1;
    }
    
    printf("==> 2FA TOKEN GENERATOR\n");
    printf("==> Press button to generate code\n");
    
    bool last_button_state = true;
    uint32_t last_code_time = 0;
    
    // User database - in practice, this would be securely provisioned
    typedef struct {
        char username[32];
        char secret[32];
        int user_id;
    } token_user_t;
    
    token_user_t current_user = {"alice", "SECRET_KEY_ALICE", 0};
    
    while (1) {
        bool button_state = gpio_get(BUTTON_PIN);
        
        // Button pressed (falling edge)
        if (last_button_state && !button_state) {
            printf("Button pressed! Generating 2FA code ..\n");
            
            // Get current time (in real implementation, sync with NTP)
            uint32_t current_time = time(NULL);
            if (current_time == 0) {
                current_time = 1704067200; // Fallback: Jan 1, 2024
            }
            
            // Generate TOTP code
            uint32_t totp_code = generate_totp(current_time, current_user.secret);
            
            // Display the code
            printf("User: %s\n", current_user.username);
            display_totp_code(totp_code);
            
            // Indicate code generation with LED
            blink_led(3);
            
            // Show countdown
            printf("Code expires in: ");
            int remaining = 30 - (current_time % 30);
            for (int i = remaining; i > 0; i--) {
                printf("\rCode expires in: %2d seconds", i);
                fflush(stdout);
                sleep_ms(1000);
            }
            printf("\rCode expired!\n");
            
            last_code_time = current_time;
        }
        
        last_button_state = button_state;
        sleep_ms(50);
    }
    
    return 0;
}
```


### Client Implementation (Python Example)

The client, implemented in Python, encrypts user credentials and communicates
with the Authentication Server to perform the 2FA process.

```python
import requests
import getpass
import time

def xor_encrypt(data, key):
    """Simple XOR encryption matching Pico implementation"""
    key_bytes = key.encode()
    data_bytes = data.encode()
    encrypted = bytearray()
    
    for i, byte in enumerate(data_bytes):
        encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    return encrypted.decode('latin1')

def authenticate_2fa(server_url, username, password):
    """Perform 2FA authentication"""
    
    # Encrypt credentials
    encrypted_user = xor_encrypt(username, "SHARED_KEY")
    encrypted_pass = xor_encrypt(password, "SHARED_KEY")
    
    print(f"Connecting to {server_url}")
    
    # Step 1: Send first factor (username/password)
    try:
        response = requests.get(f"{server_url}/login", params={
            'user': encrypted_user,
            'pass': encrypted_pass
        }, timeout=5)
        
        result = response.json()
        
        if result['status'] == 'error':
            print(f"Authentication failed: {result['message']}")
            return False
            
        elif result['status'] == '2fa_required':
            print(f"First factor verified: {result['message']}")
            
            # Step 2: Get 2FA code from user
            print("\nPlease generate 2FA code on your hardware token..")
            totp_code = input("Enter 6-digit 2FA code: ").strip()
            
            # Send second factor
            response = requests.get(f"{server_url}/login", params={
                'user': encrypted_user,
                'pass': encrypted_pass,
                'totp': totp_code
            }, timeout=5)
            
            result = response.json()
            
            if result['status'] == 'success':
                print(f"{result['message']}")
                return True
            else:
                print(f"2FA failed: {result['message']}")
                return False

    except requests.RequestException as e:
        print(f"Connection error: {e}")
        return False
    
    return False

def access_protected_resource(server_url):
    """Access the protected dashboard"""
    try:
        response = requests.get(f"{server_url}/dashboard", timeout=5)
        if response.status_code == 200:
            print("Successfully accessed protected resource!")
            print("Dashboard content received.")
        else:
            print("Access denied to protected resource")
    except requests.RequestException as e:
        print(f"Error accessing resource: {e}")

def main():
    server_ip = input("Enter Pico server IP address: ").strip()
    if not server_ip:
        server_ip = "192.168.1.100"  # Default
    
    server_url = f"http://{server_ip}"
    
    print("..> 2FA CLIENT LOGIN")
    print("..> Connecting to Pico Auth Server")
    
    username = input("\nUsername: ")
    password = getpass.getpass("Password: ")
    
    if authenticate_2fa(server_url, username, password):
        access_protected_resource(server_url)
    else:
        print("Authentication failed!")

if __name__ == "__main__":
    main()
```


### Security Considerations

This implementation is designed for *educational purposes* and requires enhancements for
production use:

- *Encryption*: The XOR encryption used here is weak. Replace it with a robust algorithm
  like AES to secure credentials and communication.

- *TOTP Implementation*: The simplified TOTP function should be replaced with a proper
  HMAC-SHA1-based TOTP as per RFC 6238 for secure token generation.

- *Time Synchronisation*: Accurate time synchronisation via Network Time Protocol (NTP)
  is critical for TOTP to function correctly.

- *Secure Storage*: Store user secrets and credentials in a hardware security module or
  secure enclave, not in plaintext arrays.

- *Session Management*: Implement proper session tokens with timeouts to prevent unauthorised
  access after authentication.

- *HTTPS*: Use Transport Layer Security (TLS) for encrypted communication between the client
  and server.

- *Rate Limiting*: Add mechanisms to prevent brute-force attacks on the authentication endpoints.



This Raspberry Pi Pico W-based 2FA system offers several advantages:

- *Hardware Security*: The physical token (Pico W #2) cannot be remotely compromised, enhancing
  the "something you have" factor.

- *Offline Operation*: The token generator functions without network connectivity, making it
  resilient to network-based attacks.

- *Cost-Effective*: The system uses affordable Raspberry Pi Pico W boards, providing a low-cost
  alternative to commercial 2FA tokens.

- *Customizable*: The open-source nature allows organisations to tailor the system to specific
  requirements.

- *Educational Value*: The implementation demonstrates cryptographic principles like TOTP and
  secure communication in an accessible way.


This system illustrates how embedded devices can implement robust security protocols, making
it a learning tool and a foundation for developing secure authentication solutions.

