#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "pico/util/queue.h"

// Configuration
#define UART_ID uart1
#define BAUD_RATE 9600
#define UART_TX_PIN 4
#define UART_RX_PIN 5

#define BUFFER_SIZE 50
#define MESSAGE_SIZE 128
#define HISTORY_SIZE 20

// Message structures
typedef struct {
    char data[MESSAGE_SIZE];
    uint32_t timestamp;
} message_t;

typedef struct {
    char command[MESSAGE_SIZE];
    uint32_t timestamp;
} history_entry_t;

// Global variables
static queue_t rx_queue;
static queue_t tx_queue;
static volatile bool running = true;
static history_entry_t command_history[HISTORY_SIZE];
static int history_count = 0;

// Function prototypes
void core1_main();
void rx_thread();
void send_command(const char* command);
void send_request(const char* request);
void display_messages();
void interactive_mode();
void monitor_mode();
void add_to_history(const char* command);
void show_history();
char* format_message(const char* message, char* buffer);
char* parse_message(const char* raw_message, char* buffer);
void format_time(uint32_t timestamp, char* buffer);
char* trim_string(char* str);

int main() {
    stdio_init_all();
    
    // Initialize hardware
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    
    // Initialize queues
    queue_init(&rx_queue, sizeof(message_t), BUFFER_SIZE);
    queue_init(&tx_queue, sizeof(message_t), BUFFER_SIZE);
    
    printf("UART Controller Starting..\n");
    printf("TX=GP%d, RX=GP%d\n", UART_TX_PIN, UART_RX_PIN);
    
    // Start second core for UART handling
    multicore_launch_core1(core1_main);
    
    // Choose mode
    printf("\nSelect mode:\n");
    printf("1. Interactive mode (send commands)\n");
    printf("2. Monitor mode (just listen)\n");
    printf("Enter choice (1 or 2): ");
    
    char choice = getchar();
    getchar(); // consume newline
    
    if (choice == '1') {
        interactive_mode();
    } else if (choice == '2') {
        monitor_mode();
    } else {
        printf("Invalid choice\n");
    }
    
    running = false;
    printf("\nStopping controller..\n");
    
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
    
    printf("Controller RX Thread started on core 1\n");
    
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
            
            printf("Sent: %s\n", tx_msg.data);
        }
        
        sleep_ms(10); // Small delay
    }
}

void send_command(const char* command) {
    char message[MESSAGE_SIZE];
    snprintf(message, sizeof(message), "CMD:%s", command);
    
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
    
    // Add to history
    add_to_history(message);
}

void send_request(const char* request) {
    char message[MESSAGE_SIZE];
    snprintf(message, sizeof(message), "REQ:%s", request);
    
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
    
    // Add to history
    add_to_history(message);
}

void display_messages() {
    message_t rx_msg;
    while (queue_try_remove(&rx_queue, &rx_msg)) {
        char time_str[16];
        format_time(rx_msg.timestamp, time_str);
        printf("[%s] Received: %s\n", time_str, rx_msg.data);
    }
}

void interactive_mode() {
    printf("\n-- UART Controller --\n");
    printf("Commands:\n");
    printf("  STATUS    - Get device status\n");
    printf("  PING      - Ping device\n");
    printf("  LED_ON    - Turn LED on\n");
    printf("  LED_OFF   - Turn LED off\n");
    printf("  TEMP      - Request temperature\n");
    printf("  HISTORY   - Show command history\n");
    printf("  MESSAGES  - Show recent messages\n");
    printf("  QUIT      - Exit\n");
    printf("------------------------\n");
    
    char input[MESSAGE_SIZE];
    
    while (running) {
        // Display any new messages
        display_messages();
        
        // Get user input
        printf("Enter command: ");
        if (fgets(input, sizeof(input), stdin)) {
            char* cmd = trim_string(input);
            
            // Convert to uppercase
            for (int i = 0; cmd[i]; i++) {
                cmd[i] = toupper(cmd[i]);
            }
            
            if (strcmp(cmd, "QUIT") == 0) {
                break;
            } else if (strcmp(cmd, "STATUS") == 0) {
                send_command("STATUS");
            } else if (strcmp(cmd, "PING") == 0) {
                send_command("PING");
            } else if (strcmp(cmd, "LED_ON") == 0) {
                send_command("LED_ON");
            } else if (strcmp(cmd, "LED_OFF") == 0) {
                send_command("LED_OFF");
            } else if (strcmp(cmd, "TEMP") == 0) {
                send_request("TEMP");
            } else if (strcmp(cmd, "HISTORY") == 0) {
                show_history();
            } else if (strcmp(cmd, "MESSAGES") == 0) {
                printf("Recent messages displayed above\n");
            } else if (strlen(cmd) == 0) {
                continue;
            } else {
                printf("Unknown command: %s\n", cmd);
            }
            
            sleep_ms(100);
        }
    }
}

void monitor_mode() {
    printf("Monitor Mode - Press 'q' + Enter to exit\n");
    
    while (running) {
        display_messages();
        
        // Check for quit command (non-blocking read would be better)
        if (getchar_timeout_us(0) == 'q') {
            char c = getchar_timeout_us(0);
            if (c == '\n' || c == '\r') {
                break;
            }
        }
        
        sleep_ms(500);
    }
}

void add_to_history(const char* command) {
    strncpy(command_history[history_count % HISTORY_SIZE].command, command, 
            sizeof(command_history[0].command) - 1);
    command_history[history_count % HISTORY_SIZE].command[
        sizeof(command_history[0].command) - 1] = '\0';
    command_history[history_count % HISTORY_SIZE].timestamp = 
        to_ms_since_boot(get_absolute_time());
    history_count++;
}

void show_history() {
    printf("\nCommand History:\n");
    int start = (history_count > HISTORY_SIZE) ? history_count - HISTORY_SIZE : 0;
    int count = (history_count > HISTORY_SIZE) ? HISTORY_SIZE : history_count;
    
    for (int i = 0; i < count; i++) {
        int idx = (start + i) % HISTORY_SIZE;
        char time_str[16];
        format_time(command_history[idx].timestamp, time_str);
        printf("  %d. [%s] %s\n", i + 1, time_str, command_history[idx].command);
    }
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

void format_time(uint32_t timestamp, char* buffer) {
    uint32_t seconds = timestamp / 1000;
    uint32_t hours = (seconds / 3600) % 24;
    uint32_t minutes = (seconds / 60) % 60;
    uint32_t secs = seconds % 60;
    snprintf(buffer, 16, "%02lu:%02lu:%02lu", hours, minutes, secs);
}

char* trim_string(char* str) {
    char* end;
    
    // Trim leading space
    while(isspace((unsigned char)*str)) str++;
    
    if(*str == 0)  // All spaces?
        return str;
    
    // Trim trailing space
    end = str + strlen(str) - 1;
    while(end > str && isspace((unsigned char)*end)) end--;
    
    // Write new null terminator
    end[1] = '\0';
    
    return str;
}