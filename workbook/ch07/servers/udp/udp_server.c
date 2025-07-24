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
#define MAX_CLIENTS 100

// Global variables for graceful shutdown
volatile int server_running = 1;
int server_sockfd = -1;

// Client information structure
typedef struct {
    struct sockaddr_in addr;
    time_t last_seen;
    int message_count;
} client_info_t;

// Array to track clients
client_info_t clients[MAX_CLIENTS];
int client_count = 0;

// Signal handler for graceful shutdown
void signal_handler(int sig) {
    printf("\nReceived signal %d. Shutting down server...\n", sig);
    server_running = 0;
    if (server_sockfd != -1) {
        close(server_sockfd);
    }
}

// Find or add client to tracking array
int find_or_add_client(struct sockaddr_in *client_addr) {
    time_t current_time = time(NULL);
    
    // Look for existing client
    for (int i = 0; i < client_count; i++) {
        if (clients[i].addr.sin_addr.s_addr == client_addr->sin_addr.s_addr &&
            clients[i].addr.sin_port == client_addr->sin_port) {
            clients[i].last_seen = current_time;
            clients[i].message_count++;
            return i;
        }
    }
    
    // Add new client if space available
    if (client_count < MAX_CLIENTS) {
        clients[client_count].addr = *client_addr;
        clients[client_count].last_seen = current_time;
        clients[client_count].message_count = 1;
        return client_count++;
    }
    
    return -1; // No space for new client
}

// Clean up inactive clients (not seen for 5 minutes)
void cleanup_inactive_clients() {
    time_t current_time = time(NULL);
    int i = 0;
    
    while (i < client_count) {
        if (current_time - clients[i].last_seen > 300) { // 5 minutes
            printf("Removing inactive client: %s:%d\n", 
                   inet_ntoa(clients[i].addr.sin_addr), 
                   ntohs(clients[i].addr.sin_port));
            
            // Shift remaining clients
            for (int j = i; j < client_count - 1; j++) {
                clients[j] = clients[j + 1];
            }
            client_count--;
        } else {
            i++;
        }
    }
}

// Print server statistics
void print_statistics() {
    printf("\n=== Server Statistics ===\n");
    printf("Active clients: %d\n", client_count);
    for (int i = 0; i < client_count; i++) {
        printf("Client %d: %s:%d (Messages: %d, Last seen: %ld seconds ago)\n",
               i + 1,
               inet_ntoa(clients[i].addr.sin_addr),
               ntohs(clients[i].addr.sin_port),
               clients[i].message_count,
               time(NULL) - clients[i].last_seen);
    }
    printf("========================\n\n");
}

// Process different message types
void process_message(char *buffer, struct sockaddr_in *client_addr, 
                    socklen_t addr_len, int client_index) {
    char response[BUFFER_SIZE];
    time_t now = time(NULL);
    char *time_str = ctime(&now);
    time_str[strlen(time_str) - 1] = '\0'; // Remove newline
    
    if (strncmp(buffer, "PING", 4) == 0) {
        snprintf(response, sizeof(response), "PONG from server at %s", time_str);
    } else if (strncmp(buffer, "TIME", 4) == 0) {
        snprintf(response, sizeof(response), "Server time: %s", time_str);
    } else if (strncmp(buffer, "STATS", 5) == 0) {
        snprintf(response, sizeof(response), 
                "Server stats - Active clients: %d, Your messages: %d", 
                client_count, clients[client_index].message_count);
    } else if (strncmp(buffer, "ECHO ", 5) == 0) {
        snprintf(response, sizeof(response), "Echo: %s", buffer + 5);
    } else {
        snprintf(response, sizeof(response), 
                "ACK: Received '%s' at %s (Message #%d)", 
                buffer, time_str, clients[client_index].message_count);
    }
    
    // Send response
    ssize_t sent = sendto(server_sockfd, response, strlen(response), 0, 
                         (struct sockaddr*)client_addr, addr_len);
    if (sent < 0) {
        perror("Failed to send response");
    }
}

int main(int argc, char* argv[]) {
    int port = DEFAULT_PORT;
    struct sockaddr_in server_addr, client_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(client_addr);
    
    // Parse command line arguments
    if (argc > 1) {
        port = atoi(argv[1]);
        if (port <= 0 || port > 65535) {
            fprintf(stderr, "Invalid port number. Using default port %d\n", DEFAULT_PORT);
            port = DEFAULT_PORT;
        }
    }
    
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Create UDP socket
    server_sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (server_sockfd < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Set socket options
    int opt = 1;
    if (setsockopt(server_sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt failed");
        close(server_sockfd);
        exit(EXIT_FAILURE);
    }
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    
    // Bind socket
    if (bind(server_sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_sockfd);
        exit(EXIT_FAILURE);
    }
    
    printf("Enhanced UDP Server started on port %d\n", port);
    printf("Supported commands: PING, TIME, STATS, ECHO <message>, or any text\n");
    printf("Press Ctrl+C to stop the server\n\n");
    
    time_t last_cleanup = time(NULL);
    time_t last_stats = time(NULL);
    
    // Main server loop
    while (server_running) {
        // Set receive timeout
        struct timeval tv;
        tv.tv_sec = 1;
        tv.tv_usec = 0;
        setsockopt(server_sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        
        // Receive message
        ssize_t n = recvfrom(server_sockfd, buffer, BUFFER_SIZE - 1, 0, 
                           (struct sockaddr*)&client_addr, &addr_len);
        
        if (n < 0) {
            if (errno == EWOULDBLOCK || errno == EAGAIN) {
                // Timeout occurred, continue loop for cleanup
            } else if (errno != EINTR) {
                perror("Receive failed");
            }
        } else {
            buffer[n] = '\0';
            
            // Find or add client
            int client_index = find_or_add_client(&client_addr);
            if (client_index == -1) {
                printf("Warning: Maximum clients reached. Ignoring new client.\n");
                continue;
            }
            
            printf("[%s:%d] Received: %s\n", 
                   inet_ntoa(client_addr.sin_addr), 
                   ntohs(client_addr.sin_port), 
                   buffer);
            
            // Process the message
            process_message(buffer, &client_addr, addr_len, client_index);
        }
        
        // Periodic cleanup and statistics
        time_t current_time = time(NULL);
        if (current_time - last_cleanup > 60) { // Every minute
            cleanup_inactive_clients();
            last_cleanup = current_time;
        }
        
        if (current_time - last_stats > 300) { // Every 5 minutes
            print_statistics();
            last_stats = current_time;
        }
    }
    
    printf("\nServer shutting down gracefully...\n");
    print_statistics();
    
    if (server_sockfd != -1) {
        close(server_sockfd);
    }
    
    return 0;
}