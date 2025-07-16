import json
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

# Service endpoints
INVENTORY_SVC = "http://localhost:7001"
PRICING_SVC = "http://localhost:7003"

# Simple circuit breaker implementation
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, *kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e

# Circuit breakers for each service
inventory_breaker = CircuitBreaker()
pricing_breaker = CircuitBreaker()

def fetch_with_timeout(url, timeout=5):
    """Fetch URL with timeout and error handling"""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise Exception(f"HTTP {e.code}: {e.reason}")
    except Exception as e:
        raise Exception(f"Network error: {str(e)}")

def fetch_item(sku):
    """Fetch item with circuit breaker"""
    try:
        return inventory_breaker.call(fetch_with_timeout, f"{INVENTORY_SVC}/items/{sku}")
    except Exception:
        return None

def fetch_price(sku):
    """Fetch price with circuit breaker and fallback"""
    try:
        return pricing_breaker.call(fetch_with_timeout, f"{PRICING_SVC}/price/{sku}")
    except Exception:
        # Fallback pricing when service is down
        return {"sku": sku, "price": 0.00, "currency": "USD", "fallback": True}

class OrderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/orders":
            self._handle_create_order()
        else:
            self._respond(404, {"error": "endpoint not found"})

    def do_GET(self):
        if self.path == "/health":
            self._handle_health()
        else:
            self._respond(404, {"error": "endpoint not found"})

    def _handle_create_order(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            order_data = json.loads(self.rfile.read(length).decode())
            
            skus = order_data.get("skus", [])
            customer_id = order_data.get("customer_id", "anonymous")
            
            if not skus:
                self._respond(400, {"error": "no SKUs provided"})
                return

            # Validate inventory
            unavailable_items = []
            order_items = []
            
            for sku in skus:
                item = fetch_item(sku)
                if not item:
                    unavailable_items.append(sku)
                elif not item.get("available", False):
                    unavailable_items.append(sku)
                else:
                    order_items.append(item)

            if unavailable_items:
                self._respond(400, {
                    "error": "items unavailable",
                    "unavailable_skus": unavailable_items
                })
                return

            # Get pricing for all items
            order_total = 0
            enriched_items = []
            
            for item in order_items:
                sku = item["sku"]
                price_info = fetch_price(sku)
                
                enriched_item = {
                    "sku": sku,
                    "name": item["name"],
                    "price": price_info["price"],
                    "currency": price_info["currency"],
                    "fallback_pricing": price_info.get("fallback", False)
                }
                enriched_items.append(enriched_item)
                order_total += price_info["price"]

            # Create order response
            order_id = f"ORD-{int(time.time())}"
            response = {
                "order_id": order_id,
                "status": "confirmed",
                "customer_id": customer_id,
                "items": enriched_items,
                "total": round(order_total, 2),
                "currency": "USD",
                "timestamp": time.time()
            }
            
            self._respond(201, response)
            
        except json.JSONDecodeError:
            self._respond(400, {"error": "invalid JSON"})
        except Exception as e:
            self._respond(500, {"error": "internal server error", "details": str(e)})

    def _handle_health(self):
        # Check downstream services
        inventory_status = "healthy"
        pricing_status = "healthy"
        
        try:
            inventory_breaker.call(fetch_with_timeout, f"{INVENTORY_SVC}/health")
        except:
            inventory_status = "unhealthy"
        
        try:
            pricing_breaker.call(fetch_with_timeout, f"{PRICING_SVC}/health")
        except:
            pricing_status = "unhealthy"
        
        overall_status = "healthy" if inventory_status == "healthy" and pricing_status == "healthy" else "degraded"
        
        self._respond(200, {
            "status": overall_status,
            "service": "order",
            "timestamp": time.time(),
            "dependencies": {
                "inventory": inventory_status,
                "pricing": pricing_status
            },
            "circuit_breakers": {
                "inventory": inventory_breaker.state,
                "pricing": pricing_breaker.state
            }
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
    server = HTTPServer(("", 7002), OrderHandler)
    print("   Order Service running on http://localhost:7002")
    print("   POST /orders - create order")
    print("   GET /health - health check")
    server.serve_forever()
