import json
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Enhanced inventory with more realistic data
INVENTORY = {
    "A001": {"name": "MacBook Pro", "stock": 12, "category": "electronics"},
    "A002": {"name": "iPhone 15", "stock": 25, "category": "electronics"},
    "B001": {"name": "Office Chair", "stock": 8, "category": "furniture"},
    "B002": {"name": "Standing Desk", "stock": 3, "category": "furniture"},
    "C001": {"name": "Coffee Beans", "stock": 50, "category": "food"},
    "C002": {"name": "Green Tea", "stock": 0, "category": "food"},  # Out of stock
}

class InventoryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Simulate occasional service delays
        if random.random() < 0.1:  # 10% chance
            time.sleep(2)
        
        if path.startswith("/items/"):
            self._handle_single_item(path)
        elif path == "/items":
            self._handle_all_items(query_params)
        elif path == "/health":
            self._handle_health()
        else:
            self._respond(404, {"error": "endpoint not found", "path": path})

    def _handle_single_item(self, path):
        sku = path.split("/")[-1]
        item = INVENTORY.get(sku)
        
        if item:
            # Add availability status
            response = {**item, "available": item["stock"] > 0, "sku": sku} #response = {*item, "available":  item["stock"] > 0, "sku": sku}
            self._respond(200, response)
        else:
            self._respond(404, {"error": "SKU not found", "sku": sku})

    def _handle_all_items(self, query_params):
        category = query_params.get("category", [None])[0]
        
        if category:
            filtered = {k: v for k, v in INVENTORY.items() if v["category"] == category}
            self._respond(200, filtered)
        else:
            self._respond(200, INVENTORY)

    def _handle_health(self):
        self._respond(200, {
            "status": "healthy",
            "service": "inventory",
            "timestamp": time.time(),
            "total_items": len(INVENTORY)
        })

    def _respond(self, code, payload):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("", 7001), InventoryHandler)
    print("   Inventory Service running on http://localhost:7001")
    print("   GET /items - list all items")
    print("   GET /items?category=electronics - filter by category")
    print("   GET /items/{sku} - get specific item")
    print("   GET /health - health check")
    server.serve_forever()
