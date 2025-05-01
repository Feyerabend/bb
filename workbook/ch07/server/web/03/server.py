#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
import random
import time

# Game state
game_state = {
    "player": {"x": 100, "y": 100},
    "items": [
        {"id": 1, "x": 50, "y": 50, "collected": False},
        {"id": 2, "x": 200, "y": 150, "collected": False},
        {"id": 3, "x": 300, "y": 75, "collected": False},
        {"id": 4, "x": 150, "y": 250, "collected": False},
        {"id": 5, "x": 350, "y": 200, "collected": False}
    ],
    "score": 0,
    "lastUpdate": time.time()
}

class AjaxHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve static files for paths without /api/
        if not self.path.startswith('/api/'):
            return super().do_GET()
        
        # Set CORS headers for all responses
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Handle API endpoints
        if self.path == '/api/game-state':
            self.wfile.write(json.dumps(game_state).encode())
        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Handle different API endpoints
        if self.path == '/api/move-player':
            try:
                data = json.loads(post_data)
                game_state["player"]["x"] = data["x"]
                game_state["player"]["y"] = data["y"]
                
                # Check if player collected any items
                for item in game_state["items"]:
                    if not item["collected"]:
                        dx = abs(game_state["player"]["x"] - item["x"])
                        dy = abs(game_state["player"]["y"] - item["y"])
                        if dx < 30 and dy < 30:  # Collection radius
                            item["collected"] = True
                            game_state["score"] += 10
                
                game_state["lastUpdate"] = time.time()
                self.wfile.write(json.dumps({"success": True, "state": game_state}).encode())
            except json.JSONDecodeError:
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        
        elif self.path == '/api/reset-game':
            # Reset game state
            for item in game_state["items"]:
                item["collected"] = False
                item["x"] = random.randint(50, 450)
                item["y"] = random.randint(50, 350)
            game_state["player"]["x"] = 100
            game_state["player"]["y"] = 100
            game_state["score"] = 0
            game_state["lastUpdate"] = time.time()
            self.wfile.write(json.dumps({"success": True, "state": game_state}).encode())
        
        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    port = 8000
    handler = AjaxHandler
    handler.extensions_map.update({
        '.js': 'application/javascript',
        '.html': 'text/html',
        '.css': 'text/css',
    })
    
    # Ensure current directory is served
    handler.directory = "."
    server = socketserver.TCPServer(("", port), handler)
    
    print(f"Server running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    run_server()
