#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include "pico/util/queue.h"

// Configuration
#define UART_ID uart1
#define BAUD_RATE 9600
#define UART_TX_PIN 4
#define UART_RX_PIN 5
#define LED_PIN 25
#define TEMP_ADC_PIN 4

#define BUFFER_SIZE 50
#define MESSAGE_SIZE 128

// Message structures
typedef struct {
    char data[MESSAGE_SIZE];
    uint32_t timestamp;
} message_t;

// Global variables
static queue_t rx_queue;
static queue_t tx_queue;
static volatile bool running = true;
static volatile uint32_t counter = 0;

// Function prototypes
void core1_main();
void rx_thread();
void tx_thread();
void process_command(const char* command);
void process_request(const char* request);
void send_message(const char* message);
float read_temperature();
void blink_led(uint32_t duration_ms);
char* format_message(const char* message, char* buffer);
char* parse_message(const char* raw_message, char* buffer);

int main() {
    stdio_init_all();
    
    // Initialize hardware
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    adc_init();
    adc_gpio_init(26 + TEMP_ADC_PIN); // ADC pin 4 = GPIO 30, but internal temp is ADC 4
    adc_select_input(TEMP_ADC_PIN);
    
    // Initialize queues
    queue_init(&rx_queue, sizeof(message_t), BUFFER_SIZE);
    queue_init(&tx_queue, sizeof(message_t), BUFFER_SIZE);
    
    printf("Full-Duplex UART Communication Starting..\n");
    printf("TX=GP%d, RX=GP%d\n", UART_TX_PIN, UART_RX_PIN);
    printf("Commands: STATUS, PING, LED_ON, LED_OFF\n");
    printf("Requests: TEMP\n");
    
    // Start second core for UART handling
    multicore_launch_core1(core1_main);
    
    // Main loop - send periodic data and process messages
    while (running) {
        // Send periodic temperature data
        float temp_c = read_temperature();
        float temp_f = (temp_c * 9.0f / 5.0f) + 32.0f;
        
        char temp_msg[MESSAGE_SIZE];
        snprintf(temp_msg, sizeof(temp_msg), "TEMP:%.1fC,%.1fF,COUNT:%lu", 
                temp_c, temp_f, counter);
        send_message(temp_msg);
        
        // Process received messages
        message_t rx_msg;
        while (queue_try_remove(&rx_queue, &rx_msg)) {
            printf("Received: %s\n", rx_msg.data);
            
            if (strncmp(rx_msg.data, "CMD:", 4) == 0) {
                process_command(rx_msg.data + 4);
            } else if (strncmp(rx_msg.data, "REQ:", 4) == 0) {
                process_request(rx_msg.data + 4);
            }
        }
        
        counter++;
        sleep_ms(2000); // Wait 2 seconds between cycles
    }
    
    return 0;
}

void core1_main() {
    // Core 1 handles UART RX/TX
    rx_thread();
}

void rx_thread() {
    char buffer[MESSAGE_SIZE * 2] = {0};
    char parsed_msg[MESSAGE_SIZE];
    int buffer_pos = 0;
    
    printf("RX Thread started on core 1\n");
    
    while (running) {
        // Read available data
        while (uart_is_readable(UART_ID)) {
            char c = uart_getc(UART_ID);
            
            if (buffer_pos < sizeof(buffer) - 1) {
                buffer[buffer_pos++] = c;
                buffer[buffer_pos] = '\0';
            } else {
                // Buffer overflow, reset
                buffer_pos = 0;
                buffer[0] = '\0';
            }
            
            // Look for complete messages
            char* start = strchr(buffer, '#');
            if (start) {
                char* end = strchr(start, '*');
                if (end) {
                    // Extract message
                    size_t msg_len = end - start + 1;
                    char raw_msg[MESSAGE_SIZE];
                    strncpy(raw_msg, start, msg_len);
                    raw_msg[msg_len] = '\0';
                    
                    // Parse message
                    if (parse_message(raw_msg, parsed_msg)) {
                        message_t rx_msg;
                        strncpy(rx_msg.data, parsed_msg, sizeof(rx_msg.data) - 1);
                        rx_msg.data[sizeof(rx_msg.data) - 1] = '\0';
                        rx_msg.timestamp = to_ms_since_boot(get_absolute_time());
                        
                        // Add to queue (non-blocking)
                        if (!queue_try_add(&rx_queue, &rx_msg)) {
                            // Queue full, remove oldest
                            message_t dummy;
                            queue_try_remove(&rx_queue, &dummy);
                            queue_try_add(&rx_queue, &rx_msg);
                        }
                    }
                    
                    // Remove processed data from buffer
                    size_t remaining = buffer_pos - (end - buffer + 1);
                    memmove(buffer, end + 1, remaining);
                    buffer_pos = remaining;
                    buffer[buffer_pos] = '\0';
                }
            }
        }
        
        // Send queued messages
        message_t tx_msg;
        if (queue_try_remove(&tx_queue, &tx_msg)) {
            char formatted[MESSAGE_SIZE + 4];
            format_message(tx_msg.data, formatted);
            
            for (size_t i = 0; i < strlen(formatted); i++) {
                uart_putc(UART_ID, formatted[i]);
            }
            
            blink_led(50); // Quick blink for TX
            printf("Transmitted: %s\n", tx_msg.data);
        }
        
        sleep_ms(10); // Small delay
    }
}

void process_command(const char* command) {
    printf("Processing command: %s\n", command);
    
    if (strcmp(command, "STATUS") == 0) {
        float temp_c = read_temperature();
        char status_msg[MESSAGE_SIZE];
        snprintf(status_msg, sizeof(status_msg), "STATUS:TEMP=%.1fC,COUNT=%lu", 
                temp_c, counter);
        send_message(status_msg);
    }
    else if (strcmp(command, "PING") == 0) {
        send_message("PONG");
    }
    else if (strcmp(command, "LED_ON") == 0) {
        gpio_put(LED_PIN, 1);
        send_message("ACK:LED_ON");
    }
    else if (strcmp(command, "LED_OFF") == 0) {
        gpio_put(LED_PIN, 0);
        send_message("ACK:LED_OFF");
    }
}

void process_request(const char* request) {
    printf("Processing request: %s\n", request);
    
    if (strcmp(request, "TEMP") == 0) {
        float temp_c = read_temperature();
        float temp_f = (temp_c * 9.0f / 5.0f) + 32.0f;
        char temp_msg[MESSAGE_SIZE];
        snprintf(temp_msg, sizeof(temp_msg), "TEMP:%.1fC,%.1fF", temp_c, temp_f);
        send_message(temp_msg);
    }
}

void send_message(const char* message) {
    message_t tx_msg;
    strncpy(tx_msg.data, message, sizeof(tx_msg.data) - 1);
    tx_msg.data[sizeof(tx_msg.data) - 1] = '\0';
    tx_msg.timestamp = to_ms_since_boot(get_absolute_time());
    
    // Add to queue (non-blocking)
    if (!queue_try_add(&tx_queue, &tx_msg)) {
        // Queue full, remove oldest
        message_t dummy;
        queue_try_remove(&tx_queue, &dummy);
        queue_try_add(&tx_queue, &tx_msg);
    }
}

float read_temperature() {
    // Read internal temperature sensor
    uint16_t raw = adc_read();
    const float conversion_factor = 3.3f / (1 << 12);
    float voltage = raw * conversion_factor;
    float temperature = 27.0f - (voltage - 0.706f) / 0.001721f;
    return temperature;
}

void blink_led(uint32_t duration_ms) {
    gpio_put(LED_PIN, 1);
    sleep_ms(duration_ms);
    gpio_put(LED_PIN, 0);
}

char* format_message(const char* message, char* buffer) {
    snprintf(buffer, MESSAGE_SIZE + 4, "#%s*", message);
    return buffer;
}

char* parse_message(const char* raw_message, char* buffer) {
    size_t len = strlen(raw_message);
    if (len >= 3 && raw_message[0] == '#' && raw_message[len-1] == '*') {
        strncpy(buffer, raw_message + 1, len - 2);
        buffer[len - 2] = '\0';
        return buffer;
    }
    return NULL;
}