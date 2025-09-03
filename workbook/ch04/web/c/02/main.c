#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/tcp.h"

#define TCP_PORT 80
#define DEBUG_printf printf
#define BUF_SIZE 2048

// Access Point credentials
const char AP_SSID[] = "PicoW-Server";
const char AP_PASSWORD[] = "12345678";  // Must be at least 8 characters

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
    "<html>\r\n"
    "<head>\r\n"
    "<title>Pico W Access Point</title>\r\n"
    "</head>\r\n"
    "<body>\r\n"
    "<h1>Raspberry Pi Pico W Access Point</h1>\r\n"
    "<p>Status: Access Point is running!</p>\r\n"
    "<p>SSID: PicoW-Server</p>\r\n"
    "<p>IP Address: 192.168.4.1</p>\r\n"
    "<p>Board: Raspberry Pi Pico W</p>\r\n"
    "<p>Chip: RP2040</p>\r\n"
    "<hr>\r\n"
    "<p>This Pico W is running its own WiFi network.</p>\r\n"
    "<p>Any device can connect to it directly!</p>\r\n"
    "<p><a href=\"/\">Refresh Page</a></p>\r\n"
    "<p><a href=\"/led\">Toggle LED</a></p>\r\n"
    "<p><a href=\"/status\">System Status</a></p>\r\n"
    "<hr>\r\n"
    "<p><small>Embedded Access Point Web Server Demo</small></p>\r\n"
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
            sprintf(con_state->result, 
                "<html><body><h1>LED Control</h1>"
                "<p>LED is now: %s</p>"
                "<p><a href=\"/\">Back to main page</a></p>"
                "</body></html>", led_on ? "ON" : "OFF");
            con_state->result_len = strlen(con_state->result);
            strcpy(con_state->headers, http_html_hdr);
            con_state->header_len = strlen(http_html_hdr);
        }
        else if (strncmp(con_state->headers, "GET /status", 11) == 0) {
            // Show system status
            sprintf(con_state->result,
                "<html><body><h1>System Status</h1>"
                "<p>Mode: Access Point</p>"
                "<p>SSID: %s</p>"
                "<p>IP: 192.168.4.1</p>"
                "<p>Uptime: %d ms</p>"
                "<p><a href=\"/\">Back to main page</a></p>"
                "</body></html>", 
                AP_SSID,
                (int)to_ms_since_boot(get_absolute_time()));
            con_state->result_len = strlen(con_state->result);
            strcpy(con_state->headers, http_html_hdr);
            con_state->header_len = strlen(http_html_hdr);
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
    DEBUG_printf("Starting server on port %u\n", TCP_PORT);

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

    // Init WiFi in Access Point mode
    if (cyw43_arch_init()) {
        DEBUG_printf("failed to initialise\n");
        return 1;
    }

    cyw43_arch_enable_ap_mode(AP_SSID, AP_PASSWORD, CYW43_AUTH_WPA2_AES_PSK);

    DEBUG_printf("Access Point started!\n");
    DEBUG_printf("SSID: %s\n", AP_SSID);
    DEBUG_printf("Password: %s\n", AP_PASSWORD);
    DEBUG_printf("IP Address: 192.168.4.1\n");
    DEBUG_printf("Connect your device to the WiFi network and visit http://192.168.4.1\n");

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

    DEBUG_printf("Web server is running in Access Point mode!\n");
    DEBUG_printf("Connect to WiFi: %s (password: %s)\n", AP_SSID, AP_PASSWORD);
    DEBUG_printf("Then visit: http://192.168.4.1\n");

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

