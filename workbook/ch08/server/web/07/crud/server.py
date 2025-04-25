#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import uuid

# in-memory database
class Database:
    def __init__(self):
        self.data = {}
    
    def create(self, item):
        item_id = str(uuid.uuid4())
        item['id'] = item_id
        self.data[item_id] = item
        return item
    
    def read(self, item_id=None):
        if item_id:
            return self.data.get(item_id)
        return list(self.data.values())
    
    def update(self, item_id, updates):
        if item_id in self.data:
            item = self.data[item_id]
            for key, value in updates.items():
                if key != 'id':  # don't allow changing the id
                    item[key] = value
            return item
        return None
    
    def delete(self, item_id):
        if item_id in self.data:
            return self.data.pop(item_id)
        return None

# init database
db = Database()

class CRUDHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts[0] == 'items':
            if len(path_parts) > 1:
                # specific item
                item = db.read(path_parts[1])
                if item:
                    self._set_headers()
                    self.wfile.write(json.dumps(item).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Item not found"}).encode())
            else:
                # all items
                self._set_headers()
                self.wfile.write(json.dumps(db.read()).encode())
        elif path_parts[0] == '':
            # index.html for root path
            with open('index.html', 'rb') as file:
                self._set_headers(content_type='text/html')
                self.wfile.write(file.read())
        else:
            # static files
            try:
                with open(self.path[1:], 'rb') as file:
                    if self.path.endswith('.js'):
                        self._set_headers(content_type='application/javascript')
                    elif self.path.endswith('.css'):
                        self._set_headers(content_type='text/css')
                    elif self.path.endswith('.html'):
                        self._set_headers(content_type='text/html')
                    else:
                        self._set_headers(content_type='application/octet-stream')
                    self.wfile.write(file.read())
            except:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        if self.path == '/items':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                item = json.loads(post_data)
                result = db.create(item)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_PUT(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts[0] == 'items' and len(path_parts) > 1:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            try:
                updates = json.loads(put_data)
                result = db.update(path_parts[1], updates)
                if result:
                    self._set_headers()
                    self.wfile.write(json.dumps(result).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Item not found"}).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts[0] == 'items' and len(path_parts) > 1:
            result = db.delete(path_parts[1])
            if result:
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Item not found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CRUDHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()