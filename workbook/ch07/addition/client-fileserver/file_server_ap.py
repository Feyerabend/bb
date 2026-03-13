import machine
import sdcard
import uos
import ujson
import utime
import _thread
import socket
import network
import gc

class FileServer:
    """
    Dual-core file server for MicroPython with AP mode
    Core 1: File operations (save, load, delete, stats) with chunked transfers
    Core 0: WebDAV-like TCP server
    """
    
    # Chunk size for file transfers (8KB - adjust based on available RAM)
    CHUNK_SIZE = 8192
    
    def __init__(self, mount_point="/sd", port=8080, ap_mode=True, 
                 ap_ssid="PicoFileServer", ap_password="pico1234"):
        self.mount_point = mount_point
        self.metadata_file = f"{mount_point}/.vfs_metadata.json"
        self.metadata = self._load_metadata()
        self.port = port
        
        # Access Point settings
        self.ap_mode = ap_mode
        self.ap_ssid = ap_ssid
        self.ap_password = ap_password
        self.ip_address = None
        
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
    
    # ========== NETWORK SETUP ==========
    
    def setup_access_point(self):
        """Setup device as WiFi Access Point"""
        print("Setting up Access Point...")
        
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        
        # Configure AP
        ap.config(essid=self.ap_ssid, password=self.ap_password)
        ap.config(channel=6)
        
        # Wait for AP to become active
        max_wait = 10
        while max_wait > 0:
            if ap.active():
                break
            max_wait -= 1
            utime.sleep(1)
        
        if ap.active():
            self.ip_address = ap.ifconfig()[0]
            print(f"✓ Access Point '{self.ap_ssid}' started")
            print(f"✓ Password: {self.ap_password}")
            print(f"✓ Server IP: {self.ip_address}")
            print(f"✓ Connect to WiFi and access: http://{self.ip_address}:{self.port}")
            return True
        else:
            print("✗ Failed to start Access Point")
            return False
    
    def setup_station_mode(self, ssid, password):
        """Connect to existing WiFi network"""
        print(f"Connecting to WiFi: {ssid}...")
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        
        # Wait for connection
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection...')
            utime.sleep(1)
        
        if wlan.status() != 3:
            print('✗ Network connection failed')
            return False
        else:
            self.ip_address = wlan.ifconfig()[0]
            print(f'✓ Connected to {ssid}')
            print(f'✓ IP: {self.ip_address}')
            print(f'✓ Access: http://{self.ip_address}:{self.port}')
            return True
    
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
                
                # Free memory after each operation
                gc.collect()
            
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
                # Return file info for chunked transfer
                file_info = self._get_file_info(filename)
                return {"id": request_id, "status": "OK", "data": file_info}
            
            elif cmd == "GET_CHUNK":
                filename = request.get("filename")
                offset = request.get("offset", 0)
                data = self._read_file_chunk(filename, offset)
                return {"id": request_id, "status": "OK", "data": data, "eof": len(data) < self.CHUNK_SIZE}
            
            elif cmd == "PUT_START":
                filename = request.get("filename")
                total_size = request.get("size", 0)
                self._start_file_write(filename, total_size)
                return {"id": request_id, "status": "OK", "message": f"Ready to receive '{filename}'"}
            
            elif cmd == "PUT_CHUNK":
                filename = request.get("filename")
                data = request.get("data")
                offset = request.get("offset", 0)
                self._write_file_chunk(filename, data, offset)
                return {"id": request_id, "status": "OK", "message": "Chunk written"}
            
            elif cmd == "PUT_COMPLETE":
                filename = request.get("filename")
                self._complete_file_write(filename)
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
            import sys
            sys.print_exception(e)
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
    
    def _get_file_info(self, filename):
        """Get file information for chunked transfer"""
        if filename not in self.metadata:
            raise FileNotFoundError(f"File '{filename}' not found")
        
        return {
            "name": filename,
            "size": self.metadata[filename]["size"],
            "chunk_size": self.CHUNK_SIZE
        }
    
    def _read_file_chunk(self, filename, offset):
        """Read a chunk of file data"""
        if filename not in self.metadata:
            raise FileNotFoundError(f"File '{filename}' not found")
        
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "rb") as f:
            f.seek(offset)
            return f.read(self.CHUNK_SIZE)
    
    def _start_file_write(self, filename, total_size):
        """Initialize file for chunked writing"""
        # Create/truncate file
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "wb") as f:
            pass  # Just create empty file
        
        # Initialize temp metadata
        now = utime.time()
        if filename in self.metadata:
            self.metadata[filename]["modified"] = now
        else:
            self.metadata[filename] = {"created": now}
        
        self.metadata[filename]["size"] = 0
        self.metadata[filename]["expected_size"] = total_size
    
    def _write_file_chunk(self, filename, data, offset):
        """Write a chunk of data to file"""
        full_path = f"{self.mount_point}/{filename}"
        
        # Append data
        with open(full_path, "r+b") as f:
            f.seek(offset)
            f.write(data)
        
        # Update size
        self.metadata[filename]["size"] = offset + len(data)
    
    def _complete_file_write(self, filename):
        """Finalize file after all chunks written"""
        # Update final metadata
        full_path = f"{self.mount_point}/{filename}"
        
        # Get actual file size
        try:
            stat = uos.stat(full_path)
            actual_size = stat[6]  # File size
            self.metadata[filename]["size"] = actual_size
        except:
            pass
        
        # Remove temp fields
        if "expected_size" in self.metadata[filename]:
            del self.metadata[filename]["expected_size"]
        
        self._save_metadata()
        print(f"✓ Completed: {filename} ({self.metadata[filename]['size']} bytes)")
    
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
            "used_percent": (total_size / total_space * 100) if total_space > 0 else 0,
            "chunk_size": self.CHUNK_SIZE
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
        
        print(f"Core 0: Listening on {self.ip_address}:{self.port}")
        
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
            # Read request headers
            request_data = b""
            conn.settimeout(2.0)
            
            while True:
                try:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    request_data += chunk
                    
                    # Check if we have complete headers
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
            
            # Route request
            self._route_request(conn, method, path, content_length, request_data)
            
        except Exception as e:
            print(f"Client handler error: {e}")
            import sys
            sys.print_exception(e)
            self._send_error(conn, 500, str(e))
    
    def _route_request(self, conn, method, path, content_length, request_data):
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
            # Get file (chunked)
            filename = path[5:]
            self._handle_get_chunked(conn, filename)
        
        elif method == "PUT" and path.startswith("file/"):
            # Upload file (chunked)
            filename = path[5:]
            self._handle_put_chunked(conn, filename, content_length, request_data)
        
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
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "LIST"}
        
        with self.lock:
            self.request_queue.append(request)
        
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
    
    def _handle_get_chunked(self, conn, filename):
        """Handle GET file request with chunked transfer"""
        # Get file info
        request_id = utime.ticks_ms()
        request = {"id": request_id, "cmd": "GET", "filename": filename}
        
        with self.lock:
            self.request_queue.append(request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] != "OK":
            self._send_error(conn, 404, response.get("message", "File not found"))
            return
        
        file_info = response["data"]
        file_size = file_info["size"]
        
        # Send headers
        header = f"HTTP/1.1 200 OK\r\n"
        header += f"Content-Type: application/octet-stream\r\n"
        header += f"Content-Length: {file_size}\r\n"
        header += f"Content-Disposition: attachment; filename=\"{filename}\"\r\n"
        header += "Access-Control-Allow-Origin: *\r\n"
        header += "Connection: close\r\n"
        header += "\r\n"
        conn.send(header.encode())
        
        # Send file in chunks
        offset = 0
        while offset < file_size:
            # Request chunk from Core 1
            chunk_id = utime.ticks_ms()
            chunk_request = {
                "id": chunk_id,
                "cmd": "GET_CHUNK",
                "filename": filename,
                "offset": offset
            }
            
            with self.lock:
                self.request_queue.append(chunk_request)
            
            chunk_response = self._wait_for_response(chunk_id)
            
            if chunk_response["status"] == "OK":
                chunk_data = chunk_response["data"]
                conn.send(chunk_data)
                offset += len(chunk_data)
                
                # Check if we're done
                if chunk_response.get("eof", False):
                    break
            else:
                break
            
            # Small delay and gc between chunks
            gc.collect()
        
        print(f"✓ Sent {filename} ({offset} bytes)")
    
    def _handle_put_chunked(self, conn, filename, content_length, request_data):
        """Handle PUT file request with chunked receiving"""
        # Start file write
        request_id = utime.ticks_ms()
        start_request = {
            "id": request_id,
            "cmd": "PUT_START",
            "filename": filename,
            "size": content_length
        }
        
        with self.lock:
            self.request_queue.append(start_request)
        
        response = self._wait_for_response(request_id)
        
        if response["status"] != "OK":
            self._send_error(conn, 500, response.get("message", "Error"))
            return
        
        # Get any body data that came with headers
        header_end = request_data.find(b"\r\n\r\n")
        body_data = b""
        if header_end != -1:
            body_data = request_data[header_end + 4:]
        
        # Receive file data in chunks
        offset = 0
        bytes_received = len(body_data)
        
        # Write first chunk if we have data
        if len(body_data) > 0:
            chunk_id = utime.ticks_ms()
            chunk_request = {
                "id": chunk_id,
                "cmd": "PUT_CHUNK",
                "filename": filename,
                "data": body_data,
                "offset": offset
            }
            
            with self.lock:
                self.request_queue.append(chunk_request)
            
            self._wait_for_response(chunk_id)
            offset += len(body_data)
            gc.collect()
        
        # Receive remaining data
        while bytes_received < content_length:
            try:
                chunk_size = min(self.CHUNK_SIZE, content_length - bytes_received)
                chunk = conn.recv(chunk_size)
                
                if not chunk:
                    break
                
                # Send chunk to Core 1
                chunk_id = utime.ticks_ms()
                chunk_request = {
                    "id": chunk_id,
                    "cmd": "PUT_CHUNK",
                    "filename": filename,
                    "data": chunk,
                    "offset": offset
                }
                
                with self.lock:
                    self.request_queue.append(chunk_request)
                
                self._wait_for_response(chunk_id)
                
                bytes_received += len(chunk)
                offset += len(chunk)
                
                # Free memory
                gc.collect()
                
            except OSError:
                break
        
        # Complete file write
        complete_id = utime.ticks_ms()
        complete_request = {
            "id": complete_id,
            "cmd": "PUT_COMPLETE",
            "filename": filename
        }
        
        with self.lock:
            self.request_queue.append(complete_request)
        
        final_response = self._wait_for_response(complete_id)
        
        if final_response["status"] == "OK":
            self._send_json_response(conn, 201, {"message": final_response["message"]})
        else:
            self._send_error(conn, 500, final_response.get("message", "Error"))
    
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
    
    def _wait_for_response(self, request_id, timeout_ms=10000):
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
        print("=" * 50)
        print("  MicroPython File Server")
        print("=" * 50)
        
        # Setup network
        if self.ap_mode:
            if not self.setup_access_point():
                print("Failed to start Access Point!")
                return
        
        print()
        print("Starting File Server...")
        
        # Start Core 1 (file handler)
        _thread.start_new_thread(self.file_handler_core, ())
        
        # Small delay to let Core 1 start
        utime.sleep(1)
        
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
        print("✓ SD card mounted successfully")
        return True
    except OSError as e:
        print(f"✗ Failed to initialize SD card: {e}")
        return False


if __name__ == "__main__":
    # Initialize SD card
    if initialize_sd_card():
        # Create and start file server in AP mode
        server = FileServer(
            mount_point="/sd",
            port=80,  # Use port 80 for easier access (http://192.168.4.1)
            ap_mode=True,
            ap_ssid="PicoFileServer",
            ap_password="pico1234"
        )
        server.start()
        
        # To use Station mode instead, comment above and use:
        # server = FileServer(mount_point="/sd", port=8080, ap_mode=False)
        # server.setup_station_mode("YourWiFiSSID", "YourPassword")
        # server.start()
