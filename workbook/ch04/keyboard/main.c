/*
Connects to WiFi using CYW43 (Pico W's WiFi chip).
Sets up a TCP server on port 80 using lwIP.
Handles incoming HTTP connections, parses POST requests to /keystrokes.
Extracts the JSON body with the hex-encoded encrypted data.
Decrypts using mbedtls AES-GCM (key must match client's; hardcoded here for demo—use secure storage in production).
Processes the keystrokes: For demo, prints to UART. To simulate USB keyboard, it uses TinyUSB to send HID reports (mapping chars to keycodes).
*/

#include <stdio.h>
#include <string.h>
#include <ctype.h>  // For tolower, isupper
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/tcp.h"
#include "lwip/dns.h"
#include "tusb.h"
#include "bsp/board.h"
#include "usb_descriptors.h"  // Create this file with descriptors below
#include "mbedtls/aes.h"
#include "wifi_credentials.h"  // #define WIFI_SSID, WIFI_PASSWORD

// Shared key (16 bytes for AES-128)
const uint8_t shared_key[16] = "mysecretkey12345";

// HID Report ID
enum {
    REPORT_ID_KEYBOARD = 1
};

// Keycode map (A-Z, space)
uint8_t char_to_hid(char c) {
    c = tolower(c);
    if (c >= 'a' && c <= 'z') return (HID_KEY_A + (c - 'a'));
    if (c == ' ') return HID_KEY_SPACE;
    return 0;
}

// Send HID key press (with modifier support)
void send_hid_key(uint8_t keycode, uint8_t modifier, bool press) {
    if (!tud_hid_ready()) return;  // Ensure ready
    if (press) {
        uint8_t keycodes[6] = {keycode, 0, 0, 0, 0, 0};
        tud_hid_keyboard_report(REPORT_ID_KEYBOARD, modifier, keycodes);
    } else {
        tud_hid_keyboard_report(REPORT_ID_KEYBOARD, 0, NULL);
    }
    sleep_ms(10);  // Small delay
}

// TCP recv callback
err_t recv_callback(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (!p) {
        tcp_close(tpcb);
        return ERR_OK;
    }

    char buf[2048];  // Larger buffer
    size_t len = pbuf_copy_partial(p, buf, sizeof(buf) - 1, 0);
    buf[len] = '\0';
    pbuf_free(p);

    if (strstr(buf, "POST /keystrokes HTTP/1.")) {
        char *body = strstr(buf, "\r\n\r\n");
        if (body) {
            body += 4;
            char *encrypted_start = strstr(body, "\"encrypted\":\"");
            if (encrypted_start) {
                encrypted_start += 13;
                char *encrypted_end = strchr(encrypted_start, '\"');
                if (encrypted_end) {
                    *encrypted_end = '\0';
                    size_t hex_len = strlen(encrypted_start);
                    if (hex_len % 2 != 0) goto error;
                    size_t bin_len = hex_len / 2;
                    uint8_t encrypted[bin_len];
                    for (size_t i = 0; i < bin_len; i++) {
                        if (sscanf(encrypted_start + 2 * i, "%2hhx", &encrypted[i]) != 1) goto error;
                    }

                    // Extract IV, ciphertext, tag
                    if (bin_len < 12 + 16) goto error;
                    uint8_t iv[12];
                    memcpy(iv, encrypted, 12);
                    size_t ct_len = bin_len - 12 - 16;
                    uint8_t ciphertext[ct_len];
                    memcpy(ciphertext, encrypted + 12, ct_len);
                    uint8_t tag[16];
                    memcpy(tag, encrypted + bin_len - 16, 16);

                    // Decrypt
                    mbedtls_aes_context aes;
                    mbedtls_aes_init(&aes);
                    int key_bits = 128;
                    mbedtls_aes_setkey_enc(&aes, shared_key, key_bits);  // Use enc for GCM decrypt
                    uint8_t decrypted[ct_len + 1];  // +1 for null
                    int ret = mbedtls_aes_crypt_gcm(&aes, MBEDTLS_AES_DECRYPT,
                                                    ct_len, iv, sizeof(iv),
                                                    NULL, 0,  // No AAD
                                                    ciphertext, decrypted,
                                                    tag, sizeof(tag));
                    mbedtls_aes_free(&aes);

                    if (ret == 0) {
                        decrypted[ct_len] = '\0';
                        printf("Decrypted keystrokes: %s\n", decrypted);

                        // Simulate HID typing
                        char *ks = (char *)decrypted;
                        for (size_t i = 0; ks[i]; i++) {
                            char c = ks[i];
                            uint8_t keycode = char_to_hid(c);
                            if (keycode) {
                                uint8_t modifier = isupper(c) ? KEYBOARD_MODIFIER_LEFTSHIFT : 0;
                                send_hid_key(keycode, modifier, true);   // Press
                                send_hid_key(keycode, modifier, false);  // Release
                            }
                        }
                    } else {
                        printf("Decryption failed: %d\n", ret);
                    }
                }
            }
        }
    }
error:
    const char *resp = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK";
    tcp_write(tpcb, resp, strlen(resp), TCP_WRITE_FLAG_COPY);
    tcp_close(tpcb);
    return ERR_OK;
}

err_t accept_callback(void *arg, struct tcp_pcb *newpcb, err_t err) {
    tcp_recv(newpcb, recv_callback);
    return ERR_OK;
}

int main() {
    stdio_init_all();
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return 1;
    }
    cyw43_arch_enable_sta_mode();
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("WiFi connect failed\n");
        return 1;
    }
    printf("WiFi connected, IP: %s\n", ip4addr_ntoa(&cyw43_state.netif[0].ip_addr));

    // Init TinyUSB
    board_init();
    tusb_init();

    // TCP server
    struct tcp_pcb *pcb = tcp_new_ip_type(IPADDR_TYPE_ANY);
    if (!pcb) return 1;
    err_t err = tcp_bind(pcb, IP_ANY_TYPE, 80);
    if (err != ERR_OK) return 1;
    pcb = tcp_listen_with_backlog(pcb, 1);
    if (!pcb) return 1;
    tcp_accept(pcb, accept_callback);

    while (1) {
        tud_task();  // USB task
        cyw43_arch_poll();  // WiFi poll
        sleep_ms(1);
    }
    return 0;
}
