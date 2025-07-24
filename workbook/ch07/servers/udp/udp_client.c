#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <signal.h>
#include <time.h>
#include <errno.h>

#define DEFAULT_PORT 8888
#define BUFFER_SIZE 1024
#define TIMEOUT_SECONDS 5

// Global variables for graceful shutdown
volatile int client_running = 1;
int client_sockfd = -1;

// Signal handler for graceful shutdown
void signal_handler(int sig) {
    printf("\nReceived signal %d. Shutting down client...\n", sig);
    client_running = 0;
    if (client_sockfd != -1) {
        close(client_sockfd);
    }
}

// Send message and receive response with timeout
int send_and_receive(int sockfd, struct sockaddr_in *server_addr, 
                    const char *message, char *response) {
    socklen_t addr_len = sizeof(*server_addr);
    
    // Send message
    ssize_t sent = sendto(sockfd, message, strlen(message), 0, 
                         (struct sockaddr*)server_addr, addr_len);
    if (sent < 0) {
        perror("Send failed");
        return -1;
    }
    
    printf("Sent: %s\n", message);
    
    // Set receive timeout
    struct timeval tv;
    tv.tv_sec = TIMEOUT_SECONDS;
    tv.tv_usec = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("Setsockopt timeout failed");
        return -1;
    }
    
    // Receive response
    ssize_t n = recvfrom(sockfd, response, BUFFER_SIZE - 1, 0, NULL, NULL);
    if (n < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            printf("Timeout: No response received within %d seconds\n", TIMEOUT_SECONDS);
        } else {
            perror("Receive failed");
        }
        return -1;
    }
    
    response[n] = '\0';
    printf("Server response: %s\n\n", response);
    return 0;
}

// Interactive mode
void interactive_mode(int sockfd, struct sockaddr_in *server_addr) {
    char message[BUFFER_SIZE];
    char response[BUFFER_SIZE];
    
    printf("\n=== Interactive Mode ===\n");
    printf("Commands: PING, TIME, STATS, ECHO <message>, or any text\n");
    printf("Type 'quit' or 'exit' to stop, 'help' for commands\n\n");
    
    while (client_running) {
        printf("Enter message: ");
        fflush(stdout);
        
        if (fgets(message, sizeof(message), stdin) == NULL) {
            break;
        }
        
        // Remove newline
        message[strcspn(message, "\n")] = 0;
        
        // Check for exit commands
        if (strcmp(message, "quit") == 0 || strcmp(message, "exit") == 0) {
            break;
        }
        
        // Help command
        if (strcmp(message, "help") == 0) {
            printf("\nAvailable commands:\n");
            printf("  PING        - Test connectivity\n");
            printf("  TIME        - Get server time\n");
            printf("  STATS       - Get server statistics\n");
            printf("  ECHO <msg>  - Echo a message\n");
            printf("  help        - Show this help\n");
            printf("  quit/exit   - Exit interactive mode\n");
            printf("  Any other text will be sent as a regular message\n\n");
            continue;
        }
        
        // Skip empty messages
        if (strlen(message) == 0) {
            continue;
        }
        
        send_and_receive(sockfd, server_addr, message, response);
    }
}

// Batch mode - send multiple messages
void batch_mode(int sockfd, struct sockaddr_in *server_addr, 
               char *messages[], int count) {
    char response[BUFFER_SIZE];
    
    printf("\n=== Batch Mode ===\n");
    printf("Sending %d messages to server...\n\n", count);
    
    for (int i = 0; i < count && client_running; i++) {
        printf("Message %d/%d:\n", i + 1, count);
        if (send_and_receive(sockfd, server_addr, messages[i], response) < 0) {
            printf("Failed to send message %d\n", i + 1);
        }
        
        // Small delay between messages
        usleep(100000); // 100ms
    }
}

// Stress test mode
void stress_test(int sockfd, struct sockaddr_in *server_addr, int num_messages) {
    char message[BUFFER_SIZE];
    char response[BUFFER_SIZE];
    int successful = 0, failed = 0;
    
    printf("\n=== Stress Test Mode ===\n");
    printf("Sending %d messages rapidly...\n\n", num_messages);
    
    clock_t start_time = clock();
    
    for (int i = 0; i < num_messages && client_running; i++) {
        snprintf(message, sizeof(message), "Stress test message #%d", i + 1);
        
        if (send_and_receive(sockfd, server_addr, message, response) == 0) {
            successful++;
        } else {
            failed++;
        }
        
        if ((i + 1) % 10 == 0) {
            printf("Progress: %d/%d messages sent\n", i + 1, num_messages);
        }
    }
    
    clock_t end_time = clock();
    double duration = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;
    
    printf("\n=== Stress Test Results ===\n");
    printf("Total messages: %d\n", num_messages);
    printf("Successful: %d\n", successful);
    printf("Failed: %d\n", failed);
    printf("Duration: %.2f seconds\n", duration);
    printf("Rate: %.2f messages/second\n", num_messages / duration);
}

void show_usage(const char *program_name) {
    printf("Usage: %s [OPTIONS] <server_ip> [message...]\n\n", program_name);
    printf("OPTIONS:\n");
    printf("  -p <port>     Server port (default: %d)\n", DEFAULT_PORT);
    printf("  -i            Interactive mode\n");
    printf("  -s <count>    Stress test mode with <count> messages\n");
    printf("  -h            Show this help\n\n");
    printf("EXAMPLES:\n");
    printf("  %s 127.0.0.1 \"Hello Server\"          # Send single message\n", program_name);
    printf("  %s 127.0.0.1 PING TIME STATS          # Send multiple messages\n", program_name);
    printf("  %s -i 127.0.0.1                       # Interactive mode\n", program_name);
    printf("  %s -p 9999 127.0.0.1 \"Hello\"          # Custom port\n", program_name);
    printf("  %s -s 100 127.0.0.1                   # Stress test with 100 messages\n", program_name);
}

int main(int argc, char* argv[]) {
    int port = DEFAULT_PORT;
    int interactive = 0;
    int stress_count = 0;
    char *server_ip = NULL;
    struct sockaddr_in server_addr;
    char response[BUFFER_SIZE];
    
    // Parse command line arguments
    int opt;
    while ((opt = getopt(argc, argv, "p:is:h")) != -1) {
        switch (opt) {
            case 'p':
                port = atoi(optarg);
                if (port <= 0 || port > 65535) {
                    fprintf(stderr, "Invalid port number: %s\n", optarg);
                    return EXIT_FAILURE;
                }
                break;
            case 'i':
                interactive = 1;
                break;
            case 's':
                stress_count = atoi(optarg);
                if (stress_count <= 0) {
                    fprintf(stderr, "Invalid stress test count: %s\n", optarg);
                    return EXIT_FAILURE;
                }
                break;
            case 'h':
                show_usage(argv[0]);
                return EXIT_SUCCESS;
            default:
                show_usage(argv[0]);
                return EXIT_FAILURE;
        }
    }
    
    // Check for server IP
    if (optind >= argc) {
        fprintf(stderr, "Error: Server IP address required\n\n");
        show_usage(argv[0]);
        return EXIT_FAILURE;
    }
    
    server_ip = argv[optind];
    
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Create UDP socket
    client_sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (client_sockfd < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    if (inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0) {
        fprintf(stderr, "Invalid server IP address: %s\n", server_ip);
        close(client_sockfd);
        return EXIT_FAILURE;
    }
    
    printf("Connecting to server %s:%d\n", server_ip, port);
    
    if (interactive) {
        // Interactive mode
        interactive_mode(client_sockfd, &server_addr);
    } else if (stress_count > 0) {
        // Stress test mode
        stress_test(client_sockfd, &server_addr, stress_count);
    } else if (optind + 1 < argc) {
        // Batch mode - multiple messages from command line
        batch_mode(client_sockfd, &server_addr, &argv[optind + 1], argc - optind - 1);
    } else {
        // Single message mode - use PING as default
        const char *message = "PING";
        printf("No message specified, sending default: %s\n", message);
        send_and_receive(client_sockfd, &server_addr, message, response);
    }
    
    printf("Client shutting down...\n");
    close(client_sockfd);
    return EXIT_SUCCESS;
}