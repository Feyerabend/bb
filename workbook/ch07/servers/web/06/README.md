
## WebSocket Chat Server and Client

### WebSocket Server

This is a simple *WebSocket chat server** implemented using Python's standard
`socket` and `threading` libraries. It performs a WebSocket handshake manually
and supports broadcasting messages between connected clients.

- Listens for incoming TCP connections on port 8765.
- Performs a WebSocket upgrade handshake (as per RFC 6455).
- Receives messages from one client and *broadcasts* them to all others.
- Handles multiple clients using threads.
- Includes minimal frame decoding (only text, fixed-size).


### WebSocket Client

A simple *HTML and JavaScript frontend* that connects to the chat server over WebSocket.

- Connects to `ws://localhost:8765`.
- Lets the user enter a name and message.
- Displays received messages in a scrollable text box.
- Sends messages in plain text (`username: message` format).
- Automatically logs connection, disconnection, and errors.

This setup allows basic multi-user chat over WebSockets using only browser and Python sockets.
You test this by e.g. opening up clients in different browsers and tests towards the server,
at the same computer.


### Summary

| Feature                | WebSocket Server (Python)               | WebSocket Client (HTML/JS)            |
|--|--|--|
| Language               | Python                                  | HTML + JavaScript                     |
| Protocol               | WebSocket (RFC 6455)                    | WebSocket (via browser API)           |
| Handles Connections    | Yes (manual threading per client)       | Yes (single connection per tab)       |
| Message Format         | Raw WebSocket text frames               | `username: message` strings           |
| Broadcast Support      | Yes, to all connected clients           | Receives all messages via `.onmessage` |
| Frontend / UI          | None (console only)                     | Basic input/output UI in browser      |
| Concurrency            | Yes (via Python threads)                | Handled by browser                    |
| Use Case               | Educational, low-level WebSocket demo   | Local testing of chat functionality   |

This chat demonstrates a *full-duplex communication model*, where both client and server can send and receive
data independently. Unlike traditional HTTP servers, which are *stateless* and rely on short-lived request-response
cycles, WebSocket servers maintain *open and persistent* connections. This enables real-time interaction,
making WebSockets ideal for use cases like chat, collaborative tools, games, and live data feeds.

The server side showcases *manual handling of WebSocket frames*, providing insight into the protocol's internals.
The client shows how to easily use WebSockets from a browser.

Together, they portait a minimal but still functional *real-time chat* system.
