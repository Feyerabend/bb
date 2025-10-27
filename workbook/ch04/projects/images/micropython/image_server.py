import machine
import sdcard
import uos
import ujson
import utime
import network
import socket
import gc

# VFS Component 
class SimpleVFS:
    def __init__(self, mount_point="/sd"):
        self.mount_point = mount_point
        self.metadata_file = f"{mount_point}/.vfs_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        try:
            with open(self.metadata_file, "r") as f:
                return ujson.load(f)
        except:
            return {}
    
    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            ujson.dump(self.metadata, f)
    
    def create_file(self, filename, data, permissions="rw"):
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "wb") as f:
            if isinstance(data, str):
                f.write(data.encode())
            else:
                f.write(data)
        
        self.metadata[filename] = {
            "permissions": permissions,
            "created": utime.time(),
            "size": len(data)
        }
        self._save_metadata()
        print(f"Created: {filename} ({len(data)} bytes)")
    
    def read_file(self, filename):
        if filename not in self.metadata:
            raise FileNotFoundError(f"File not found: {filename}")
        
        if 'r' not in self.metadata[filename]["permissions"]:
            raise OSError(f"No read permission: {filename}")
        
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "rb") as f:
            return f.read()
    
    def list_files(self):
        return [{"name": f, "size": m["size"]} 
                for f, m in self.metadata.items()]
    
    def file_exists(self, filename):
        return filename in self.metadata
    
    def get_file_size(self, filename):
        if filename not in self.metadata:
            return None
        return self.metadata[filename]["size"]


# Compression RLE
class RLECompressor:    
    @staticmethod
    def compress(data):
        if len(data) == 0:
            return bytes()
        
        compressed = bytearray()
        i = 0
        while i < len(data):
            current = data[i]
            count = 1
            
            # Count consecutive identical bytes (max 255)
            while i + count < len(data) and data[i + count] == current and count < 255:
                count += 1
            
            compressed.append(count)
            compressed.append(current)
            i += count
        
        return bytes(compressed)
    
    @staticmethod
    def decompress(data):
        decompressed = bytearray()
        i = 0
        while i < len(data) - 1:
            count = data[i]
            value = data[i + 1]
            decompressed.extend([value] * count)
            i += 2
        return bytes(decompressed)


# Network Server 
class ImageServer:
    def __init__(self, vfs, ssid="PicoImages", port=8080):
        self.vfs = vfs
        self.ssid = ssid
        self.port = port
        self.ap = None
        self.server_socket = None
        self.led = None
        
        # Try to initialize LED
        try:
            self.led = machine.Pin(25, machine.Pin.OUT)
        except:
            print("LED not available")
        
    def setup_access_point(self):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        
        # Configure as open network (no password for ease of use)
        self.ap.config(essid=self.ssid, authmode=network.AUTH_OPEN)
        print(f"Open AP '{self.ssid}' created (no password)")
        
        # Wait for interface to become active
        max_wait = 10
        while max_wait > 0:
            if self.ap.active():
                break
            utime.sleep(1)
            max_wait -= 1
        
        if self.ap.active():
            config = self.ap.ifconfig()
            print(f"Access Point active!")
            print(f"  IP: {config[0]}")
            print(f"  Netmask: {config[1]}")
            print(f"  Gateway: {config[2]}")
            print(f"  DNS: {config[3]}")
            if self.led:
                self.led.value(1)  # Turn on LED to indicate AP is active
        else:
            print("Failed to activate Access Point")
            raise RuntimeError("AP activation failed")
    
    def setup_tcp_server(self):
        try:
            # Create and bind socket using getaddrinfo
            addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(addr)
            self.server_socket.listen(5)  # Allow up to 5 pending connections
            
            print(f"TCP server listening on port {self.port}")
        except Exception as e:
            print(f"Failed to setup TCP server: {e}")
            raise
    
    def handle_list_request(self, conn):
        try:
            files = self.vfs.list_files()
            response = ujson.dumps(files)
            
            # Send response with header
            header = f"OK|{len(response)}|\n"
            conn.send(header.encode())
            conn.send(response.encode())
            
            print(f"Sent file list: {len(files)} files")
        except Exception as e:
            error_msg = f"ERROR|{str(e)}\n"
            conn.send(error_msg.encode())
            print(f"List error: {e}")
    
    def handle_get_request(self, conn, filename):
        try:
            if not self.vfs.file_exists(filename):
                conn.send(b"ERROR|File not found\n")
                print(f"File not found: {filename}")
                return
            
            print(f"Reading: {filename}")
            raw_data = self.vfs.read_file(filename)
            print(f"Read {len(raw_data)} bytes")
            
            # Compress data
            print("Compressing..")
            compressed = RLECompressor.compress(raw_data)
            ratio = len(compressed) / len(raw_data) * 100 if len(raw_data) > 0 else 0
            print(f"Compressed to {len(compressed)} bytes ({ratio:.1f}%)")
            
            # Send header with newline: OK|original_size|compressed_size|\n
            header = f"OK|{len(raw_data)}|{len(compressed)}|\n"
            conn.send(header.encode())
            print(f"Sent header: {header.strip()}")
            
            # Send compressed data in chunks
            chunk_size = 1024
            sent = 0
            for i in range(0, len(compressed), chunk_size):
                chunk = compressed[i:i+chunk_size]
                conn.send(chunk)
                sent += len(chunk)
                if sent % 10240 == 0 or sent == len(compressed):
                    print(f"Sent {sent}/{len(compressed)} bytes")
            
            print("Transfer complete")
            
        except Exception as e:
            error_msg = f"ERROR|{str(e)}\n"
            conn.send(error_msg.encode())
            print(f"Transfer error: {e}")
            import sys
            sys.print_exception(e)
    
    def handle_client_connection(self, client_socket, client_addr):
        print(f"\nClient connected from {client_addr}")
        client_socket.settimeout(30.0)  # 30 second timeout
        
        try:
            # Receive request
            request = client_socket.recv(256).decode().strip()
            print(f"Request: {request}")
            
            if request.startswith("LIST"):
                self.handle_list_request(client_socket)
                
            elif request.startswith("GET|"):
                parts = request.split("|")
                if len(parts) >= 2:
                    filename = parts[1]
                    self.handle_get_request(client_socket, filename)
                else:
                    client_socket.send(b"ERROR|Invalid GET format\n")
                    
            else:
                client_socket.send(b"ERROR|Unknown command. Use LIST or GET|filename\n")
            
        except socket.timeout:
            print(f"Client {client_addr} timed out")
        except Exception as e:
            print(f"Error handling client {client_addr}: {e}")
            import sys
            sys.print_exception(e)
        finally:
            try:
                client_socket.close()
            except:
                pass
            print(f"Client {client_addr} disconnected\n")
    
    def run(self):
        print("\n" + "-"*50)
        print("IMAGE SERVER STARTING")
        print("-"*50)
        
        self.setup_access_point()
        self.setup_tcp_server()
        
        print("\nServer ready! Waiting for clients..")
        print(f"Connect to WiFi: {self.ssid} (no password)")
        print(f"Server IP: 192.168.4.1:{self.port}")
        print("="*50 + "\n")
        
        try:
            while True:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    self.handle_client_connection(client_socket, client_addr)
                    gc.collect()  # Clean up memory after each client
                    
                except KeyboardInterrupt:
                    print("\nServer shutdown requested")
                    break
                except Exception as e:
                    print(f"Server error: {e}")
                    import sys
                    sys.print_exception(e)
                    utime.sleep(1)
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if self.ap:
            self.ap.active(False)
        if self.led:
            self.led.value(0)
        print("Server cleanup completed")


# Main Setup 
def main():
    print("\n" + "-"*50)
    print("INIT IMAGE SERVER")
    print("-"*50)
    
    # Initialize SD card
    try:
        print("\nMounting SD card..")
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
        vfs_fat = uos.VfsFat(sd)
        uos.mount(vfs_fat, "/sd")
        print("SD card mounted successfully")
    except Exception as e:
        print(f"SD card error: {e}")
        import sys
        sys.print_exception(e)
        raise
    
    # Create VFS wrapper
    vfs = SimpleVFS("/sd")
    
    # Check for existing images or create test data
    files = vfs.list_files()
    if not files:
        print("\nNo images found, creating test image..")
        # For DisplayPack 2.0: 320x240 pixels, RGB565 format (2 bytes per pixel)
        # Create a simple gradient test pattern
        test_data = bytearray()
        for i in range(320 * 240):
            # Simple gradient pattern
            val = (i % 256)
            test_data.append(val)
            test_data.append(val)
        vfs.create_file("test.img", bytes(test_data))
        print("Test image created: test.img")
    else:
        print(f"\nFound {len(files)} existing images:")
        for f in files:
            print(f"  - {f['name']} ({f['size']} bytes)")
    
    # Start server
    print("\nStarting image server..")
    server = ImageServer(vfs, ssid="PicoImages")
    server.run()

if __name__ == "__main__":
    main()
