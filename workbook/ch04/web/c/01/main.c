#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/tcp.h"

#define TCP_PORT 80
#define DEBUG_printf printf
#define BUF_SIZE 2048

// WiFi credentials
const char WIFI_SSID[] = "WIFI_SSID";
const char WIFI_PASSWORD[] = "WIFI_PASSWORD";

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

// Simple HTTP response with HTML page
static const char *http_html_hdr = 
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n"
    "Connection: close\r\n"
    "\r\n";

static const char *http_index_html = 
    "<!DOCTYPE html>\r\n"
    "<html>\r\n"
    "<head>\r\n"
    "<title>Raspberry Pi Pico W</title>\r\n"
    "<style>\r\n"
    "body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }\r\n"
    ".container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }\r\n"
    "h1 { color: #333; text-align: center; }\r\n"
    ".status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }\r\n"
    ".button { background: #007cba; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }\r\n"
    ".button:hover { background: #005a85; }\r\n"
    "</style>\r\n"
    "</head>\r\n"
    "<body>\r\n"
    "<div class='container'>\r\n"
    "<h1>Raspberry Pi Pico W Web Server</h1>\r\n"
    "<div class='status'>\r\n"
    "<p><strong>Status:</strong> Server is running!</p>\r\n"
    "<p><strong>Board:</strong> Raspberry Pi Pico W</p>\r\n"
    "<p><strong>Chip:</strong> RP2040</p>\r\n"
    "</div>\r\n"
    "<p>This is a simple web server running on the Raspberry Pi Pico W microcontroller.</p>\r\n"
    "<button class='button' onclick='location.reload()'>Refresh Page</button>\r\n"
    "<button class='button' onclick='toggleLED()'>Toggle LED</button>\r\n"
    "<p><small>LED control requires additional GPIO handling in the server code.</small></p>\r\n"
    "</div>\r\n"
    "<script>\r\n"
    "function toggleLED() {\r\n"
    "    fetch('/led').then(() => location.reload());\r\n"
    "}\r\n"
    "</script>\r\n"
    "</body>\r\n"
    "</html>\r\n";

static const char *http_404_html = 
    "HTTP/1.1 404 Not Found\r\n"
    "Content-Type: text/html\r\n"
    "Connection: close\r\n"
    "\r\n"
    "<html><body><h1>404 - Page Not Found</h1>"
    "<p>The requested page does not exist.</p>"
    "<p><a href=\"/\">Go to main page</a></p>"
    "</body></html>\r\n";

static err_t tcp_close_client_connection(TCP_CONNECT_STATE_T *con_state, struct tcp_pcb *client_pcb, err_t close_err) {
    if (client_pcb) {
        tcp_arg(client_pcb, NULL);
        tcp_poll(client_pcb, NULL, 0);
        tcp_sent(client_pcb, NULL);
        tcp_recv(client_pcb, NULL);
        tcp_err(client_pcb, NULL);
        err_t err = tcp_close(client_pcb);
        if (err != ERR_OK) {
            DEBUG_printf("Close failed %d, calling abort\n", err);
            tcp_abort(client_pcb);
            close_err = ERR_ABRT;
        }
        if (con_state) {
            free(con_state);
        }
    }
    return close_err;
}

static void tcp_server_close(TCP_SERVER_T *state) {
    if (state->server_pcb) {
        tcp_arg(state->server_pcb, NULL);
        tcp_close(state->server_pcb);
        state->server_pcb = NULL;
    }
}

static err_t tcp_server_sent(void *arg, struct tcp_pcb *pcb, u16_t len) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    DEBUG_printf("tcp_server_sent %u\n", len);
    con_state->sent_len += len;

    if (con_state->sent_len >= con_state->header_len + con_state->result_len) {
        DEBUG_printf("All data sent, closing connection\n");
        return tcp_close_client_connection(con_state, pcb, ERR_OK);
    }
    return ERR_OK;
}

static int tcp_server_send_data(void *arg, struct tcp_pcb *pcb) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;

    // Send headers first
    if (con_state->sent_len < con_state->header_len) {
        size_t left = con_state->header_len - con_state->sent_len;
        size_t send_len = left < tcp_sndbuf(pcb) ? left : tcp_sndbuf(pcb);
        
        err_t err = tcp_write(pcb, con_state->headers + con_state->sent_len, send_len, TCP_WRITE_FLAG_COPY);
        if (err != ERR_OK) {
            DEBUG_printf("Failed to write header data %d\n", err);
            return tcp_close_client_connection(con_state, pcb, err);
        }
    }
    // Then send the HTML content
    else {
        size_t left = con_state->result_len - (con_state->sent_len - con_state->header_len);
        size_t send_len = left < tcp_sndbuf(pcb) ? left : tcp_sndbuf(pcb);
        
        err_t err = tcp_write(pcb, con_state->result + (con_state->sent_len - con_state->header_len), send_len, TCP_WRITE_FLAG_COPY);
        if (err != ERR_OK) {
            DEBUG_printf("Failed to write result data %d\n", err);
            return tcp_close_client_connection(con_state, pcb, err);
        }
    }

    return ERR_OK;
}

static err_t tcp_server_recv(void *arg, struct tcp_pcb *pcb, struct pbuf *p, err_t err) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    if (!p) {
        DEBUG_printf("Connection closed by client\n");
        return tcp_close_client_connection(con_state, pcb, ERR_OK);
    }

    if (p->tot_len > 0) {
        DEBUG_printf("tcp_server_recv %d/%d err %d\n", p->tot_len, con_state->header_len, err);

        // Copy the request data
        pbuf_copy_partial(p, con_state->headers, p->tot_len > BUF_SIZE - 1 ? BUF_SIZE - 1 : p->tot_len, 0);

        // Process the HTTP request
        if (strncmp(con_state->headers, "GET / ", 6) == 0 || strncmp(con_state->headers, "GET /index", 10) == 0) {
            // Serve index page
            strcpy(con_state->result, http_index_html);
            con_state->result_len = strlen(http_index_html);
            strcpy(con_state->headers, http_html_hdr);
            con_state->header_len = strlen(http_html_hdr);
        }
        else if (strncmp(con_state->headers, "GET /led", 8) == 0) {
            // Toggle onboard LED
            static bool led_on = false;
            led_on = !led_on;
            cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, led_on);
            
            // Send simple response
            strcpy(con_state->result, "LED toggled!");
            con_state->result_len = strlen(con_state->result);
            strcpy(con_state->headers, "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n");
            con_state->header_len = strlen(con_state->headers);
        }
        else {
            // 404 response
            strcpy(con_state->headers, "");
            con_state->header_len = 0;
            strcpy(con_state->result, http_404_html);
            con_state->result_len = strlen(http_404_html);
        }

        // Send response
        tcp_server_send_data(arg, pcb);
        tcp_recved(pcb, p->tot_len);
    }
    pbuf_free(p);
    return ERR_OK;
}

static err_t tcp_server_poll(void *arg, struct tcp_pcb *pcb) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    DEBUG_printf("tcp_server_poll_fn\n");
    return tcp_close_client_connection(con_state, pcb, ERR_OK);
}

static void tcp_server_err(void *arg, err_t err) {
    TCP_CONNECT_STATE_T *con_state = (TCP_CONNECT_STATE_T*)arg;
    if (err != ERR_ABRT) {
        DEBUG_printf("tcp_client_err_fn %d\n", err);
        tcp_close_client_connection(con_state, con_state->pcb, err);
    }
}

static err_t tcp_server_accept(void *arg, struct tcp_pcb *client_pcb, err_t err) {
    TCP_SERVER_T *state = (TCP_SERVER_T*)arg;
    if (err != ERR_OK || client_pcb == NULL) {
        DEBUG_printf("Failure in accept\n");
        return ERR_VAL;
    }
    DEBUG_printf("Client connected\n");

    // Create connection state
    TCP_CONNECT_STATE_T *con_state = calloc(1, sizeof(TCP_CONNECT_STATE_T));
    if (!con_state) {
        DEBUG_printf("failed to allocate connect state\n");
        return ERR_MEM;
    }
    con_state->pcb = client_pcb;

    // Set up connection
    tcp_arg(client_pcb, con_state);
    tcp_sent(client_pcb, tcp_server_sent);
    tcp_recv(client_pcb, tcp_server_recv);
    tcp_poll(client_pcb, tcp_server_poll, 10);
    tcp_err(client_pcb, tcp_server_err);

    return ERR_OK;
}

static bool tcp_server_open(void *arg) {
    TCP_SERVER_T *state = (TCP_SERVER_T*)arg;
    DEBUG_printf("Starting server at %s on port %u\n", ip4addr_ntoa(netif_ip4_addr(netif_list)), TCP_PORT);

    struct tcp_pcb *pcb = tcp_new_ip_type(IPADDR_TYPE_ANY);
    if (!pcb) {
        DEBUG_printf("failed to create pcb\n");
        return false;
    }

    err_t err = tcp_bind(pcb, NULL, TCP_PORT);
    if (err) {
        DEBUG_printf("failed to bind to port %u\n", TCP_PORT);
        return false;
    }

    state->server_pcb = tcp_listen_with_backlog(pcb, 1);
    if (!state->server_pcb) {
        DEBUG_printf("failed to listen\n");
        if (pcb) {
            tcp_close(pcb);
        }
        return false;
    }

    tcp_arg(state->server_pcb, state);
    tcp_accept(state->server_pcb, tcp_server_accept);

    return true;
}

int main() {
    stdio_init_all();

    // Initialize WiFi
    if (cyw43_arch_init()) {
        DEBUG_printf("failed to initialise\n");
        return 1;
    }

    cyw43_arch_enable_sta_mode();

    DEBUG_printf("Connecting to WiFi ..\n");
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        DEBUG_printf("failed to connect.\n");
        return 1;
    } else {
        DEBUG_printf("Connected.\n");
        DEBUG_printf("IP Address: %s\n", ip4addr_ntoa(netif_ip4_addr(netif_list)));
    }

    // Start server
    TCP_SERVER_T *state = calloc(1, sizeof(TCP_SERVER_T));
    if (!state) {
        DEBUG_printf("failed to allocate state\n");
        return 1;
    }

    if (!tcp_server_open(state)) {
        DEBUG_printf("failed to open server\n");
        free(state);
        return 1;
    }

    DEBUG_printf("Web server is running! Visit http://%s\n", ip4addr_ntoa(netif_ip4_addr(netif_list)));

    // Main loop
    while (!state->complete) {
        cyw43_arch_poll();
        cyw43_arch_wait_for_work_until(make_timeout_time_ms(1000));
    }

    tcp_server_close(state);
    cyw43_arch_deinit();
    free(state);
    return 0;
}

