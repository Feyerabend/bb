
### C Server

This is a *minimal HTTP server* written in C. It listens on port 8080 and returns a
fixed plain-text response (`"Hello, World!"`) for every incoming HTTP request. It manually
handles low-level socket setup (creating, binding, listening, accepting connections) and
sends raw HTTP response headers and content directly. It doesn’t serve files or parse
requests--just responds with a hardcoded string.

### Python Server

This is a *basic file-serving web server* using Python’s built-in `http.server` module.
It automatically serves files from the current directory over HTTP. For example, if
there's an `index.html`, it will be displayed in the browser. It abstracts away the
lower-level socket logic and provides a simple way to serve static content with few
lines of code.

### Summary

A *web server* is a program that listens for HTTP requests (typically from web browsers)
and returns responses--usually HTML, files, or data. At its core, it:
- Waits for a connection
- Receives a request (like “GET /index.html”)
- Decides how to respond
- Sends back a response, often including content and metadata

Some web servers are *low-level*, giving full control (like the C example), while others
are more *high-level*, providing built-in behavior (like the Python example).

| Feature                | C Server                         | Python Server (`http.server`)        |
|------------------------|----------------------------------|--------------------------------------|
| Language               | C                                | Python                               |
| Lines of Code          | ~50                              | ~10                                  |
| Response               | Fixed string ("Hello, World!")   | Serves actual files from disk        |
| Abstraction Level      | Low-level (manual sockets)       | High-level (built-in HTTP handler)   |
| Ease of Use            | Requires more boilerplate        | Very simple to start and use         |
| Flexibility            | Full control over behavior       | Good for simple static serving       |
| Use Case               | Learning, embedded, custom logic | Quick tests, simple static hosting   |
