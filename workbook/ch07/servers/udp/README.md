
## UDP Client-Server Application

This project implements a robust UDP client-server application in C, designed for reliable communication
over UDP with support for multiple operational modes and commands. The application consists of two main
components: a UDP server (udp_server.c) and a UDP client (udp_client.c).

User Datagram Protocol (UDP) is a connectionless transport layer protocol in the TCP/IP protocol suite.
Unlike TCP, UDP does not establish a connection before sending data, nor does it guarantee delivery,
ordering, or error checking. This makes UDP faster and more lightweight, ideal for applications where
speed is critical, and occasional packet loss is acceptable, such as streaming, gaming, or real-time
communications.

* Connectionless: No handshake is required before data transmission.
* Unreliable: No built-in mechanisms for ensuring delivery or order of packets.
* Low Overhead: Minimal protocol overhead, leading to faster transmission.
* Datagram-Oriented: Data is sent in discrete packets (datagrams).

This project leverages UDP to create a flexible client-server system with features like message handling,
client tracking, and graceful shutdowns.

Features

__UDP Server (udp_server.c)__

Command Processing: Supports commands like PING, TIME, STATS, and ECHO, along with generic text messages.
Client Tracking: Maintains a list of up to 100 clients, tracking their IP, port, message count, and last activity time.
Periodic Maintenance: Cleans up inactive clients (idle for 5 minutes) and prints server statistics every 5 minutes.
Graceful Shutdown: Handles SIGINT and SIGTERM signals to close the socket cleanly and display final statistics.
Configurable Port: Defaults to port 8888 but can be overridden via command-line arguments.

__UDP Client (udp_client.c)__

Multiple Modes:
* Interactive Mode: Allows users to input commands/messages interactively.
* Batch Mode: Sends multiple messages specified via command-line arguments.
* Stress Test Mode: Sends a specified number of messages rapidly to test server performance.


- Command Support: Supports PING, TIME, STATS, ECHO, and arbitrary text messages.
- Timeout Handling: Implements a 5-second timeout for receiving server responses.
- Graceful Shutdown: Handles SIGINT and SIGTERM signals to close the socket cleanly.



### Code Details

### Common Features

- Both client and server use UDP sockets (SOCK_DGRAM) for communication.
- Signal handlers ensure graceful shutdowns by closing sockets and cleaning up resources.
- Error handling is robust, with appropriate checks for socket creation, binding, and data transmission.
- The BUFFER_SIZE is set to 1024 bytes, sufficient for most message types.


#### Server-Specific Details

- Client Management: Uses a client_info_t structure to store client details (IP, port, last seen time, message count).
- Periodic Tasks: A main loop with a 1-second receive timeout allows periodic cleanup of inactive clients and statistics printing.
- Message Processing: The process_message function handles different command types:
- PING: Responds with a timestamped PONG.
- TIME: Returns the current server time.
- STATS: Reports the number of active clients and the client's message count.
- ECHO <msg>: Echoes back the provided message.
- Other messages: Acknowledges with an ACK containing the message, timestamp, and message count.



#### Client-Specific Details

Operational Modes:
- Interactive Mode: Prompts the user for input, supports help, quit, and exit commands, and sends messages to the server.
- Batch Mode: Sends multiple messages provided as command-line arguments with a 100ms delay between each.
- Stress Test Mode: Sends a specified number of messages rapidly, reporting success/failure rates and performance metrics (messages/second).


Timeout Mechanism: Uses SO_RCVTIMEO to set a 5-second timeout for server responses, handling EWOULDBLOCK/EAGAIN errors for timeouts.

__Limitations__

- UDP's inherent unreliability means packets may be lost or arrive out of order.
- The server has a maximum client limit of 100 (MAX_CLIENTS).
- No encryption or authentication is implemented, so use in secure environments only.
- The client and server assume IPv4 addresses.

__Projects__

* Add IPv6 support.
* Implement basic authentication for client-server interactions.
* Add support for larger messages or message fragmentation.
* Enhance statistics with more detailed metrics (e.g., average response time).

