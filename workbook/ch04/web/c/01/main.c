#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/tcp.h"
#include "lwip/ip4_addr.h"
#include "lwip/netif.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

#define TCP_PORT 80
#define DEBUG_printf printf
#define BUF_SIZE 2048

// Display Pack 2.0 pin definitions
#define DISPLAY_CS_PIN 9
#define DISPLAY_CLK_PIN 10
#define DISPLAY_MOSI_PIN 11
#define DISPLAY_DC_PIN 8
#define DISPLAY_RESET_PIN 12
#define DISPLAY_BL_PIN 13

// Button pins on Display Pack 2.0
#define BUTTON_A_PIN 14
#define BUTTON_B_PIN 15
#define BUTTON_X_PIN 16
#define BUTTON_Y_PIN 17

// Display dimensions for ST7789 240x135
#define DISPLAY_WIDTH 240
#define DISPLAY_HEIGHT 135

// Access Point settings
const char AP_SSID[] = "PicoW-Display";
const char AP_PASSWORD[] = "12345678";

// Colors (RGB565 format)
#define COLOR_BLACK     0x0000
#define COLOR_WHITE     0xFFFF
#define COLOR_RED       0xF800
#define COLOR_GREEN     0x07E0
#define COLOR_BLUE      0x001F
#define COLOR_YELLOW    0xFFE0
#define COLOR_CYAN      0x07FF
#define COLOR_MAGENTA   0xF81F

// Global state variables
static int request_count = 0;
static char last_request[100] = "NONE";
static char server_status[50] = "STARTING...";
static const char ip_address[] = "192.168.4.1";

// TCP server structures
typedef struct TCP_SERVER_T_ {
    struct tcp_pcb *server_pcb;
    bool complete;
} TCP_SERVER_T;

typedef struct TCP_CONNECT_STATE_T_ {
    struct tcp_pcb *pcb;
    int sent_len;
    char headers[BUF_SIZE];
    char result[BUF_SIZE];
    int header_len;
    int result_len;
} TCP_CONNECT_STATE_T;



// Simple 5x8 font (subset for common characters)
static const uint8_t font5x8[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // Space (32)
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // ! (33)
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, // A (65)
    {0x7F, 0x49, 0x49, 0x49, 0x36}, // B (66)
    {0x3E, 0x41, 0x41, 0x41, 0x22}, // C (67)
    {0x7F, 0x41, 0x41, 0x22, 0x1C}, // D (68)
    {0x7F, 0x49, 0x49, 0x49, 0x41}, // E (69)
    {0x7F, 0x09, 0x09, 0x09, 0x01}, // F (70)
    {0x3E, 0x41, 0x49, 0x49, 0x7A}, // G (71)
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, // H (72)
    {0x00, 0x41, 0x7F, 0x41, 0x00}, // I (73)
    {0x7F, 0x08, 0x14, 0x22, 0x41}, // K (75)
    {0x7F, 0x40, 0x40, 0x40, 0x40}, // L (76)
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // M (77)
    {0x7F, 0x04, 0x08, 0x10, 0x7F}, // N (78)
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, // O (79)
    {0x7F, 0x09, 0x09, 0x09, 0x06}, // P (80)
    {0x7F, 0x09, 0x19, 0x29, 0x46}, // R (82)
    {0x46, 0x49, 0x49, 0x49, 0x31}, // S (83)
    {0x01, 0x01, 0x7F, 0x01, 0x01}, // T (84)
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, // U (85)
    {0x1F, 0x20, 0x40, 0x20, 0x1F}, // V (86)
    {0x3F, 0x40, 0x38, 0x40, 0x3F}, // W (87)
    {0x63, 0x14, 0x08, 0x14, 0x63}, // X (88)
    {0x07, 0x08, 0x70, 0x08, 0x07}, // Y (89)
    {0x20, 0x10, 0x08, 0x04, 0x02}, // / (47)
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, // 0 (48)
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // 1 (49)
    {0x42, 0x61, 0x51, 0x49, 0x46}, // 2 (50)
    {0x21, 0x41, 0x45, 0x4B, 0x31}, // 3 (51)
    {0x18, 0x14, 0x12, 0x7F, 0x10}, // 4 (52)
    {0x27, 0x45, 0x45, 0x45, 0x39}, // 5 (53)
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, // 6 (54)
    {0x01, 0x71, 0x09, 0x05, 0x03}, // 7 (55)
    {0x36, 0x49, 0x49, 0x49, 0x36}, // 8 (56)
    {0x06, 0x49, 0x49, 0x29, 0x1E}, // 9 (57)
    {0x00, 0x36, 0x36, 0x00, 0x00}, // : (58)
    {0x00, 0x60, 0x60, 0x00, 0x00}, // . (46)
    {0x08, 0x08, 0x08, 0x08, 0x08}, // - (45)
};

void display_write_command(uint8_t cmd) {
    gpio_put(DISPLAY_DC_PIN, 0);
    gpio_put(DISPLAY_CS_PIN, 0);
    spi_write_blocking(spi1, &cmd, 1);
    gpio_put(DISPLAY_CS_PIN, 1);
}

void display_write_data(uint8_t data) {
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_CS_PIN, 0);
    spi_write_blocking(spi1, &data, 1);
    gpio_put(DISPLAY_CS_PIN, 1);
}

void display_init() {
    // Initialize SPI1 for Display Pack 2.0
    spi_init(spi1, 10000000); // 10MHz
    gpio_set_function(DISPLAY_CLK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(DISPLAY_MOSI_PIN, GPIO_FUNC_SPI);
    
    // Initialize control pins
    gpio_init(DISPLAY_CS_PIN);
    gpio_init(DISPLAY_DC_PIN);
    gpio_init(DISPLAY_RESET_PIN);
    gpio_init(DISPLAY_BL_PIN);
    
    gpio_set_dir(DISPLAY_CS_PIN, GPIO_OUT);
    gpio_set_dir(DISPLAY_DC_PIN, GPIO_OUT);
    gpio_set_dir(DISPLAY_RESET_PIN, GPIO_OUT);
    gpio_set_dir(DISPLAY_BL_PIN, GPIO_OUT);
    
    // Initialize pins
    gpio_put(DISPLAY_CS_PIN, 1);
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_BL_PIN, 1); // Turn on backlight
    
    // Hardware reset
    gpio_put(DISPLAY_RESET_PIN, 1);
    sleep_ms(5);
    gpio_put(DISPLAY_RESET_PIN, 0);
    sleep_ms(20);
    gpio_put(DISPLAY_RESET_PIN, 1);
    sleep_ms(150);
    
    // ST7789 initialization for Display Pack 2.0
    display_write_command(0x01); // SWRESET
    sleep_ms(150);
    
    display_write_command(0x11); // SLPOUT
    sleep_ms(120);
    
    display_write_command(0x3A); // COLMOD
    display_write_data(0x55);    // 16-bit RGB565
    
    display_write_command(0x36); // MADCTL - Memory Access Control
    display_write_data(0x00);    // Standard orientation for Display Pack 2.0
    
    display_write_command(0x21); // INVON
    display_write_command(0x13); // NORON
    display_write_command(0x29); // DISPON
    sleep_ms(100);
    
    DEBUG_printf("Display initialized (Pack 2.0 - 240x360)\n");
}

void display_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    display_write_command(0x2A); // CASET
    display_write_data(x0 >> 8);
    display_write_data(x0 & 0xFF);
    display_write_data(x1 >> 8);
    display_write_data(x1 & 0xFF);
    
    display_write_command(0x2B); // RASET
    display_write_data(y0 >> 8);
    display_write_data(y0 & 0xFF);
    display_write_data(y1 >> 8);
    display_write_data(y1 & 0xFF);
    
    display_write_command(0x2C); // RAMWR
}

void display_fill_rect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color) {
    if (x >= DISPLAY_WIDTH || y >= DISPLAY_HEIGHT) return;
    if (x + width > DISPLAY_WIDTH) width = DISPLAY_WIDTH - x;
    if (y + height > DISPLAY_HEIGHT) height = DISPLAY_HEIGHT - y;
    
    display_set_window(x, y, x + width - 1, y + height - 1);
    
    uint8_t color_bytes[2] = {color >> 8, color & 0xFF};
    gpio_put(DISPLAY_DC_PIN, 1);
    gpio_put(DISPLAY_CS_PIN, 0);
    
    for (uint32_t i = 0; i < width * height; i++) {
        spi_write_blocking(spi1, color_bytes, 2);
    }
    
    gpio_put(DISPLAY_CS_PIN, 1);
}

void display_clear(uint16_t color) {
    display_fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color);
}

void display_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg_color) {
    // Simple character mapping for basic chars
    int font_index = -1;
    
    if (c == ' ') font_index = 0;
    else if (c == '!') font_index = 1;
    else if (c >= 'A' && c <= 'Y') font_index = c - 'A' + 2;
    else if (c == '/') font_index = 20;
    else if (c >= '0' && c <= '9') font_index = c - '0' + 21;
    else if (c == ':') font_index = 31;
    else if (c == '.') font_index = 32;
    else if (c == '-') font_index = 33;
    else font_index = 0; // Default to space
    
    const uint8_t *char_data = font5x8[font_index];
    
    for (int col = 0; col < 5; col++) {
        uint8_t line = char_data[col];
        for (int row = 0; row < 8; row++) {
            uint16_t pixel_color = (line & (0x80 >> row)) ? color : bg_color;
            if (x + col < DISPLAY_WIDTH && y + row < DISPLAY_HEIGHT) {
                display_fill_rect(x + col, y + row, 1, 1, pixel_color);
            }
        }
    }
}

void display_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg_color) {
    int offset_x = 0;
    while (*str && x + offset_x < DISPLAY_WIDTH) {
        display_draw_char(x + offset_x, y, *str, color, bg_color);
        offset_x += 6; // 5 pixel font + 1 pixel spacing
        str++;
    }
}

void display_update_status() {
    display_clear(COLOR_BLACK);
    
    // Title
    display_draw_string(10, 5, "PICO W ACCESS POINT", COLOR_WHITE, COLOR_BLACK);
    
    // Status
    char status_line[40];
    snprintf(status_line, sizeof(status_line), "STATUS: %s", server_status);
    display_draw_string(5, 25, status_line, COLOR_GREEN, COLOR_BLACK);
    
    // Network info
    display_draw_string(5, 45, "SSID: PICOW-DISPLAY", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(5, 60, "IP: 192.168.4.1", COLOR_CYAN, COLOR_BLACK);
    
    // Stats
    char req_line[30];
    snprintf(req_line, sizeof(req_line), "REQUESTS: %d", request_count);
    display_draw_string(5, 80, req_line, COLOR_YELLOW, COLOR_BLACK);
    
    // Last request (first 35 chars)
    display_draw_string(5, 95, "LAST:", COLOR_WHITE, COLOR_BLACK);
    char truncated[36];
    strncpy(truncated, last_request, 35);
    truncated[35] = '\0';
    display_draw_string(5, 110, truncated, COLOR_MAGENTA, COLOR_BLACK);
    
    DEBUG_printf("Display updated\n");
}



void init_buttons() {
    gpio_init(BUTTON_A_PIN);
    gpio_init(BUTTON_B_PIN);
    gpio_init(BUTTON_X_PIN);
    gpio_init(BUTTON_Y_PIN);
    
    gpio_set_dir(BUTTON_A_PIN, GPIO_IN);
    gpio_set_dir(BUTTON_B_PIN, GPIO_IN);
    gpio_set_dir(BUTTON_X_PIN, GPIO_IN);
    gpio_set_dir(BUTTON_Y_PIN, GPIO_IN);
    
    gpio_pull_up(BUTTON_A_PIN);
    gpio_pull_up(BUTTON_B_PIN);
    gpio_pull_up(BUTTON_X_PIN);
    gpio_pull_up(BUTTON_Y_PIN);
}

void handle_buttons() {
    static bool last_a = true, last_b = true, last_x = true, last_y = true;
    static uint32_t last_press_time = 0;
    uint32_t now = to_ms_since_boot(get_absolute_time());
    
    if (now - last_press_time < 200) return; // Debounce
    
    bool current_a = gpio_get(BUTTON_A_PIN);
    bool current_b = gpio_get(BUTTON_B_PIN);
    bool current_x = gpio_get(BUTTON_X_PIN);
    bool current_y = gpio_get(BUTTON_Y_PIN);
    
    // Button A - Refresh display
    if (last_a && !current_a) {
        display_update_status();
        last_press_time = now;
    }
    
    // Button B - Toggle LED
    if (last_b && !current_b) {
        static bool led_on = false;
        led_on = !led_on;
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, led_on);
        display_update_status();
        last_press_time = now;
    }
    
    // Button X - Show stats
    if (last_x && !current_x) {
        display_clear(COLOR_BLUE);
        display_draw_string(10, 10, "STATISTICS", COLOR_WHITE, COLOR_BLUE);
        
        char line[40];
        snprintf(line, sizeof(line), "TOTAL REQUESTS: %d", request_count);
        display_draw_string(5, 35, line, COLOR_WHITE, COLOR_BLUE);
        
        display_draw_string(5, 55, "AP MODE ACTIVE", COLOR_WHITE, COLOR_BLUE);
        display_draw_string(5, 75, "SSID: PICOW-DISPLAY", COLOR_YELLOW, COLOR_BLUE);
        display_draw_string(5, 95, "PASS: 12345678", COLOR_GREEN, COLOR_BLUE);
        last_press_time = now;
    }
    
    // Button Y - Clear stats
    if (last_y && !current_y) {
        request_count = 0;
        strcpy(last_request, "NONE");
        display_update_status();
        last_press_time = now;
    }
    
    last_a = current_a;
    last_b = current_b;
    last_x = current_x;
    last_y = current_y;
}



static const char *http_html_hdr = 
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n"
    "Connection: close\r\n"
    "\r\n";

static const char *http_index_html = 
    "<!DOCTYPE html>\r\n"
    "<html>\r\n"
    "<head>\r\n"
    "<title>Pico W Display Pack</title>\r\n"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>\r\n"
    "<style>\r\n"
    "body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }\r\n"
    ".container { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }\r\n"
    "h1 { color: #333; text-align: center; }\r\n"
    ".status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }\r\n"
    ".button { background: #007cba; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }\r\n"
    "</style>\r\n"
    "</head>\r\n"
    "<body>\r\n"
    "<div class='container'>\r\n"
    "<h1>Pico W Display Pack 2.0</h1>\r\n"
    "<div class='status'>\r\n"
    "<p><strong>Access Point:</strong> PicoW-Display</p>\r\n"
    "<p><strong>IP Address:</strong> 192.168.4.1</p>\r\n"
    "<p><strong>Requests:</strong> %d</p>\r\n"
    "<p><strong>Last Request:</strong> %s</p>\r\n"
    "</div>\r\n"
    "<div style='text-align: center;'>\r\n"
    "<button class='button' onclick='location.reload()'>Refresh</button>\r\n"
    "<button class='button' onclick='toggleLED()'>Toggle LED</button>\r\n"
    "</div>\r\n"
    "</div>\r\n"
    "<script>\r\n"
    "function toggleLED() {\r\n"
    "    fetch('/led').then(() => { setTimeout(() => location.reload(), 500); });\r\n"
    "}\r\n"
    "</script>\r\n"
    "</body>\r\n"
    "</html>\r\n";

static err_t tcp_close_client_connection(TCP_CONNECT_STATE_T *con_state, struct tcp_pcb *client_pcb, err_t close_err) {
    if (client_pcb) {
        tcp_arg(client_pcb, NULL);
        tcp_poll(client_pcb, NULL, 0);
        tcp_sent(client_pcb, NULL);
        tcp_recv(client_pcb, NULL);
        tcp_err(client_pcb, NULL);
        err_t err = tcp_close(client_pcb);
        if (err != ERR_OK) {
            tcp_abort(client_pcb);
            close_err = ERR_ABRT;
        }
        if (con_state) {
            free(con_state);
        }
    }
    return close_err;
}

static err_t tcp_server_sent(void *arg, struct tcp_pcb *pcb, u16_t len) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    con_state->sent_len += len;

    if (con_state->sent_len >= con_state->header_len + con_state->result_len) {
        return tcp_close_client_connection(con_state, pcb, ERR_OK);
    }
    return ERR_OK;
}

static int tcp_server_send_data(void *arg, struct tcp_pcb *pcb) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;

    if (con_state->sent_len < con_state->header_len) {
        size_t left = con_state->header_len - con_state->sent_len;
        size_t send_len = left < tcp_sndbuf(pcb) ? left : tcp_sndbuf(pcb);
        
        err_t err = tcp_write(pcb, con_state->headers + con_state->sent_len, send_len, TCP_WRITE_FLAG_COPY);
        if (err != ERR_OK) {
            return tcp_close_client_connection(con_state, pcb, err);
        }
    } else {
        size_t left = con_state->result_len - (con_state->sent_len - con_state->header_len);
        size_t send_len = left < tcp_sndbuf(pcb) ? left : tcp_sndbuf(pcb);
        
        err_t err = tcp_write(pcb, con_state->result + (con_state->sent_len - con_state->header_len), send_len, TCP_WRITE_FLAG_COPY);
        if (err != ERR_OK) {
            return tcp_close_client_connection(con_state, pcb, err);
        }
    }
    return ERR_OK;
}

static err_t tcp_server_recv(void *arg, struct tcp_pcb *pcb, struct pbuf *p, err_t err) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    if (!p) {
        return tcp_close_client_connection(con_state, pcb, ERR_OK);
    }

    if (p->tot_len > 0) {
        // Copy request
        pbuf_copy_partial(p, con_state->headers, p->tot_len > BUF_SIZE - 1 ? BUF_SIZE - 1 : p->tot_len, 0);

        request_count++;
        char* request_line = strtok(con_state->headers, "\r\n");
        if (request_line) {
            strncpy(last_request, request_line, sizeof(last_request) - 1);
            last_request[sizeof(last_request) - 1] = '\0';
        }

        // Handle requests
        if (strncmp(con_state->headers, "GET / ", 6) == 0 || strncmp(con_state->headers, "GET /index", 10) == 0) {
            // Create HTML with current stats
            snprintf(con_state->result, BUF_SIZE, http_index_html, request_count, last_request);
            con_state->result_len = strlen(con_state->result);
            strcpy(con_state->headers, http_html_hdr);
            con_state->header_len = strlen(http_html_hdr);
        }
        else if (strncmp(con_state->headers, "GET /led", 8) == 0) {
            static bool led_on = false;
            led_on = !led_on;
            cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, led_on);
            
            strcpy(con_state->result, "LED toggled!");
            con_state->result_len = strlen(con_state->result);
            strcpy(con_state->headers, "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n");
            con_state->header_len = strlen(con_state->headers);
        }
        else {
            // 404
            strcpy(con_state->result, "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>");
            con_state->result_len = strlen(con_state->result);
            con_state->header_len = 0;
        }

        display_update_status();
        tcp_server_send_data(arg, pcb);
        tcp_recved(pcb, p->tot_len);
    }
    pbuf_free(p);
    return ERR_OK;
}

static err_t tcp_server_poll(void *arg, struct tcp_pcb *pcb) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    return tcp_close_client_connection(con_state, pcb, ERR_OK);
}

static void tcp_server_err(void *arg, err_t err) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    if (err != ERR_ABRT) {
        tcp_close_client_connection(con_state, con_state->pcb, err);
    }
}

static err_t tcp_server_accept(void *arg, struct tcp_pcb *client_pcb, err_t err) {
    if (err != ERR_OK || client_pcb == NULL) {
        return ERR_VAL;
    }

    TCP_CONNECT_STATE_T *con_state = calloc(1, sizeof(TCP_CONNECT_STATE_T));
    if (!con_state) {
        return ERR_MEM;
    }
    con_state->pcb = client_pcb;

    tcp_arg(client_pcb, con_state);
    tcp_sent(client_pcb, tcp_server_sent);
    tcp_recv(client_pcb, tcp_server_recv);
    tcp_poll(client_pcb, tcp_server_poll, 10);
    tcp_err(client_pcb, tcp_server_err);

    return ERR_OK;
}

static bool tcp_server_open(TCP_SERVER_T *state) {
    struct tcp_pcb *pcb = tcp_new_ip_type(IPADDR_TYPE_ANY);
    if (!pcb) {
        return false;
    }

    err_t err = tcp_bind(pcb, NULL, TCP_PORT);
    if (err) {
        tcp_close(pcb);
        return false;
    }

    state->server_pcb = tcp_listen_with_backlog(pcb, 1);
    if (!state->server_pcb) {
        tcp_close(pcb);
        return false;
    }

    tcp_arg(state->server_pcb, state);
    tcp_accept(state->server_pcb, tcp_server_accept);
    return true;
}



int main() {
    stdio_init_all();
    
    // Initialize display
    strcpy(server_status, "INIT DISPLAY");
    display_init();
    display_update_status();
    
    // Initialize buttons
    init_buttons();
    
    // Initialize WiFi
    strcpy(server_status, "INIT WIFI");
    display_update_status();
    
    if (cyw43_arch_init()) {
        strcpy(server_status, "WIFI FAILED");
        display_update_status();
        return 1;
    }

    // Enable Access Point mode
    strcpy(server_status, "STARTING AP");
    display_update_status();
    
    cyw43_arch_enable_ap_mode(AP_SSID, AP_PASSWORD, CYW43_AUTH_WPA2_AES_PSK);

    strcpy(server_status, "AP CONFIGURING");
    display_update_status();
    
    // Configure static IP (no DHCP server needed)
    ip4_addr_t gw, mask, ip;
    IP4_ADDR(&ip, 192, 168, 4, 1);
    IP4_ADDR(&gw, 192, 168, 4, 1);
    IP4_ADDR(&mask, 255, 255, 255, 0);

    // Set the IP address for the access point
    netif_set_addr(netif_list, &ip, &mask, &gw);
    
    strcpy(server_status, "AP READY");
    display_update_status();
    
    DEBUG_printf("Access Point Ready!\n");
    DEBUG_printf("SSID: %s\n", AP_SSID);
    DEBUG_printf("Password: %s\n", AP_PASSWORD);
    DEBUG_printf("IP: %s\n", ip_address);

    // Wait for network to stabilize
    sleep_ms(2000);

    // Start TCP server
    TCP_SERVER_T *state = calloc(1, sizeof(TCP_SERVER_T));
    if (!state) {
        strcpy(server_status, "ALLOC FAILED");
        display_update_status();
        return 1;
    }

    strcpy(server_status, "STARTING SERVER");
    display_update_status();

    if (!tcp_server_open(state)) {
        strcpy(server_status, "SERVER FAILED");
        display_update_status();
        free(state);
        return 1;
    }

    strcpy(server_status, "SERVER RUNNING");
    display_update_status();
    DEBUG_printf("Web server running! Connect to '%s' and visit http://%s\n", AP_SSID, ip_address);

    // Main loop
    while (!state->complete) {
        cyw43_arch_poll();
        handle_buttons();
        cyw43_arch_wait_for_work_until(make_timeout_time_ms(100));
    }

    // Cleanup
    if (state->server_pcb) {
        tcp_close(state->server_pcb);
    }
    cyw43_arch_deinit();
    free(state);
    return 0;
}

