

### WebSockets

Definition: *WebSockets provide a full-duplex, persistent communication channel over a single TCP connection between the browser (or other client) and a server.*

Key Characteristics:
- Bidirectional: Both client and server can send messages at any time without re-establishing a connection.
- Persistent: The connection remains open after initial handshake until explicitly closed by either side.
- Low overhead: Once established, there’s no repeated HTTP request/response overhead.
- Efficient for real-time: Ideal for chat, gaming, live updates, streaming, collaborative editing, etc.

Lifecycle:
1.	Browser makes HTTP request with Upgrade: websocket.
2.	Server responds with 101 Switching Protocols and accepts.
3.	TCP connection remains open for continuous message exchange.
4.	Either party can close the connection.

#### Example usage:

```javascript
const ws = new WebSocket("ws://localhost:8765");

ws.onopen = () => ws.send("Hello, server");
ws.onmessage = (event) => console.log("From server:", event.data);
```




### Web Workers

Definition: *Web Workers allow JavaScript code to run in a separate thread from the main UI thread, enabling parallel computation without freezing or blocking the browser interface.*

Key Characteristics:
- Concurrency: Heavy computation can be offloaded to a worker thread.
- Isolation: No access to DOM or window objects directly.
- Communication via messages: Data is passed back and forth via postMessage() and onmessage.

Types:
- Dedicated Workers: Used by one script (most common).
- Shared Workers: Can be accessed by multiple scripts.
- Service Workers: Specialized for intercepting network requests, caching, and offline support (not the same as Web Workers).

#### Example usage:

```python
// main.js
const worker = new Worker("worker.js");
worker.postMessage("Start work");

worker.onmessage = (e) => console.log("Worker says:", e.data);

// worker.js
onmessage = function(e) {
    const result = heavyComputation(e.data);
    postMessage(result);
};
```


#### WebSocket vs Web Worker

|Feature	|WebSocket	|Web Worker|
|Purpose	|Communication with a server	|Background computation in browser|
|Connection	|Over network (TCP)	|Local thread (in-browser)|
|Communication	|Server ↔ Client	|Main thread ↔ Worker thread|
|Use case example	|Live chat, game server, stock feed	|Math processing, data parsing|
|Access to DOM	|Yes (client side)	|No|

