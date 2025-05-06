/**
 * TCP Connection State Machine
 * 
 * This example demonstrates a simplified TCP state machine handling
 * connection establishment, data transfer, and termination.
 * 
 * See standard TCP state diagram (RFC 793)
 * https://www.rfc-editor.org/rfc/rfc793.html
 */

 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <stdbool.h>
 
 // TCP connection states
 typedef enum {
     CLOSED,
     LISTEN,
     SYN_SENT,
     SYN_RECEIVED,
     ESTABLISHED,
     FIN_WAIT_1,
     FIN_WAIT_2,
     CLOSE_WAIT,
     CLOSING,
     LAST_ACK,
     TIME_WAIT
 } TcpState;
 
 // TCP events
 typedef enum {
     ACTIVE_OPEN,        // App initiates connection
     PASSIVE_OPEN,       // App ready to accept connection
     RECEIVE_SYN,        // Receive SYN packet
     RECEIVE_ACK,        // Receive ACK packet
     RECEIVE_SYN_ACK,    // Receive SYN+ACK packet
     RECEIVE_FIN,        // Receive FIN packet
     RECEIVE_FIN_ACK,    // Receive FIN+ACK packet
     CLOSE,              // App closes connection
     TIMEOUT,            // Timeout occurred
     SEND,               // App wants to send data
     RECEIVE             // App received data
 } TcpEvent;
 
 // TCP Connection structure
 typedef struct {
     TcpState state;
     int connection_id;
     // other connection data would be here ..
 } TcpConnection;
 
 // fwd decl
 void initializeConnection(TcpConnection *conn, int id);
 void processEvent(TcpConnection *conn, TcpEvent event);
 const char* stateToString(TcpState state);
 const char* eventToString(TcpEvent event);
 
 
 // Init TCP connection
 void initializeConnection(TcpConnection *conn, int id) {
     conn->state = CLOSED;
     conn->connection_id = id;
 }
 
 // Process event and transition to new state if applicable
 void processEvent(TcpConnection *conn, TcpEvent event) {
     TcpState oldState = conn->state;
     bool validTransition = true;
     
     // State transition logic
     switch (conn->state) {
         case CLOSED:
             switch (event) {
                 case ACTIVE_OPEN:
                     conn->state = SYN_SENT;
                     printf("[Connection %d] Send SYN\n", conn->connection_id);
                     break;
                 case PASSIVE_OPEN:
                     conn->state = LISTEN;
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case LISTEN:
             switch (event) {
                 case RECEIVE_SYN:
                     conn->state = SYN_RECEIVED;
                     printf("[Connection %d] Send SYN+ACK\n", conn->connection_id);
                     break;
                 case CLOSE:
                     conn->state = CLOSED;
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case SYN_SENT:
             switch (event) {
                 case RECEIVE_SYN:
                     conn->state = SYN_RECEIVED;
                     printf("[Connection %d] Send ACK\n", conn->connection_id);
                     break;
                 case RECEIVE_SYN_ACK:
                     conn->state = ESTABLISHED;
                     printf("[Connection %d] Send ACK\n", conn->connection_id);
                     break;
                 case CLOSE:
                     conn->state = CLOSED;
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case SYN_RECEIVED:
             switch (event) {
                 case RECEIVE_ACK:
                     conn->state = ESTABLISHED;
                     break;
                 case CLOSE:
                     conn->state = FIN_WAIT_1;
                     printf("[Connection %d] Send FIN\n", conn->connection_id);
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case ESTABLISHED:
             switch (event) {
                 case CLOSE:
                     conn->state = FIN_WAIT_1;
                     printf("[Connection %d] Send FIN\n", conn->connection_id);
                     break;
                 case RECEIVE_FIN:
                     conn->state = CLOSE_WAIT;
                     printf("[Connection %d] Send ACK\n", conn->connection_id);
                     break;
                 case SEND:
                 case RECEIVE:
                     // stay in ESTABLISHED for data transfer
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case FIN_WAIT_1:
             switch (event) {
                 case RECEIVE_ACK:
                     conn->state = FIN_WAIT_2;
                     break;
                 case RECEIVE_FIN:
                     conn->state = CLOSING;
                     printf("[Connection %d] Send ACK\n", conn->connection_id);
                     break;
                 case RECEIVE_FIN_ACK:
                     conn->state = TIME_WAIT;
                     printf("[Connection %d] Send ACK\n", conn->connection_id);
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case FIN_WAIT_2:
             switch (event) {
                 case RECEIVE_FIN:
                     conn->state = TIME_WAIT;
                     printf("[Connection %d] Send ACK\n", conn->connection_id);
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case CLOSE_WAIT:
             switch (event) {
                 case CLOSE:
                     conn->state = LAST_ACK;
                     printf("[Connection %d] Send FIN\n", conn->connection_id);
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case CLOSING:
             switch (event) {
                 case RECEIVE_ACK:
                     conn->state = TIME_WAIT;
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case LAST_ACK:
             switch (event) {
                 case RECEIVE_ACK:
                     conn->state = CLOSED;
                     break;
                 default:
                     validTransition = false;
             }
             break;
             
         case TIME_WAIT:
             switch (event) {
                 case TIMEOUT:
                     conn->state = CLOSED;
                     break;
                 default:
                     validTransition = false;
             }
             break;
     }
     
     // State transition
     if (validTransition) {
         if (oldState != conn->state) {
             printf("[Connection %d] State changed: %s -> %s (Event: %s)\n",
                    conn->connection_id, stateToString(oldState), 
                    stateToString(conn->state), eventToString(event));
         } else {
             printf("[Connection %d] Handled event: %s (State: %s)\n",
                    conn->connection_id, eventToString(event), stateToString(conn->state));
         }
     } else {
         printf("[Connection %d] Invalid event %s for state %s\n",
                conn->connection_id, eventToString(event), stateToString(conn->state));
     }
     
     printf("\n");
 }
 
 // state --> string representation
 const char* stateToString(TcpState state) {
     switch (state) {
         case CLOSED: return "CLOSED";
         case LISTEN: return "LISTEN";
         case SYN_SENT: return "SYN_SENT";
         case SYN_RECEIVED: return "SYN_RECEIVED";
         case ESTABLISHED: return "ESTABLISHED";
         case FIN_WAIT_1: return "FIN_WAIT_1";
         case FIN_WAIT_2: return "FIN_WAIT_2";
         case CLOSE_WAIT: return "CLOSE_WAIT";
         case CLOSING: return "CLOSING";
         case LAST_ACK: return "LAST_ACK";
         case TIME_WAIT: return "TIME_WAIT";
         default: return "UNKNOWN";
     }
 }
 
 // event --> string representation
 const char* eventToString(TcpEvent event) {
     switch (event) {
         case ACTIVE_OPEN: return "ACTIVE_OPEN";
         case PASSIVE_OPEN: return "PASSIVE_OPEN";
         case RECEIVE_SYN: return "RECEIVE_SYN";
         case RECEIVE_ACK: return "RECEIVE_ACK";
         case RECEIVE_SYN_ACK: return "RECEIVE_SYN_ACK";
         case RECEIVE_FIN: return "RECEIVE_FIN";
         case RECEIVE_FIN_ACK: return "RECEIVE_FIN_ACK";
         case CLOSE: return "CLOSE";
         case TIMEOUT: return "TIMEOUT";
         case SEND: return "SEND";
         case RECEIVE: return "RECEIVE";
         default: return "UNKNOWN";
     }
 }


 // simulation ..
int main() {
    TcpConnection client, server;
    
    // init connections
    initializeConnection(&client, 1);
    initializeConnection(&server, 2);
    
    printf("=== TCP State Machine Simulation ===\n\n");
    
    // Simulate a typical TCP connection lifecycle
    
    // 1. Passive open (server)
    printf("Server: Waiting for connections...\n");
    processEvent(&server, PASSIVE_OPEN);
    
    // 2. Active open (client)
    printf("Client: Initiating connection...\n");
    processEvent(&client, ACTIVE_OPEN);
    
    // 3. Server receives SYN
    printf("Server: Received SYN packet\n");
    processEvent(&server, RECEIVE_SYN);
    
    // 4. Client receives SYN+ACK
    printf("Client: Received SYN+ACK packet\n");
    processEvent(&client, RECEIVE_SYN_ACK);
    
    // 5. Server receives ACK
    printf("Server: Received ACK packet\n");
    processEvent(&server, RECEIVE_ACK);
    
    // 6. Data transfer
    printf("Client: Sending data...\n");
    processEvent(&client, SEND);
    
    printf("Server: Receiving data...\n");
    processEvent(&server, RECEIVE);
    
    printf("Server: Sending response...\n");
    processEvent(&server, SEND);
    
    printf("Client: Receiving response...\n");
    processEvent(&client, RECEIVE);
    
    // 7. Client initiates connection termination
    printf("Client: Closing connection...\n");
    processEvent(&client, CLOSE);
    
    // 8. Server receives FIN
    printf("Server: Received FIN packet\n");
    processEvent(&server, RECEIVE_FIN);
    
    // 9. Server closes connection
    printf("Server: Closing connection...\n");
    processEvent(&server, CLOSE);
    
    // 10. Client receives FIN+ACK
    printf("Client: Received FIN+ACK packet\n");
    processEvent(&client, RECEIVE_FIN_ACK);
    
    // 11. Server receives ACK
    printf("Server: Received final ACK packet\n");
    processEvent(&server, RECEIVE_ACK);
    
    // 12. Client times out from TIME_WAIT
    printf("Client: Timeout in TIME_WAIT\n");
    processEvent(&client, TIMEOUT);
    
    return 0; // ok
}
