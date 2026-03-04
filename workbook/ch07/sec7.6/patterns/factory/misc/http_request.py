import json
from typing import Dict, Optional, Any
from urllib.parse import urlencode, urljoin

class HttpRequest:
    def __init__(self):
        self.method: str = "GET"
        self.url: str = ""
        self.headers: Dict[str, str] = {}
        self.query_params: Dict[str, Any] = {}
        self.body: Optional[Any] = None
        self.timeout: Optional[float] = None

    def __str__(self):
        parts = [f"{self.method} {self.url}"]
        if self.query_params:
            parts.append(f"?{urlencode(self.query_params)}")
        if self.headers:
            parts.append(f"Headers: {self.headers}")
        if self.body is not None:
            parts.append(f"Body: {json.dumps(self.body, indent=2) if isinstance(self.body, dict) else self.body}")
        if self.timeout:
            parts.append(f"Timeout: {self.timeout}s")
        return "\n".join(parts)

    # Imagine a .send() method that would actually make the request


class HttpRequestBuilder:
    def __init__(self, base_url: str = ""):
        self.request = HttpRequest()
        self.base_url = base_url.rstrip("/")

    def get(self) -> 'HttpRequestBuilder':
        self.request.method = "GET"
        return self

    def post(self) -> 'HttpRequestBuilder':
        self.request.method = "POST"
        return self

    def path(self, path: str) -> 'HttpRequestBuilder':
        self.request.url = urljoin(self.base_url + "/", path.lstrip("/"))
        return self

    def header(self, key: str, value: str) -> 'HttpRequestBuilder':
        self.request.headers[key] = value
        return self

    def query(self, key: str, value: Any) -> 'HttpRequestBuilder':
        self.request.query_params[key] = value
        return self

    def json_body(self, data: Dict) -> 'HttpRequestBuilder':
        self.request.body = data
        self.header("Content-Type", "application/json")
        return self

    def timeout(self, seconds: float) -> 'HttpRequestBuilder':
        self.request.timeout = seconds
        return self

    def build(self) -> HttpRequest:
        if not self.request.url:
            raise ValueError("URL (at least path) must be set")
        return self.request


# Usage examples – feels like building a small "request construction algorithm"

# Simple GET
req1 = (HttpRequestBuilder("https://api.example.com")
        .get()
        .path("/users")
        .query("role", "admin")
        .query("limit", 20)
        .header("Authorization", "Bearer xyz123")
        .timeout(10.0)
        .build())

print("Request 1:")
print(req1)
# Output:
# GET https://api.example.com/users?role=admin&limit=20
# Headers: {'Authorization': 'Bearer xyz123', 'Content-Type': 'application/json'}
# Timeout: 10.0s

# POST with JSON body
req2 = (HttpRequestBuilder("https://api.example.com")
        .post()
        .path("/orders/create")
        .json_body({
            "items": ["book", "pen"],
            "total": 45.99,
            "customer_id": 1234
        })
        .header("X-Request-ID", "abc-789")
        .build())

print("\nRequest 2:")
print(req2)
# Output:
# POST https://api.example.com/orders/create
# Headers: {'Content-Type': 'application/json', 'X-Request-ID': 'abc-789'}
# Body: {
#   "items": [
#     "book",
#     "pen"
#   ],
#   "total": 45.99,
#   "customer_id": 1234
# }
