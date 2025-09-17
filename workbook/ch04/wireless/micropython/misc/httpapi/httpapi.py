import socket
import json
import time
from machine import Pin

class HTTPAPIServer:
    def __init__(self, port=80):
        self.port = port
        self.server_socket = None
        self.led = Pin(25, Pin.OUT)
        self.device_state = {
            'led': False,
            'uptime': 0,
            'requests_served': 0
        }
        self.setup_server()
    
    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"HTTP API Server listening on port {self.port}")
    
    def parse_http_request(self, request):
        lines = request.split('\r\n')
        if not lines:
            return None, None, {}
        
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) < 3:
            return None, None, {}
        
        method, path, version = parts[0], parts[1], parts[2]
        
        # Parse headers
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        return method, path, headers
    
    def create_json_response(self, data, status_code=200):
        response_body = json.dumps(data)
        
        status_messages = {
            200: "OK",
            201: "Created", 
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error"
        }
        
        status_text = status_messages.get(status_code, "Unknown")
        
        response = f"""HTTP/1.1 {status_code} {status_text}\r
Content-Type: application/json\r
Content-Length: {len(response_body)}\r
Access-Control-Allow-Origin: *\r
Connection: close\r
\r
{response_body}"""
        
        return response
    
    def handle_api_request(self, method, path):
        self.device_state['uptime'] = time.ticks_ms() // 1000
        self.device_state['requests_served'] += 1
        
        if path == '/api/status':
            if method == 'GET':
                return self.create_json_response(self.device_state)
            else:
                return self.create_json_response({'error': 'Method not allowed'}, 405)
        
        elif path == '/api/led':
            if method == 'GET':
                return self.create_json_response({'led_status': self.device_state['led']})
            elif method == 'POST':
                # Toggle LED state
                self.device_state['led'] = not self.device_state['led']
                self.led.value(self.device_state['led'])
                return self.create_json_response({
                    'message': f"LED {'turned on' if self.device_state['led'] else 'turned off'}",
                    'led_status': self.device_state['led']
                })
            else:
                return self.create_json_response({'error': 'Method not allowed'}, 405)
        
        elif path == '/api/led/on':
            if method in ['GET', 'POST']:
                self.device_state['led'] = True
                self.led.value(1)
                return self.create_json_response({
                    'message': 'LED turned on',
                    'led_status': True
                })
            else:
                return self.create_json_response({'error': 'Method not allowed'}, 405)
        
        elif path == '/api/led/off':
            if method in ['GET', 'POST']:
                self.device_state['led'] = False
                self.led.value(0)
                return self.create_json_response({
                    'message': 'LED turned off',
                    'led_status': False
                })
            else:
                return self.create_json_response({'error': 'Method not allowed'}, 405)
        
        else:
            return self.create_json_response({'error': 'Endpoint not found'}, 404)
    
    def handle_client(self, client_socket, client_addr):
        try:
            # Receive request with timeout
            client_socket.settimeout(5.0)
            request = client_socket.recv(1024).decode('utf-8')
            
            if not request:
                return
            
            method, path, headers = self.parse_http_request(request)
            
            if not method or not path:
                response = self.create_json_response({'error': 'Malformed request'}, 400)
            else:
                print(f"HTTP {method} {path} from {client_addr}")
                response = self.handle_api_request(method, path)
            
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            print(f"HTTP client error: {e}")
            try:
                error_response = self.create_json_response({'error': 'Internal server error'}, 500)
                client_socket.send(error_response.encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()
    
    def run(self):
        print("HTTP API Server running...")
        print("Available endpoints:")
        print("  GET  /api/status     - Device status")
        print("  GET  /api/led        - LED status")
        print("  POST /api/led        - Toggle LED")
        print("  GET  /api/led/on     - Turn LED on")
        print("  GET  /api/led/off    - Turn LED off")
        
        while True:
            try:
                client_socket, client_addr = self.server_socket.accept()
                self.handle_client(client_socket, client_addr)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"HTTP server error: {e}")
                time.sleep(1)
        
        self.server_socket.close()

# HTTP API server usage
http_api_server = HTTPAPIServer()
http_api_server.run()
