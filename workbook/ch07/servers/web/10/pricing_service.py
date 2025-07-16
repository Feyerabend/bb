import json
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

# Pricing data with dynamic pricing logic
PRICING = {
    "A001": {"base_price": 2499.99, "discount": 0.1},
    "A002": {"base_price": 999.99, "discount": 0.05},
    "B001": {"base_price": 299.99, "discount": 0.0},
    "B002": {"base_price": 599.99, "discount": 0.15},
    "C001": {"base_price": 24.99, "discount": 0.0},
    "C002": {"base_price": 19.99, "discount": 0.0},
}

class PricingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/price/"):
            sku = self.path.split("/")[-1]
            self._handle_single_price(sku)
        elif self.path == "/health":
            self._handle_health()
        else:
            self._respond(404, {"error": "endpoint not found"})

    def do_POST(self):
        if self.path == "/prices":
            self._handle_bulk_pricing()
        else:
            self._respond(404, {"error": "endpoint not found"})

    def _handle_single_price(self, sku):
        # Simulate occasional pricing service failures
        if random.random() < 0.05:  # 5% failure rate
            self._respond(503, {"error": "pricing service temporarily unavailable"})
            return
        
        pricing = PRICING.get(sku)
        if pricing:
            price = self._calculate_price(pricing)
            self._respond(200, {
                "sku": sku,
                "price": price,
                "currency": "USD",
                "discount_applied": pricing["discount"] > 0
            })
        else:
            self._respond(404, {"error": "pricing not found", "sku": sku})

    def _handle_bulk_pricing(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length).decode())
        skus = data.get("skus", [])
        
        results = {}
        for sku in skus:
            pricing = PRICING.get(sku)
            if pricing:
                results[sku] = {
                    "price": self._calculate_price(pricing),
                    "currency": "USD",
                    "discount_applied": pricing["discount"] > 0
                }
            else:
                results[sku] = {"error": "pricing not found"}
        
        self._respond(200, {"prices": results})

    def _calculate_price(self, pricing):
        base = pricing["base_price"]
        discount = pricing["discount"]
        return round(base * (1 - discount), 2)

    def _handle_health(self):
        self._respond(200, {
            "status": "healthy",
            "service": "pricing",
            "timestamp": time.time()
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
    server = HTTPServer(("", 7003), PricingHandler)
    print("   Pricing Service running on http://localhost:7003")
    print("   GET /price/{sku} - get price for item")
    print("   POST /prices - bulk pricing (send {skus: [...]}")
    print("   GET /health - health check")
    server.serve_forever()
