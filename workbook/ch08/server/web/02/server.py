# threaded server
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.respond(200, "Root")
        elif self.path == "/hook1":
            self.respond(200, "Hook 1 working")
        elif self.path == "/hook2":
            self.respond(200, "Hook 2 working")
        else:
            self.respond(404, "Not found")

    def respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

def run(server_class=ThreadingHTTPServer, handler_class=MyHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving threaded on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
