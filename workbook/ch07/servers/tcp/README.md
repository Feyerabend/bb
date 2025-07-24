
## TCP/IP Stack with MyNet Protocol Implementation

This project provides a C-based implementation of a simplified TCP/IP stack (regtcp.c)
and an extended version with a custom application-layer protocol called MyNet (custom.c).
The code demonstrates the processing of Ethernet frames, IP packets, and TCP segments,
with additional support for peer-to-peer communication, file sharing, and chat
functionality in the MyNet protocol.


### Project Description

This repository contains two main C files:

`regtcp.c`: Implements a basic TCP/IP stack that processes Ethernet frames, IP packets,
and TCP segments. It supports connection tracking, state management, and basic TCP
handshake operations.

`custom.c`: Extends the TCP/IP stack with the MyNet protocol, a custom application-layer
protocol that adds support for peer-to-peer communication, file sharing, and chat functionality.


#### regtcp.c

- Ethernet Frame Processing: Parses Ethernet headers and identifies IP packets (EtherType 0x0800).
- IP Packet Processing: Validates IPv4 headers and calculates checksums to ensure data integrity.
- TCP Segment Processing: Handles TCP connection states (e.g., CLOSED, LISTEN, SYN_SENT, ESTABLISHED)
  and processes key TCP flags (SYN, ACK, FIN).
- Connection Management: Maintains a linked list of TCP connections with details like local/remote IP,
  ports, sequence numbers, and acknowledgment numbers.
- Checksum Calculation: Implements IP header checksum computation.
- Simulation: Includes a main function to simulate receiving a TCP SYN packet and demonstrate
  connection establishment.


#### custom.c

MyNet Protocol: Introduces a custom application-layer protocol with a defined header structure
(mynet_header) that includes a magic number, version, message type, flags, message ID, payload
length, and checksum.

Message Types: Supports various message types, such as:
* MYNET_HELLO and MYNET_HELLO_ACK for handshakes.
* MYNET_PEER_DISCOVER and MYNET_PEER_ANNOUNCE for peer-to-peer discovery.
* MYNET_CHAT_MSG for chat messages.
* MYNET_FILE_REQUEST and MYNET_FILE_RESPONSE for file sharing.
* MYNET_HEARTBEAT for connection keep-alive.
* MYNET_BYE for connection termination.


- Node Types: Defines client, server, and peer node types for flexible network configurations.
- Peer and File Management: Maintains lists of known peers and shared files, with functions to
  add and manage them.
- Enhanced Connection Tracking: Extends the TCP connection structure to include MyNet-specific
  state (e.g., peer name, last message ID, activity timestamp).
- Simulations: Demonstrates P2P chat, file sharing, peer discovery, and protocol handshakes
  through dedicated simulation functions.
- Checksums: Implements a simple checksum for MyNet payloads to ensure data integrity.


### Code Structure

Both files share core networking structures:

- `eth_header`: Defines the Ethernet frame header with source/destination MAC addresses and EtherType.
- `ip_header`: Defines the IPv4 header with fields like version, IHL, TOS, total length, and checksum.
- `tcp_header`: Defines the TCP header with source/destination ports, sequence/acknowledgment numbers,
   flags, and window size.
- `tcp_connection`: Tracks TCP connection details, including IPs, ports, sequence numbers, and state.

#### regtcp.c Specifics

- Connection State Machine: Implements a subset of the TCP state machine (e.g., CLOSED, SYN_RECEIVED,
  ESTABLISHED, CLOSE_WAIT).
- Packet Processing: Sequentially processes Ethernet, IP, and TCP layers, validating headers and
  checksums.
- Simplified Send: Includes a placeholder send_tcp_packet function (requires a real network interfac
  for full functionality).

#### custom.c Specifics

- MyNet Header: Adds a custom header with a magic number (0x4D594E45 or "MYNE"), version, and
  message-specific fields.
- Context Management: Introduces mynet_context to manage node type, name, listen port, peers,
  and shared files.
- Message Processing: Handles MyNet messages based on their type, updating connection state and
  triggering appropriate responses (e.g., HELLO_ACK for HELLO).
- Peer and File Lists: Maintains linked lists for peer discovery and file sharing, with functions
  to add and display them.
- Simulation Functions: Includes simulate_p2p_chat, simulate_file_sharing, and
  simulate_peer_discovery to demonstrate MyNet protocol capabilities.


__Compilation__

To compile the code, use a C compiler like gcc. Ensure you have the necessary headers
(arpa/inet.h for networking functions). Example:
```shell
gcc -o regtcp regtcp.c
gcc -o custom custom.c
```

__Running__

- `regtcp.c`: Run ./regtcp to simulate a TCP SYN packet processing and connection establishment.
- `custom.c`: Run ./custom to initialize a MyNet P2P node and simulate chat, file sharing,
            peer discovery, and protocol handshakes.


### Limitations

- No Network Interface: Both implementations are simulations and lack actual network I/O (e.g.,
  raw sockets). Functions like send_tcp_packet are placeholders.
- Simplified TCP: The TCP state machine is incomplete, supporting only basic states and transitions.
- MyNet Protocol: The custom protocol in custom.c is a simplified demonstration and lacks features
  like encryption, compression, or actual file transfers.
- Error Handling: Basic error checking is implemented, but robust error recovery is limited.
- Memory Management: Uses dynamic memory allocation with basic cleanup; real-world applications
  would need more robust memory handling.


### Projects

- Integrate with a real network interface (e.g., using libpcap or raw sockets).
- Implement full TCP state machine transitions and timeout handling.
- Add encryption and compression support for MyNet protocol messages.
- Implement actual file transfer mechanisms for file sharing.
- Enhance error handling and logging for better debugging.

#### Dependencies

- Standard C libraries (stdio.h, stdlib.h, string.h, stdint.h, time.h).
- Networking headers (arpa/inet.h) for IP address manipulation and byte order conversions.

