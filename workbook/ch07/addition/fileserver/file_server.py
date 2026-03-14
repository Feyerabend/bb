import machine
import sdcard
import uos
import ujson
import utime
import _thread
import socket
import gc

class FileServer:
    """
    Dual-core file server for MicroPython
    Core 1: File operations (save, load, delete, stats)
    Core 0: WebDAV-like TCP server
    """
    
    def __init__(self, mount_point="/sd", port=8080):
        self.mount_point = mount_point
        self.metadata_file = f"{mount_point}/.vfs_metadata.json"
        self.metadata = self._load_metadata()
        self.port = port
        
        # Inter-core communication
        self.request_queue = []
        self.response_queue = []
        self.lock = _thread.allocate_lock()
        self.running = True
        
        print(f"FileServer initialized on {mount_point}")
    
    def _load_metadata(self):
        """Load metadata from SD card"""
        try:
            with open(self.metadata_file, "r") as f:
                return ujson.load(f)
        except:
            return {}
    
    def _save_metadata(self):
        """Save metadata to SD card"""
        with open(self.metadata_file, "w") as f:
            ujson.dump(self.metadata, f)
    
    # ========== CORE 1: File Operations ==========
    
    def file_handler_core(self):
        """Run on Core 1 - handles all file operations"""
        print("Core 1: File handler started")
        
        while self.running:
            # Check for requests from Core 0
            if len(self.request_queue) > 0:
                with self.lock:
                    if len(self.request_queue) > 0:
                        request = self.request_queue.pop(0)
                
                # Process request
                response = self._process_request(request)
                
                # Send response back
                with self.lock:
                    self.response_queue.append(response)
            
            utime.sleep_ms(10)  # Small delay to prevent busy-waiting
        
        print("Core 1: File handler stopped")
    
    def _process_request(self, request):
        """Process file operation requests"""
        cmd = request.get("cmd")
        request_id = request.get("id")
        
        try:
            if cmd == "LIST":
                result = self._list_files()
                return {"id": request_id, "status": "OK", "data": result}
            
            elif cmd == "GET":
                filename = request.get("filename")
                data = self._read_file(filename)
                return {"id": request_id, "status": "OK", "data": data, "filename": filename}
            
            elif cmd == "PUT":
                filename = request.get("filename")
                data = request.get("data")
                self._write_file(filename, data)
                return {"id": request_id, "status": "OK", "message": f"File '{filename}' saved"}
            
            elif cmd == "DELETE":
                filename = request.get("filename")
                self._delete_file(filename)
                return {"id": request_id, "status": "OK", "message": f"File '{filename}' deleted"}
            
            elif cmd == "STATS":
                stats = self._get_stats()
                return {"id": request_id, "status": "OK", "data": stats}
            
            elif cmd == "EXISTS":
                filename = request.get("filename")
                exists = filename in self.metadata
                return {"id": request_id, "status": "OK", "exists": exists}
            
            else:
                return {"id": request_id, "status": "ERROR", "message": f"Unknown command: {cmd}"}
        
        except Exception as e:
            return {"id": request_id, "status": "ERROR", "message": str(e)}
    
    def _list_files(self):
        """List all files with metadata"""
        files = []
        for filename, meta in self.metadata.items():
            files.append({
                "name": filename,
                "size": meta["size"],
                "created": meta.get("created", 0),
                "modified": meta.get("modified", 0)
            })
        return files
    
    def _read_file(self, filename):
        """Read file contents"""
        if filename not in self.metadata:
            raise FileNotFoundError(f"File '{filename}' not found")
        
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "rb") as f:
            return f.read()
    
    def _write_file(self, filename, data):
        """Write or create file"""
        full_path = f"{self.mount_point}/{filename}"
        
        # Write the actual file
        with open(full_path, "wb") as f:
            if isinstance(data, str):
                f.write(data.encode())
            else:
                f.write(data)
        
        # Update metadata
        now = utime.time()
        if filename in self.metadata:
            self.metadata[filename]["modified"] = now
        else:
            self.metadata[filename] = {"created": now}
        
        self.metadata[filename]["size"] = len(data) if isinstance(data, bytes) else len(data.encode())
        self._save_metadata()
    
    def _delete_file(self, filename):
        """Delete file"""
        if filename not in self.metadata:
            raise FileNotFoundError(f"File '{filename}' not found")
        
        full_path = f"{self.mount_point}/{filename}"
        uos.remove(full_path)
        del self.metadata[filename]
        self._save_metadata()
    
    def _get_stats(self):
        """Get SD card and VFS statistics"""
        total_files = len(self.metadata)
        total_size = sum(meta["size"] for meta in self.metadata.values())
        
        # Get actual SD card stats
        try:
            statvfs = uos.statvfs(self.mount_point)
            block_size = statvfs[0]
            total_blocks = statvfs[2]
            free_blocks = statvfs[3]
            total_space = total_blocks * block_size
            free_space = free_blocks * block_size
        except:
            total_space = free_space = 0
        
        return {
            "files": total_files,
            "used_by_vfs": total_size,
            "total_space": total_space,
            "free_space": free_space,
            "used_percent": (total_size / total_space * 100) if total_space > 0 else 0
        }
    
    # ========== CORE 0: TCP Server ==========
    
    def tcp_server_core(self):
        """Run on Core 0 - handles WebDAV-like TCP requests"""
        print(f"Core 0: TCP server starting on port {self.port}")
        
        # Create socket
        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        
        print(f"Core 0: Listening on port {self.port}")
        
        while self.running:
            try:
                # Accept connection with timeout
                s.settimeout(1.0)
                try:
                    conn, addr = s.accept()
                except OSError:
                    continue  # Timeout, loop again
                
                print(f"Connection from {addr}")
                
                # Handle the request
                self._handle_client(conn)
                conn.close()
                
                # Garbage collect to free memory
                gc.collect()
                
            except Exception as e:
                print(f"Server error: {e}")
        
        s.close()
        print("Core 0: TCP server stopped")
    
    def _handle_client(self, conn):
        """Handle a single client connection"""
        try:
            # Read request
            request_data = b""
            conn.settimeout(2.0)
            
            while True:
                try:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    request_data += chunk
                    
                    # Check if we have a complete HTTP request
                    if b"\r\n\r\n" in request_data:
                        break
                except OSError:
                    break
            
            if not request_data:
                return
            
            # Parse HTTP request
            request_str = request_data.decode('utf-8', 'ignore')
            lines = request_str.split('\r\n')
            
            if len(lines) == 0:
                return
            
            # Parse request line
            request_line = lines[0].split(' ')
            if len(request_line) < 2:
                return
            
            method = request_line[0]
            path = request_line[1]
            
            # Get content length for PUT requests
            content_length = 0
            for line in lines:
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':')[1].strip())
            
            # Get body for PUT requests
            body = b""
            if content_length > 0:
                header_end = request_data.find(b"\r\n\r\n")
                if header_end != -1:
                    body = request_data[header_end + 4:]
                    
                    # Read remaining body if needed
                    while len(body) < content_length:
                        chunk = conn.recv(min(1024, content_length - len(body)))
                        if not chunk:
                            break
                        body += chunk
            
            # Route request
            self._route_request(conn, method, path, body)
            
        except Exception as e:
            print(f"Client handler error: {e}")
            self._send_error(conn, 500, str(e))
    
    def _route_request(self, conn, method, path, body):
        """Route HTTP request to appropriate handler"""
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        
        # Route based on method and path
        if method == "GET" and path == "":
            # List files
            self._handle_list(conn)
        
        elif method == "GET" and path == "stats":
            # Get statistics
            self._handle_stats(conn)
        
        elif method == "GET" and path.startswith("file/"):
            # Get file
            filename = path[5:]  # Remove "file/" prefix
            self._handle_get(conn, filename)
        
        elif method == "PUT" and path.startswith("file/"):
            # Upload file
            filename = path[5:]
            self._handle_put(conn, filename, body)
        
        elif method == "DELETE" and path.startswith("file/"):
            # Delete file
            filename = path[5:]
            self._handle_delete(conn, filename)
        
        elif method == "HEAD" and path.startswith("file/"):
            # Check if file exists
            filename = path[5:]
            self._handle_exists(conn, filename)
        
        else:
            self._send_error(conn, 404, "Not Found")
    
    def _handle_list(self, conn):
        """Handle LIST request"""
        # Send request to Core 1
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "LIST"}
        
        with self.lock:
            self.request_queue.append(request)
        
        # Wait for response
        response = self._wait_for_response(request_id)
        
        if response["status"] == "OK":
            self._send_json_response(conn, 200, response["data"])
        else:
            self._send_error(conn, 500, response.get("message", "Error"))
    
    def _handle_stats(self, conn):
        """Handle STATS request"""
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "STATS"}
        
        with self.lock:
            self.request_queue.append(request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] == "OK":
            self._send_json_response(conn, 200, response["data"])
        else:
            self._send_error(conn, 500, response.get("message", "Error"))
    
    def _handle_get(self, conn, filename):
        """Handle GET file request"""
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "GET", "filename": filename}
        
        with self.lock:
            self.request_queue.append(request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] == "OK":
            self._send_binary_response(conn, 200, response["data"])
        else:
            self._send_error(conn, 404, response.get("message", "File not found"))
    
    def _handle_put(self, conn, filename, data):
        """Handle PUT file request"""
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "PUT", "filename": filename, "data": data}
        
        with self.lock:
            self.request_queue.append(request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] == "OK":
            self._send_json_response(conn, 201, {"message": response["message"]})
        else:
            self._send_error(conn, 500, response.get("message", "Error"))
    
    def _handle_delete(self, conn, filename):
        """Handle DELETE file request"""
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "DELETE", "filename": filename}
        
        with self.lock:
            self.request_queue.append(request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] == "OK":
            self._send_json_response(conn, 200, {"message": response["message"]})
        else:
            self._send_error(conn, 404, response.get("message", "File not found"))
    
    def _handle_exists(self, conn, filename):
        """Handle HEAD/EXISTS request"""
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "EXISTS", "filename": filename}
        
        with self.lock:
            self.request_queue.append(request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] == "OK" and response["exists"]:
            self._send_response(conn, 200, "OK", b"")
        else:
            self._send_response(conn, 404, "Not Found", b"")
    
    def _wait_for_response(self, request_id, timeout_ms=5000):
        """Wait for response from Core 1"""
        start = utime.ticks_ms()
        
        while utime.ticks_diff(utime.ticks_ms(), start) < timeout_ms:
            with self.lock:
                for i, response in enumerate(self.response_queue):
                    if response["id"] == request_id:
                        return self.response_queue.pop(i)
            
            utime.sleep_ms(10)
        
        return {"id": request_id, "status": "ERROR", "message": "Timeout"}
    
    def _send_response(self, conn, code, status, body):
        """Send HTTP response"""
        response = f"HTTP/1.1 {code} {status}\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        
        conn.send(response.encode())
        if body:
            conn.send(body)
    
    def _send_json_response(self, conn, code, data):
        """Send JSON response"""
        json_str = ujson.dumps(data)
        body = json_str.encode()
        
        response = f"HTTP/1.1 {code} OK\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        
        conn.send(response.encode())
        conn.send(body)
    
    def _send_binary_response(self, conn, code, data):
        """Send binary file response"""
        response = f"HTTP/1.1 {code} OK\r\n"
        response += f"Content-Type: application/octet-stream\r\n"
        response += f"Content-Length: {len(data)}\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        
        conn.send(response.encode())
        conn.send(data)
    
    def _send_error(self, conn, code, message):
        """Send error response"""
        body = ujson.dumps({"error": message}).encode()
        
        response = f"HTTP/1.1 {code} Error\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        
        conn.send(response.encode())
        conn.send(body)
    
    # ========== Main Control ==========
    
    def start(self):
        """Start the file server on both cores"""
        print("Starting File Server...")
        
        # Start Core 1 (file handler)
        _thread.start_new_thread(self.file_handler_core, ())
        
        # Run Core 0 (TCP server) on main thread
        self.tcp_server_core()
    
    def stop(self):
        """Stop the file server"""
        print("Stopping File Server...")
        self.running = False


# ========== Initialization and Startup ==========

def initialize_sd_card():
    """Initialize SD card with SPI"""
    try:
        cs = machine.Pin(1, machine.Pin.OUT)
        spi = machine.SPI(0,
                          baudrate=1000000,
                          polarity=0,
                          phase=0,
                          bits=8,
                          firstbit=machine.SPI.MSB,
                          sck=machine.Pin(2),
                          mosi=machine.Pin(3),
                          miso=machine.Pin(4))
        sd = sdcard.SDCard(spi, cs)
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")
        print("SD card mounted successfully")
        return True
    except OSError as e:
        print(f"Failed to initialize SD card: {e}")
        return False


if __name__ == "__main__":
    # Initialize SD card
    if initialize_sd_card():
        # Create and start file server
        server = FileServer(mount_point="/sd", port=8080)
        server.start()
