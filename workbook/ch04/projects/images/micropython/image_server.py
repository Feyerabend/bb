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
            print("DEBUG: LED initialized on pin 25")
        except Exception as e:
            print(f"DEBUG: LED not available: {e}")
        
    def setup_access_point(self):
        print("\n" + "="*50)
        print("SETTING UP ACCESS POINT")
        print("="*50)
        
        # First, make sure STA interface is OFF
        print("\nDEBUG: Checking STA interface...")
        try:
            sta = network.WLAN(network.STA_IF)
            if sta.active():
                print("DEBUG: STA interface is active, deactivating...")
                sta.active(False)
                utime.sleep(2)
                print("DEBUG: STA interface deactivated")
            else:
                print("DEBUG: STA interface already inactive")
        except Exception as e:
            print(f"DEBUG: STA interface check error: {e}")
        
        # Create and configure AP
        print("\nDEBUG: Creating AP interface...")
        self.ap = network.WLAN(network.AP_IF)
        
        # Make sure it's off first
        if self.ap.active():
            print("DEBUG: AP was already active, deactivating first...")
            self.ap.active(False)
            utime.sleep(2)
        
        print(f"DEBUG: Activating AP with SSID: '{self.ssid}'")
        self.ap.active(True)
        utime.sleep(2)
        
        # Try multiple configuration methods
        print("\nDEBUG: Configuring AP...")
        config_success = False
        
        # Method 1: No password (open network)
        try:
            print("DEBUG: Trying config(essid=..., password='')...")
            self.ap.config(essid=self.ssid, password='')
            config_success = True
            print("DEBUG: Config method 1 succeeded")
        except Exception as e1:
            print(f"DEBUG: Config method 1 failed: {e1}")
            
            # Method 2: Just ESSID
            try:
                print("DEBUG: Trying config(essid=...)...")
                self.ap.config(essid=self.ssid)
                config_success = True
                print("DEBUG: Config method 2 succeeded")
            except Exception as e2:
                print(f"DEBUG: Config method 2 failed: {e2}")
                
                # Method 3: With channel
                try:
                    print("DEBUG: Trying config(essid=..., channel=6)...")
                    self.ap.config(essid=self.ssid, channel=6)
                    config_success = True
                    print("DEBUG: Config method 3 succeeded")
                except Exception as e3:
                    print(f"DEBUG: Config method 3 failed: {e3}")
        
        if not config_success:
            print("WARNING: All config methods failed, but continuing anyway...")
        
        # Wait for interface to become active and stable
        print("\nDEBUG: Waiting for AP to become active...")
        max_wait = 20
        while max_wait > 0:
            if self.ap.active():
                print(f"DEBUG: AP is active (waited {20-max_wait} seconds)")
                break
            print(".", end="")
            utime.sleep(1)
            max_wait -= 1
        
        if not self.ap.active():
            print("\nERROR: Failed to activate Access Point!")
            raise RuntimeError("AP activation failed")
        
        # Extra stabilization time
        print("\nDEBUG: Allowing AP to stabilize...")
        utime.sleep(3)
        
        # Get and display configuration
        try:
            config = self.ap.ifconfig()
            print("\n" + "-"*50)
            print("ACCESS POINT ACTIVE")
            print("-"*50)
            print(f"SSID: {self.ssid}")
            print(f"IP Address: {config[0]}")
            print(f"Netmask: {config[1]}")
            print(f"Gateway: {config[2]}")
            print(f"DNS: {config[3]}")
            
            # Try to get additional info
            try:
                print(f"\nDEBUG: AP Status: {self.ap.status()}")
            except:
                pass
            
            try:
                # Try to get MAC address
                mac = self.ap.config('mac')
                mac_str = ':'.join(['%02X' % b for b in mac])
                print(f"DEBUG: MAC Address: {mac_str}")
            except Exception as e:
                print(f"DEBUG: Could not get MAC: {e}")
            
            try:
                # Try to get channel
                channel = self.ap.config('channel')
                print(f"DEBUG: Channel: {channel}")
            except Exception as e:
                print(f"DEBUG: Could not get channel: {e}")
            
            print("-"*50)
            
            if self.led:
                self.led.value(1)
                print("DEBUG: LED turned on")
                
        except Exception as e:
            print(f"ERROR: Could not get AP config: {e}")
            import sys
            sys.print_exception(e)
    
    def setup_tcp_server(self):
        print("\n" + "="*50)
        print("SETTING UP TCP SERVER")
        print("="*50)
        
        try:
            print(f"DEBUG: Creating socket on port {self.port}...")
            addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
            print(f"DEBUG: Address info: {addr}")
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("DEBUG: Socket created")
            
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("DEBUG: SO_REUSEADDR set")
            
            self.server_socket.bind(addr)
            print(f"DEBUG: Socket bound to {addr}")
            
            self.server_socket.listen(5)
            print("DEBUG: Socket listening (backlog=5)")
            
            print(f"\nTCP SERVER READY on port {self.port}")
            print("="*50)
            
        except Exception as e:
            print(f"ERROR: Failed to setup TCP server: {e}")
            import sys
            sys.print_exception(e)
            raise
    
    def handle_list_request(self, conn):
        try:
            print("DEBUG: Processing LIST request...")
            files = self.vfs.list_files()
            response = ujson.dumps(files)
            
            # Send response with header
            header = f"OK|{len(response)}|\n"
            print(f"DEBUG: Sending header: {header.strip()}")
            conn.send(header.encode())
            print(f"DEBUG: Sending data: {len(response)} bytes")
            conn.send(response.encode())
            
            print(f"SUCCESS: Sent file list ({len(files)} files)")
        except Exception as e:
            error_msg = f"ERROR|{str(e)}\n"
            conn.send(error_msg.encode())
            print(f"ERROR: List error: {e}")
    
    def handle_get_request(self, conn, filename):
        try:
            print(f"DEBUG: Processing GET request for: {filename}")
            
            if not self.vfs.file_exists(filename):
                conn.send(b"ERROR|File not found\n")
                print(f"ERROR: File not found: {filename}")
                return
            
            print(f"DEBUG: Reading file: {filename}")
            raw_data = self.vfs.read_file(filename)
            print(f"DEBUG: Read {len(raw_data)} bytes")
            
            # Compress data
            print("DEBUG: Compressing...")
            compressed = RLECompressor.compress(raw_data)
            ratio = len(compressed) / len(raw_data) * 100 if len(raw_data) > 0 else 0
            print(f"DEBUG: Compressed to {len(compressed)} bytes ({ratio:.1f}%)")
            
            # Send header
            header = f"OK|{len(raw_data)}|{len(compressed)}|\n"
            print(f"DEBUG: Sending header: {header.strip()}")
            conn.send(header.encode())
            
            # Send compressed data in chunks
            chunk_size = 1024
            sent = 0
            for i in range(0, len(compressed), chunk_size):
                chunk = compressed[i:i+chunk_size]
                conn.send(chunk)
                sent += len(chunk)
                if sent % 10240 == 0 or sent == len(compressed):
                    print(f"DEBUG: Sent {sent}/{len(compressed)} bytes")
            
            print("SUCCESS: Transfer complete")
            
        except Exception as e:
            error_msg = f"ERROR|{str(e)}\n"
            conn.send(error_msg.encode())
            print(f"ERROR: Transfer error: {e}")
            import sys
            sys.print_exception(e)
    
    def handle_client_connection(self, client_socket, client_addr):
        print(f"\n{'='*50}")
        print(f"CLIENT CONNECTED: {client_addr}")
        print(f"{'='*50}")
        client_socket.settimeout(30.0)
        
        try:
            print("DEBUG: Waiting for request...")
            request = client_socket.recv(256).decode().strip()
            print(f"DEBUG: Received request: '{request}'")
            
            if request.startswith("LIST"):
                self.handle_list_request(client_socket)
                
            elif request.startswith("GET|"):
                parts = request.split("|")
                if len(parts) >= 2:
                    filename = parts[1]
                    self.handle_get_request(client_socket, filename)
                else:
                    client_socket.send(b"ERROR|Invalid GET format\n")
                    print("ERROR: Invalid GET format")
                    
            else:
                error_msg = b"ERROR|Unknown command. Use LIST or GET|filename\n"
                client_socket.send(error_msg)
                print(f"ERROR: Unknown command: {request}")
            
        except socket.timeout:
            print(f"ERROR: Client {client_addr} timed out")
        except Exception as e:
            print(f"ERROR: Error handling client {client_addr}: {e}")
            import sys
            sys.print_exception(e)
        finally:
            try:
                client_socket.close()
                print(f"DEBUG: Client socket closed")
            except:
                pass
            print(f"CLIENT DISCONNECTED: {client_addr}\n")
    
    def run(self):
        print("\n" + "="*50)
        print("IMAGE SERVER STARTING")
        print("="*50)
        
        self.setup_access_point()
        self.setup_tcp_server()
        
        print("\n" + "="*50)
        print("SERVER READY - WAITING FOR CLIENTS")
        print("="*50)
        print(f"\nInstructions for client:")
        print(f"1. Connect to WiFi: '{self.ssid}' (no password)")
        print(f"2. Client will connect to: 192.168.4.1:{self.port}")
        print("\nListening for connections...\n")
        
        try:
            while True:
                try:
                    print("DEBUG: Waiting for client connection...")
                    client_socket, client_addr = self.server_socket.accept()
                    self.handle_client_connection(client_socket, client_addr)
                    gc.collect()
                    print(f"DEBUG: Memory collected, free: {gc.mem_free()}")
                    
                except KeyboardInterrupt:
                    print("\n\nSERVER SHUTDOWN REQUESTED")
                    break
                except Exception as e:
                    print(f"ERROR: Server error: {e}")
                    import sys
                    sys.print_exception(e)
                    utime.sleep(1)
        finally:
            self.cleanup()
    
    def cleanup(self):
        print("\nDEBUG: Cleaning up...")
        if self.server_socket:
            try:
                self.server_socket.close()
                print("DEBUG: Server socket closed")
            except:
                pass
        if self.ap:
            self.ap.active(False)
            print("DEBUG: AP deactivated")
        if self.led:
            self.led.value(0)
            print("DEBUG: LED turned off")
        print("Server cleanup completed")


# Main Setup 
def main():
    print("\n" + "="*70)
    print(" "*20 + "IMAGE SERVER INITIALIZATION")
    print("="*70)
    
    # Print system info
    try:
        import sys
        print(f"\nSystem Information:")
        print(f"  Platform: {sys.platform}")
        print(f"  Version: {sys.version}")
        print(f"  Implementation: {sys.implementation}")
    except:
        pass
    
    # Initialize SD card
    try:
        print("\n" + "-"*50)
        print("Mounting SD card...")
        print("-"*50)
        
        cs = machine.Pin(1, machine.Pin.OUT)
        print("DEBUG: CS pin initialized (Pin 1)")
        
        spi = machine.SPI(0,
                          baudrate=1000000,
                          polarity=0,
                          phase=0,
                          bits=8,
                          firstbit=machine.SPI.MSB,
                          sck=machine.Pin(2),
                          mosi=machine.Pin(3),
                          miso=machine.Pin(4))
        print("DEBUG: SPI initialized (SPI0, 1MHz)")
        
        sd = sdcard.SDCard(spi, cs)
        print("DEBUG: SDCard object created")
        
        vfs_fat = uos.VfsFat(sd)
        print("DEBUG: VfsFat created")
        
        uos.mount(vfs_fat, "/sd")
        print("SUCCESS: SD card mounted at /sd")
        
    except Exception as e:
        print(f"ERROR: SD card error: {e}")
        import sys
        sys.print_exception(e)
        raise
    
    # Create VFS wrapper
    print("\nDEBUG: Creating VFS wrapper...")
    vfs = SimpleVFS("/sd")
    
    # Check for existing images
    files = vfs.list_files()
    if not files:
        print("\n" + "-"*50)
        print("No images found, creating test image...")
        print("-"*50)
        # For DisplayPack 2.0: 320x240 pixels, RGB565 format (2 bytes per pixel)
        test_data = bytearray()
        for i in range(320 * 240):
            val = (i % 256)
            test_data.append(val)
            test_data.append(val)
        vfs.create_file("test.img", bytes(test_data))
        print("SUCCESS: Test image created (test.img)")
    else:
        print(f"\n" + "-"*50)
        print(f"Found {len(files)} existing image(s):")
        print("-"*50)
        for f in files:
            print(f"  - {f['name']} ({f['size']} bytes)")
    
    # Start server
    print("\n" + "-"*50)
    print("Starting image server...")
    print("-"*50)
    server = ImageServer(vfs, ssid="PicoImages")
    server.run()

if __name__ == "__main__":
    main()
