
## Threaded Sample

This Python server uses `http.server.BaseHTTPRequestHandler` with `ThreadingHTTPServer`,
which means each incoming HTTP request is handled in its *own thread*. This allows the
server to handle multiple requests *concurrently*, instead of one at a time.

The server defines three basic endpoints:
- `/` responds with `"Root"`
- `/hook1` responds with `"Hook 1 working"`
- `/hook2` responds with `"Hook 2 working"`
- Any other path returns a `404 Not Found` response

It illustrates a *basic hook or API testing server*, where each path simulates a different
handler or service.

The HTML file (`client.html`) provides a very simple browser interface for testing the
threaded server. It includes buttons that:
- Call different paths (`/`, `/hook1`, `/hook2`, `/notfound`)
- Display the result in a `<pre>` block using JavaScript and the Fetch API

This is a minimal front-end to manually trigger and test server responses, useful for
local development or simulating hook-style integrations.


| Feature                | Threaded Python Server              | HTML Client                     |
|----|----|----|
| Language               | Python                              | HTML + JavaScript                |
| Purpose                | Handle HTTP requests with simple routing | Send HTTP requests to server     |
| Concurrency            | Yes (via `ThreadingHTTPServer`)     | N/A (browser runs JavaScript)    |
| Input/Interaction      | From browser or tools like `curl`   | Button clicks trigger requests   |
| Routing                | `/`, `/hook1`, `/hook2`, fallback  | Calls these routes via buttons   |
| Use Case               | Simulating backend hooks or APIs    | Testing frontend interaction or hook endpoints |
