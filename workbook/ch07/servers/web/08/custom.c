#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <time.h>

// Ethernet header structure
struct eth_header {
    uint8_t dest_mac[6];
    uint8_t src_mac[6];
    uint16_t ethertype;
} __attribute__((packed));

// IP header structure
struct ip_header {
    uint8_t version_ihl;
    uint8_t tos;
    uint16_t total_length;
    uint16_t id;
    uint16_t flags_fragment;
    uint8_t ttl;
    uint8_t protocol;
    uint16_t checksum;
    uint32_t src_ip;
    uint32_t dest_ip;
} __attribute__((packed));

// TCP header structure
struct tcp_header {
    uint16_t src_port;
    uint16_t dest_port;
    uint32_t seq_num;
    uint32_t ack_num;
    uint8_t data_offset_flags;
    uint8_t flags;
    uint16_t window_size;
    uint16_t checksum;
    uint16_t urgent_ptr;
} __attribute__((packed));

// Custom Protocol Header (MyNet Protocol)
#define MYNET_MAGIC 0x4D594E45  // "MYNE"
#define MYNET_VERSION 1
#define MYNET_MAX_PAYLOAD 1024

struct mynet_header {
    uint32_t magic;         // Protocol magic number
    uint8_t version;        // Protocol version
    uint8_t msg_type;       // Message type
    uint16_t flags;         // Protocol flags
    uint32_t msg_id;        // Message ID for tracking
    uint32_t payload_len;   // Payload length
    uint32_t checksum;      // Payload checksum
} __attribute__((packed));

// MyNet Message Types
enum mynet_msg_type {
    MYNET_HELLO = 1,        // Initial handshake
    MYNET_HELLO_ACK,        // Handshake response
    MYNET_PEER_DISCOVER,    // P2P peer discovery
    MYNET_PEER_ANNOUNCE,    // P2P peer announcement
    MYNET_DATA,             // Data transfer
    MYNET_DATA_ACK,         // Data acknowledgment
    MYNET_FILE_REQUEST,     // File request (client-server)
    MYNET_FILE_RESPONSE,    // File response (client-server)
    MYNET_CHAT_MSG,         // Chat message (P2P)
    MYNET_HEARTBEAT,        // Keep-alive
    MYNET_BYE               // Connection termination
};

// MyNet Protocol Flags
#define MYNET_FLAG_ENCRYPTED    0x0001
#define MYNET_FLAG_COMPRESSED   0x0002
#define MYNET_FLAG_PRIORITY     0x0004
#define MYNET_FLAG_P2P_MODE     0x0008
#define MYNET_FLAG_SERVER_MODE  0x0010

// MyNet Node Types
enum mynet_node_type {
    MYNET_NODE_CLIENT,
    MYNET_NODE_SERVER,
    MYNET_NODE_PEER
};

// Peer information structure
struct peer_info {
    uint32_t ip;
    uint16_t port;
    char name[32];
    time_t last_seen;
    enum mynet_node_type type;
    struct peer_info *next;
};

// File sharing structure
struct shared_file {
    char filename[256];
    uint32_t size;
    uint32_t checksum;
    char path[512];
    struct shared_file *next;
};

// TCP connection state
enum tcp_state {
    TCP_CLOSED,
    TCP_LISTEN,
    TCP_SYN_SENT,
    TCP_SYN_RECEIVED,
    TCP_ESTABLISHED,
    TCP_FIN_WAIT_1,
    TCP_FIN_WAIT_2,
    TCP_CLOSE_WAIT,
    TCP_CLOSING,
    TCP_LAST_ACK,
    TCP_TIME_WAIT
};

// Enhanced connection control block with MyNet protocol state
struct tcp_connection {
    uint32_t local_ip;
    uint32_t remote_ip;
    uint16_t local_port;
    uint16_t remote_port;
    uint32_t seq_num;
    uint32_t ack_num;
    enum tcp_state state;
    
    // MyNet protocol state
    uint8_t mynet_active;
    enum mynet_node_type node_type;
    uint32_t last_msg_id;
    time_t last_activity;
    char peer_name[32];
    
    struct tcp_connection *next;
};

// MyNet protocol context
struct mynet_context {
    enum mynet_node_type node_type;
    char node_name[32];
    uint16_t listen_port;
    struct peer_info *peers;
    struct shared_file *files;
    uint32_t next_msg_id;
};

// Global variables
static struct tcp_connection *connections = NULL;
static struct mynet_context *mynet_ctx = NULL;

// Function declarations
uint16_t ip_checksum(void *data, int len);
uint32_t simple_checksum(void *data, int len);
struct tcp_connection *find_connection(uint32_t local_ip, uint16_t local_port,
                                      uint32_t remote_ip, uint16_t remote_port);
struct tcp_connection *create_connection(uint32_t local_ip, uint16_t local_port,
                                        uint32_t remote_ip, uint16_t remote_port);

// Calculate simple checksum for MyNet protocol
uint32_t simple_checksum(void *data, int len) {
    uint32_t sum = 0;
    uint8_t *ptr = (uint8_t *)data;
    for (int i = 0; i < len; i++) {
        sum += ptr[i];
    }
    return sum;
}

// Initialize MyNet protocol context
struct mynet_context *init_mynet_context(enum mynet_node_type type, 
                                        const char *name, uint16_t port) {
    struct mynet_context *ctx = malloc(sizeof(struct mynet_context));
    if (!ctx) return NULL;
    
    ctx->node_type = type;
    strncpy(ctx->node_name, name, sizeof(ctx->node_name) - 1);
    ctx->node_name[sizeof(ctx->node_name) - 1] = '\0';
    ctx->listen_port = port;
    ctx->peers = NULL;
    ctx->files = NULL;
    ctx->next_msg_id = 1;
    
    return ctx;
}

// Add peer to peer list
void add_peer(struct mynet_context *ctx, uint32_t ip, uint16_t port, 
              const char *name, enum mynet_node_type type) {
    struct peer_info *peer = malloc(sizeof(struct peer_info));
    if (!peer) return;
    
    peer->ip = ip;
    peer->port = port;
    strncpy(peer->name, name, sizeof(peer->name) - 1);
    peer->name[sizeof(peer->name) - 1] = '\0';
    peer->last_seen = time(NULL);
    peer->type = type;
    peer->next = ctx->peers;
    ctx->peers = peer;
    
    printf("Added peer: %s (%u.%u.%u.%u:%u) - Type: %s\n", 
           name,
           (ip >> 24) & 0xFF, (ip >> 16) & 0xFF, 
           (ip >> 8) & 0xFF, ip & 0xFF, port,
           type == MYNET_NODE_SERVER ? "Server" : 
           type == MYNET_NODE_PEER ? "Peer" : "Client");
}

// Add shared file
void add_shared_file(struct mynet_context *ctx, const char *filename, 
                    const char *path, uint32_t size) {
    struct shared_file *file = malloc(sizeof(struct shared_file));
    if (!file) return;
    
    strncpy(file->filename, filename, sizeof(file->filename) - 1);
    file->filename[sizeof(file->filename) - 1] = '\0';
    strncpy(file->path, path, sizeof(file->path) - 1);
    file->path[sizeof(file->path) - 1] = '\0';
    file->size = size;
    file->checksum = simple_checksum((void*)filename, strlen(filename));
    file->next = ctx->files;
    ctx->files = file;
    
    printf("Shared file added: %s (%u bytes)\n", filename, size);
}

// Create MyNet message
int create_mynet_message(uint8_t *buffer, int buffer_size, uint8_t msg_type,
                        uint16_t flags, const void *payload, uint32_t payload_len) {
    if (buffer_size < sizeof(struct mynet_header) + payload_len) {
        return -1;
    }
    
    struct mynet_header *hdr = (struct mynet_header *)buffer;
    hdr->magic = htonl(MYNET_MAGIC);
    hdr->version = MYNET_VERSION;
    hdr->msg_type = msg_type;
    hdr->flags = htons(flags);
    hdr->msg_id = htonl(mynet_ctx ? mynet_ctx->next_msg_id++ : 1);
    hdr->payload_len = htonl(payload_len);
    
    if (payload && payload_len > 0) {
        memcpy(buffer + sizeof(struct mynet_header), payload, payload_len);
        hdr->checksum = htonl(simple_checksum((void*)payload, payload_len));
    } else {
        hdr->checksum = 0;
    }
    
    return sizeof(struct mynet_header) + payload_len;
}

// Process MyNet protocol message
int process_mynet_message(struct tcp_connection *conn, uint8_t *data, int len) {
    if (len < sizeof(struct mynet_header)) {
        return -1;
    }
    
    struct mynet_header *hdr = (struct mynet_header *)data;
    
    // Validate magic number
    if (ntohl(hdr->magic) != MYNET_MAGIC) {
        printf("Invalid MyNet magic number\n");
        return -1;
    }
    
    // Validate version
    if (hdr->version != MYNET_VERSION) {
        printf("Unsupported MyNet version: %d\n", hdr->version);
        return -1;
    }
    
    uint32_t payload_len = ntohl(hdr->payload_len);
    uint8_t *payload = data + sizeof(struct mynet_header);
    
    // Verify payload checksum
    if (payload_len > 0) {
        uint32_t calculated_checksum = simple_checksum(payload, payload_len);
        if (ntohl(hdr->checksum) != calculated_checksum) {
            printf("MyNet checksum mismatch\n");
            return -1;
        }
    }
    
    printf("MyNet message: Type=%d, ID=%u, Flags=0x%04x, PayloadLen=%u\n",
           hdr->msg_type, ntohl(hdr->msg_id), ntohs(hdr->flags), payload_len);
    
    conn->mynet_active = 1;
    conn->last_msg_id = ntohl(hdr->msg_id);
    conn->last_activity = time(NULL);
    
    // Process different message types
    switch (hdr->msg_type) {
        case MYNET_HELLO: {
            printf("Received HELLO from peer\n");
            if (payload_len > 0 && payload_len < sizeof(conn->peer_name)) {
                memcpy(conn->peer_name, payload, payload_len);
                conn->peer_name[payload_len] = '\0';
                printf("Peer name: %s\n", conn->peer_name);
            }
            
            // Send HELLO_ACK response
            uint8_t response[256];
            const char *our_name = mynet_ctx ? mynet_ctx->node_name : "Unknown";
            int resp_len = create_mynet_message(response, sizeof(response),
                                              MYNET_HELLO_ACK, 0,
                                              our_name, strlen(our_name));
            printf("Sending HELLO_ACK response\n");
            break;
        }
        
        case MYNET_HELLO_ACK: {
            printf("Received HELLO_ACK from peer\n");
            if (payload_len > 0 && payload_len < sizeof(conn->peer_name)) {
                memcpy(conn->peer_name, payload, payload_len);
                conn->peer_name[payload_len] = '\0';
                printf("Peer confirmed: %s\n", conn->peer_name);
            }
            break;
        }
        
        case MYNET_PEER_DISCOVER: {
            printf("Received peer discovery request\n");
            
            // In P2P mode, announce ourselves
            if (mynet_ctx && (ntohs(hdr->flags) & MYNET_FLAG_P2P_MODE)) {
                uint8_t response[256];
                char announce_data[128];
                snprintf(announce_data, sizeof(announce_data), 
                        "%s:%u:%d", mynet_ctx->node_name, 
                        mynet_ctx->listen_port, mynet_ctx->node_type);
                
                int resp_len = create_mynet_message(response, sizeof(response),
                                                  MYNET_PEER_ANNOUNCE, 
                                                  MYNET_FLAG_P2P_MODE,
                                                  announce_data, strlen(announce_data));
                printf("Announcing ourselves to peer network\n");
            }
            break;
        }
        
        case MYNET_PEER_ANNOUNCE: {
            printf("Received peer announcement\n");
            if (payload_len > 0) {
                char announce_str[256];
                memcpy(announce_str, payload, payload_len);
                announce_str[payload_len] = '\0';
                
                // Parse announcement: name:port:type
                char *name = strtok(announce_str, ":");
                char *port_str = strtok(NULL, ":");
                char *type_str = strtok(NULL, ":");
                
                if (name && port_str && type_str && mynet_ctx) {
                    uint16_t port = atoi(port_str);
                    enum mynet_node_type type = atoi(type_str);
                    add_peer(mynet_ctx, conn->remote_ip, port, name, type);
                }
            }
            break;
        }
        
        case MYNET_CHAT_MSG: {
            printf("Received chat message from %s: ", conn->peer_name);
            if (payload_len > 0) {
                printf("%.*s\n", (int)payload_len, (char*)payload);
            }
            break;
        }
        
        case MYNET_FILE_REQUEST: {
            printf("Received file request\n");
            if (payload_len > 0 && mynet_ctx) {
                char filename[256];
                memcpy(filename, payload, payload_len);
                filename[payload_len] = '\0';
                
                // Search for requested file
                struct shared_file *file = mynet_ctx->files;
                while (file) {
                    if (strcmp(file->filename, filename) == 0) {
                        printf("Found requested file: %s\n", filename);
                        
                        // Send file response (simplified - would send actual file data)
                        uint8_t response[512];
                        char file_info[256];
                        snprintf(file_info, sizeof(file_info), 
                                "FILE:%s:%u:%u", file->filename, 
                                file->size, file->checksum);
                        
                        int resp_len = create_mynet_message(response, sizeof(response),
                                                          MYNET_FILE_RESPONSE, 0,
                                                          file_info, strlen(file_info));
                        printf("Sending file response\n");
                        break;
                    }
                    file = file->next;
                }
            }
            break;
        }
        
        case MYNET_FILE_RESPONSE: {
            printf("Received file response\n");
            if (payload_len > 0) {
                printf("File info: %.*s\n", (int)payload_len, (char*)payload);
            }
            break;
        }
        
        case MYNET_HEARTBEAT: {
            printf("Received heartbeat from %s\n", conn->peer_name);
            // Send heartbeat response
            uint8_t response[64];
            int resp_len = create_mynet_message(response, sizeof(response),
                                              MYNET_HEARTBEAT, 0, NULL, 0);
            break;
        }
        
        case MYNET_BYE: {
            printf("Received BYE from %s\n", conn->peer_name);
            // Mark connection for cleanup
            break;
        }
        
        default:
            printf("Unknown MyNet message type: %d\n", hdr->msg_type);
            break;
    }
    
    return 0;
}

// Calculate IP checksum
uint16_t ip_checksum(void *data, int len) {
    uint32_t sum = 0;
    uint16_t *ptr = (uint16_t *)data;
    
    while (len > 1) {
        sum += *ptr++;
        len -= 2;
    }
    
    if (len == 1) {
        sum += *(uint8_t *)ptr;
    }
    
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    
    return ~sum;
}

// Find TCP connection
struct tcp_connection *find_connection(uint32_t local_ip, uint16_t local_port,
                                      uint32_t remote_ip, uint16_t remote_port) {
    struct tcp_connection *conn = connections;
    while (conn) {
        if (conn->local_ip == local_ip && conn->local_port == local_port &&
            conn->remote_ip == remote_ip && conn->remote_port == remote_port) {
            return conn;
        }
        conn = conn->next;
    }
    return NULL;
}

// Create new TCP connection
struct tcp_connection *create_connection(uint32_t local_ip, uint16_t local_port,
                                        uint32_t remote_ip, uint16_t remote_port) {
    struct tcp_connection *conn = malloc(sizeof(struct tcp_connection));
    if (!conn) return NULL;
    
    conn->local_ip = local_ip;
    conn->local_port = local_port;
    conn->remote_ip = remote_ip;
    conn->remote_port = remote_port;
    conn->seq_num = rand() % 0xFFFFFFFF;
    conn->ack_num = 0;
    conn->state = TCP_CLOSED;
    conn->mynet_active = 0;
    conn->node_type = MYNET_NODE_CLIENT;
    conn->last_msg_id = 0;
    conn->last_activity = time(NULL);
    memset(conn->peer_name, 0, sizeof(conn->peer_name));
    conn->next = connections;
    connections = conn;
    
    return conn;
}

// Process Ethernet frame
int process_ethernet(uint8_t *packet, int len) {
    if (len < sizeof(struct eth_header)) {
        return -1;
    }
    
    struct eth_header *eth = (struct eth_header *)packet;
    
    // Check if it's an IP packet
    if (ntohs(eth->ethertype) == 0x0800) {
        return process_ip(packet + sizeof(struct eth_header), 
                         len - sizeof(struct eth_header));
    }
    
    return 0;
}

// Process IP packet
int process_ip(uint8_t *packet, int len) {
    if (len < sizeof(struct ip_header)) {
        return -1;
    }
    
    struct ip_header *ip = (struct ip_header *)packet;
    
    // Basic IP header validation
    if ((ip->version_ihl >> 4) != 4) {
        return -1; // Not IPv4
    }
    
    int header_len = (ip->version_ihl & 0x0F) * 4;
    if (len < header_len) {
        return -1;
    }
    
    // Process TCP packets
    if (ip->protocol == 6) {
        return process_tcp(packet + header_len, len - header_len, ip);
    }
    
    return 0;
}

// Process TCP segment with MyNet protocol support
int process_tcp(uint8_t *packet, int len, struct ip_header *ip) {
    if (len < sizeof(struct tcp_header)) {
        return -1;
    }
    
    struct tcp_header *tcp = (struct tcp_header *)packet;
    
    uint16_t src_port = ntohs(tcp->src_port);
    uint16_t dest_port = ntohs(tcp->dest_port);
    uint32_t seq_num = ntohl(tcp->seq_num);
    uint32_t ack_num = ntohl(tcp->ack_num);
    int tcp_header_len = ((tcp->data_offset_flags >> 4) & 0x0F) * 4;
    
    printf("TCP: %u.%u.%u.%u:%u -> %u.%u.%u.%u:%u\n",
           (ntohl(ip->src_ip) >> 24) & 0xFF,
           (ntohl(ip->src_ip) >> 16) & 0xFF,
           (ntohl(ip->src_ip) >> 8) & 0xFF,
           ntohl(ip->src_ip) & 0xFF,
           src_port,
           (ntohl(ip->dest_ip) >> 24) & 0xFF,
           (ntohl(ip->dest_ip) >> 16) & 0xFF,
           (ntohl(ip->dest_ip) >> 8) & 0xFF,
           ntohl(ip->dest_ip) & 0xFF,
           dest_port);
    
    // Find or create connection
    struct tcp_connection *conn = find_connection(ip->dest_ip, dest_port,
                                                 ip->src_ip, src_port);
    if (!conn) {
        conn = create_connection(ip->dest_ip, dest_port,
                               ip->src_ip, src_port);
        if (!conn) return -1;
    }
    
    // Process TCP flags
    uint8_t flags = tcp->flags;
    
    if (flags & 0x02) { // SYN
        printf("TCP SYN received\n");
        if (conn->state == TCP_CLOSED || conn->state == TCP_LISTEN) {
            conn->ack_num = seq_num + 1;
            conn->state = TCP_SYN_RECEIVED;
            printf("Should send SYN-ACK\n");
        }
    }
    
    if (flags & 0x10) { // ACK
        printf("TCP ACK received\n");
        if (conn->state == TCP_SYN_RECEIVED) {
            conn->state = TCP_ESTABLISHED;
            printf("TCP connection established\n");
        }
    }
    
    // Process application data if connection is established
    if (conn->state == TCP_ESTABLISHED && len > tcp_header_len) {
        uint8_t *app_data = packet + tcp_header_len;
        int app_data_len = len - tcp_header_len;
        
        printf("Processing application data (%d bytes)\n", app_data_len);
        
        // Check if it's MyNet protocol data
        if (app_data_len >= sizeof(struct mynet_header)) {
            struct mynet_header *mynet_hdr = (struct mynet_header *)app_data;
            if (ntohl(mynet_hdr->magic) == MYNET_MAGIC) {
                process_mynet_message(conn, app_data, app_data_len);
            }
        }
    }
    
    if (flags & 0x01) { // FIN
        printf("TCP FIN received\n");
        if (conn->state == TCP_ESTABLISHED) {
            conn->state = TCP_CLOSE_WAIT;
            conn->ack_num = seq_num + 1;
            printf("Should send ACK and FIN\n");
        }
    }
    
    return 0;
}

// Initialize TCP/IP stack with MyNet protocol
int init_tcp_ip_stack(enum mynet_node_type node_type, const char *node_name, 
                     uint16_t port) {
    mynet_ctx = init_mynet_context(node_type, node_name, port);
    if (!mynet_ctx) {
        printf("Failed to initialize MyNet context\n");
        return -1;
    }
    
    printf("TCP/IP stack with MyNet protocol initialized\n");
    printf("Node: %s (Type: %s, Port: %u)\n", 
           node_name,
           node_type == MYNET_NODE_SERVER ? "Server" : 
           node_type == MYNET_NODE_PEER ? "Peer" : "Client",
           port);
    
    return 0;
}

// Cleanup TCP/IP stack
void cleanup_tcp_ip_stack() {
    // Cleanup connections
    struct tcp_connection *conn = connections;
    while (conn) {
        struct tcp_connection *next = conn->next;
        free(conn);
        conn = next;
    }
    connections = NULL;
    
    // Cleanup MyNet context
    if (mynet_ctx) {
        // Cleanup peers
        struct peer_info *peer = mynet_ctx->peers;
        while (peer) {
            struct peer_info *next = peer->next;
            free(peer);
            peer = next;
        }
        
        // Cleanup files
        struct shared_file *file = mynet_ctx->files;
        while (file) {
            struct shared_file *next = file->next;
            free(file);
            file = next;
        }
        
        free(mynet_ctx);
        mynet_ctx = NULL;
    }
    
    printf("TCP/IP stack cleaned up\n");
}

// Simulate different scenarios
void simulate_p2p_chat() {
    printf("\n=== Simulating P2P Chat ===\n");
    
    // Create MyNet chat message
    uint8_t msg_buffer[512];
    const char *chat_msg = "Hello from peer!";
    int msg_len = create_mynet_message(msg_buffer, sizeof(msg_buffer),
                                      MYNET_CHAT_MSG, MYNET_FLAG_P2P_MODE,
                                      chat_msg, strlen(chat_msg));
    
    // Simulate TCP connection with chat data
    struct ip_header ip;
    memset(&ip, 0, sizeof(ip));
    ip.version_ihl = 0x45;
    ip.protocol = 6;
    ip.src_ip = htonl(0xC0A80101); // 192.168.1.1
    ip.dest_ip = htonl(0xC0A80102); // 192.168.1.2
    
    struct tcp_connection *conn = create_connection(ip.dest_ip, 8080,
                                                  ip.src_ip, 12345);
    conn->state = TCP_ESTABLISHED;
    
    process_mynet_message(conn, msg_buffer, msg_len);
}

void simulate_file_sharing() {
    printf("\n=== Simulating File Sharing ===\n");
    
    // Add a shared file
    if (mynet_ctx) {
        add_shared_file(mynet_ctx, "document.txt", "/home/user/document.txt", 1024);
    }
    
    // Create file request
    uint8_t msg_buffer[512];
    const char *filename = "document.txt";
    int msg_len = create_mynet_message(msg_buffer, sizeof(msg_buffer),
                                      MYNET_FILE_REQUEST, MYNET_FLAG_SERVER_MODE,
                                      filename, strlen(filename));
    
    struct tcp_connection *conn = create_connection(0xC0A80102, 8080,
                                                  0xC0A80101, 12346);
    conn->state = TCP_ESTABLISHED;
    strcpy(conn->peer_name, "FileClient");
    
    process_mynet_message(conn, msg_buffer, msg_len);
}

void simulate_peer_discovery() {
    printf("\n=== Simulating Peer Discovery ===\n");
    
    // Create peer discovery message
    uint8_t msg_buffer[256];
    int msg_len = create_mynet_message(msg_buffer, sizeof(msg_buffer),
                                      MYNET_PEER_DISCOVER, MYNET_FLAG_P2P_MODE,
                                      NULL, 0);
    
    struct tcp_connection *conn = create_connection(0xC0A80102, 8080,
                                                  0xC0A80103, 12347);
    conn->state = TCP_ESTABLISHED;
    strcpy(conn->peer_name, "DiscoveryPeer");
    
    process_mynet_message(conn, msg_buffer, msg_len);
}

// Example usage demonstrating different modes
int main() {
    srand(time(NULL));
    
    // Initialize as a P2P node
    init_tcp_ip_stack(MYNET_NODE_PEER, "MyPeerNode", 8080);
    
    // Add some peers and files for demonstration
    if (mynet_ctx) {
        add_peer(mynet_ctx, 0xC0A80101, 8080, "Peer1", MYNET_NODE_PEER);
        add_peer(mynet_ctx, 0xC0A80103, 9090, "Server1", MYNET_NODE_SERVER);
        add_shared_file(mynet_ctx, "readme.txt", "/tmp/readme.txt", 512);
        add_shared_file(mynet_ctx, "music.mp3", "/music/song.mp3", 4096000);
    }
    
    // Simulate different protocol scenarios
    simulate_p2p_chat();
    simulate_file_sharing();
    simulate_peer_discovery();
    
    // Demonstrate protocol handshake
    printf("\n=== Simulating Protocol Handshake ===\n");
    uint8_t hello_buffer[256];
    const char *our_name = mynet_ctx ? mynet_ctx->node_name : "TestNode";
    int hello_len = create_mynet_message(hello_buffer, sizeof(hello_buffer),
                                          MYNET_HELLO, 0,
                                          our_name, strlen(our_name));
    
    struct tcp_connection *hello_conn = create_connection(0xC0A80102, 8080,
                                                         0xC0A80104, 12348);
    hello_conn->state = TCP_ESTABLISHED;
    
    process_mynet_message(hello_conn, hello_buffer, hello_len);
    
    // Show connection status
    printf("\n=== Connection Status ===\n");
    struct tcp_connection *conn = connections;
    int conn_count = 0;
    while (conn) {
        printf("Connection %d: %u.%u.%u.%u:%u <-> %u.%u.%u.%u:%u (State: %d, MyNet: %s)\n",
               ++conn_count,
               (conn->local_ip >> 24) & 0xFF, (conn->local_ip >> 16) & 0xFF,
               (conn->local_ip >> 8) & 0xFF, conn->local_ip & 0xFF, conn->local_port,
               (conn->remote_ip >> 24) & 0xFF, (conn->remote_ip >> 16) & 0xFF,
               (conn->remote_ip >> 8) & 0xFF, conn->remote_ip & 0xFF, conn->remote_port,
               conn->state, conn->mynet_active ? "Active" : "Inactive");
        
        if (conn->mynet_active && strlen(conn->peer_name) > 0) {
            printf("  Peer: %s (Last msg ID: %u)\n", conn->peer_name, conn->last_msg_id);
        }
        conn = conn->next;
    }
    
    // Show peer list
    if (mynet_ctx && mynet_ctx->peers) {
        printf("\n=== Known Peers ===\n");
        struct peer_info *peer = mynet_ctx->peers;
        int peer_count = 0;
        while (peer) {
            printf("Peer %d: %s at %u.%u.%u.%u:%u (Type: %s, Last seen: %ld)\n",
                   ++peer_count, peer->name,
                   (peer->ip >> 24) & 0xFF, (peer->ip >> 16) & 0xFF,
                   (peer->ip >> 8) & 0xFF, peer->ip & 0xFF, peer->port,
                   peer->type == MYNET_NODE_SERVER ? "Server" : 
                   peer->type == MYNET_NODE_PEER ? "Peer" : "Client",
                   peer->last_seen);
            peer = peer->next;
        }
    }
    
    // Show shared files
    if (mynet_ctx && mynet_ctx->files) {
        printf("\n=== Shared Files ===\n");
        struct shared_file *file = mynet_ctx->files;
        int file_count = 0;
        while (file) {
            printf("File %d: %s (%u bytes, checksum: 0x%08x)\n",
                   ++file_count, file->filename, file->size, file->checksum);
            printf("  Path: %s\n", file->path);
            file = file->next;
        }
    }
    
    printf("\n=== MyNet Protocol Demo Complete ===\n");
    printf("Total connections: %d\n", conn_count);
    
    // Cleanup
    cleanup_tcp_ip_stack();
    
    return 0;
}


// This code implements a custom TCP/IP stack with MyNet protocol support, including
// peer-to-peer communication, file sharing, and chat functionality. It demonstrates
// how to create, manage, and process connections, messages, and shared resources.
