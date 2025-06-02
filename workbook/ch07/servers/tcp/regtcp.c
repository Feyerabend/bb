#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>

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

// Connection control block
struct tcp_connection {
    uint32_t local_ip;
    uint32_t remote_ip;
    uint16_t local_port;
    uint16_t remote_port;
    uint32_t seq_num;
    uint32_t ack_num;
    enum tcp_state state;
    struct tcp_connection *next;
};

// Global connection list
static struct tcp_connection *connections = NULL;

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
    
    // Verify checksum
    uint16_t original_checksum = ip->checksum;
    ip->checksum = 0;
    uint16_t calculated_checksum = ip_checksum(ip, header_len);
    ip->checksum = original_checksum;
    
    if (original_checksum != calculated_checksum) {
        printf("IP checksum mismatch\n");
        return -1;
    }
    
    // Process TCP packets
    if (ip->protocol == 6) {
        return process_tcp(packet + header_len, len - header_len, ip);
    }
    
    return 0;
}

// Process TCP segment
int process_tcp(uint8_t *packet, int len, struct ip_header *ip) {
    if (len < sizeof(struct tcp_header)) {
        return -1;
    }
    
    struct tcp_header *tcp = (struct tcp_header *)packet;
    
    uint16_t src_port = ntohs(tcp->src_port);
    uint16_t dest_port = ntohs(tcp->dest_port);
    uint32_t seq_num = ntohl(tcp->seq_num);
    uint32_t ack_num = ntohl(tcp->ack_num);
    
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
            // Send SYN-ACK (would need actual network interface)
            printf("Should send SYN-ACK\n");
        }
    }
    
    if (flags & 0x10) { // ACK
        printf("TCP ACK received\n");
        if (conn->state == TCP_SYN_RECEIVED) {
            conn->state = TCP_ESTABLISHED;
            printf("Connection established\n");
        }
    }
    
    if (flags & 0x01) { // FIN
        printf("TCP FIN received\n");
        if (conn->state == TCP_ESTABLISHED) {
            conn->state = TCP_CLOSE_WAIT;
            conn->ack_num = seq_num + 1;
            // Send ACK and FIN (would need actual network interface)
            printf("Should send ACK and FIN\n");
        }
    }
    
    return 0;
}

// Send TCP packet (simplified - would need actual network interface)
int send_tcp_packet(struct tcp_connection *conn, uint8_t flags, 
                   uint8_t *data, int data_len) {
    printf("Sending TCP packet with flags: 0x%02x\n", flags);
    
    // In a real implementation, you would:
    // 1. Build complete TCP header with checksum
    // 2. Build IP header with checksum
    // 3. Build Ethernet header
    // 4. Send via raw socket or network interface
    
    conn->seq_num += data_len;
    return 0;
}

// Initialize TCP/IP stack
int init_tcp_ip_stack() {
    printf("TCP/IP stack initialized\n");
    return 0;
}

// Cleanup TCP/IP stack
void cleanup_tcp_ip_stack() {
    struct tcp_connection *conn = connections;
    while (conn) {
        struct tcp_connection *next = conn->next;
        free(conn);
        conn = next;
    }
    connections = NULL;
    printf("TCP/IP stack cleaned up\n");
}

// Example usage
int main() {
    init_tcp_ip_stack();
    
    // Example: simulate receiving a TCP SYN packet
    printf("=== Simulating TCP connection ===\n");
    
    // Create a sample IP header
    struct ip_header ip;
    memset(&ip, 0, sizeof(ip));
    ip.version_ihl = 0x45;
    ip.protocol = 6; // TCP
    ip.src_ip = htonl(0xC0A80101); // 192.168.1.1
    ip.dest_ip = htonl(0xC0A80102); // 192.168.1.2
    
    // Create a sample TCP header with SYN flag
    struct tcp_header tcp;
    memset(&tcp, 0, sizeof(tcp));
    tcp.src_port = htons(12345);
    tcp.dest_port = htons(80);
    tcp.seq_num = htonl(1000);
    tcp.flags = 0x02; // SYN
    tcp.window_size = htons(8192);
    
    // Process the TCP packet
    process_tcp((uint8_t *)&tcp, sizeof(tcp), &ip);
    
    cleanup_tcp_ip_stack();
    return 0;
}


// This code provides a basic implementation of a TCP/IP stack with support for
// processing Ethernet frames, IP packets, and TCP segments. It includes functions
// for initialising and cleaning up the stack, managing TCP connections, and
// simulating TCP connection establishment.

