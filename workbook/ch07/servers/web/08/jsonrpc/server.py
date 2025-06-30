#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid

# Simple in-memory database
class Database:
    def __init__(self):
        self.data = {}
    
    def item_create(self, params):
        item = params
        item_id = str(uuid.uuid4())
        item['id'] = item_id
        self.data[item_id] = item
        return item
    
    def item_read(self, params):
        item_id = params.get('id')
        if item_id:
            return self.data.get(item_id)
        return list(self.data.values())
    
    def item_update(self, params):
        item_id = params.get('id')
        updates = params.get('updates', {})
        if item_id in self.data:
            item = self.data[item_id]
            for key, value in updates.items():
                if key != 'id':  # Don't allow changing the id
                    item[key] = value
            return item
        return {"error": "Item not found"}
    
    def item_delete(self, params):
        item_id = params.get('id')
        if item_id in self.data:
            return self.data.pop(item_id)
        return {"error": "Item not found"}

# Initialize database
db = Database()

class JSONRPCHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
        
    def do_GET(self):
        if self.path == '/':
            # Serve index.html for root path
            with open('index.html', 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        elif self.path.endswith('.js'):
            # Serve JavaScript files
            try:
                with open(self.path[1:], 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/javascript')
                    self.end_headers()
                    self.wfile.write(file.read())
            except:
                self.send_error(404, 'File not found')
        else:
            self.send_error(404, 'File not found')
    
    def do_POST(self):
        if self.path == '/jsonrpc':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request = json.loads(post_data)
                response = self.handle_jsonrpc(request)
                
                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_error(404, 'Endpoint not found')
    
    def handle_jsonrpc(self, request):
        # Check for required fields
        if 'jsonrpc' not in request or request['jsonrpc'] != '2.0' or 'method' not in request:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
                "id": request.get('id')
            }
        
        method = request['method']
        params = request.get('params', {})
        req_id = request.get('id')
        
        # Method dispatch
        method_map = {
            'item.create': db.item_create,
            'item.read': db.item_read,
            'item.update': db.item_update,
            'item.delete': db.item_delete
        }
        
        if method in method_map:
            try:
                result = method_map[method](params)
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": req_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                    "id": req_id
                }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": req_id
            }

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, JSONRPCHandler)
    print(f"JSON-RPC server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
