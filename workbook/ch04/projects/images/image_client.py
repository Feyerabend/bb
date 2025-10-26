import network
import socket
import utime
import ujson
import sys

# Try to import display, but make it optional for testing
try:
    from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
    DISPLAY_AVAILABLE = True
    print("Display library loaded")
except ImportError as e:
    print(f"Display not available: {e}")
    DISPLAY_AVAILABLE = False

# ============= Compression =============
class RLECompressor:
    """Simple Run-Length Encoding decoder"""
    
    @staticmethod
    def decompress(data):
        """Decompress RLE data"""
        decompressed = bytearray()
        i = 0
        while i < len(data) - 1:
            count = data[i]
            value = data[i + 1]
            decompressed.extend([value] * count)
            i += 2
        return bytes(decompressed)


# ============= Display Handler (Optional) =============
class ImageDisplay:
    def __init__(self):
        if not DISPLAY_AVAILABLE:
            self.display = None
            print("Display disabled - console only mode")
            return
            
        try:
            self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
            self.width = self.display.get_bounds()[0]
            self.height = self.display.get_bounds()[1]
            print(f"Display initialized: {self.width}x{self.height}")
        except Exception as e:
            print(f"Display init failed: {e}")
            self.display = None
        
    def clear(self, color=(0, 0, 0)):
        """Clear display"""
        if not self.display:
            return
        try:
            pen = self.display.create_pen(*color)
            self.display.set_pen(pen)
            self.display.clear()
            self.display.update()
        except Exception as e:
            print(f"Clear failed: {e}")
        
    def show_text(self, text, x=10, y=10, scale=2):
        """Display text"""
        print(f"Display: {text}")
        if not self.display:
            return
        try:
            self.display.set_pen(self.display.create_pen(255, 255, 255))
            self.display.text(text, x, y, scale=scale)
            self.display.update()
        except Exception as e:
            print(f"Show text failed: {e}")
        
    def display_image(self, image_data):
        """Display raw RGB565 image data"""
        if not self.display:
            print(f"Would display {len(image_data)} bytes")
            return
            
        if len(image_data) != self.width * self.height * 2:
            print(f"Warning: Image size mismatch!")
            print(f"Expected: {self.width * self.height * 2}, Got: {len(image_data)}")
        
        try:
            for y in range(min(self.height, len(image_data) // (self.width * 2))):
                for x in range(self.width):
                    idx = (y * self.width + x) * 2
                    if idx + 1 < len(image_data):
                        # Extract RGB565 pixel
                        pixel = (image_data[idx] << 8) | image_data[idx + 1]
                        r = ((pixel >> 11) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x3F) << 2
                        b = (pixel & 0x1F) << 3
                        
                        pen = self.display.create_pen(r, g, b)
                        self.display.set_pen(pen)
                        self.display.pixel(x, y)
            
            self.display.update()
            print("Image displayed")
        except Exception as e:
            print(f"Display image failed: {e}")


# ============= Network Client =============
class ImageClient:
    def __init__(self, server_ssid, server_password, server_ip, server_port=8080):
        self.server_ssid = server_ssid
        self.server_password = server_password
        self.server_ip = server_ip
        self.server_port = server_port
        self.wlan = None
        
    def connect_to_server(self):
        """Connect to server's WiFi AP"""
        print("\n=== WiFi Connection ===")
        print(f"SSID: {self.server_ssid}")
        print(f"Password: {self.server_password}")
        
        try:
            self.wlan = network.WLAN(network.STA_IF)
            print(f"WLAN object created: {self.wlan}")
            
            self.wlan.active(True)
            print("WLAN activated")
            
            # Wait for WLAN to become active
            timeout = 5
            while not self.wlan.active() and timeout > 0:
                print("Waiting for WLAN active...")
                utime.sleep(0.5)
                timeout -= 0.5
            
            if not self.wlan.active():
                raise RuntimeError("WLAN failed to activate")
            
            print("WLAN is active")
            print(f"Current status: {self.wlan.status()}")
            
            # Disconnect if already connected
            if self.wlan.isconnected():
                print("Already connected, disconnecting...")
                self.wlan.disconnect()
                utime.sleep(1)
            
            print(f"Connecting to '{self.server_ssid}'...")
            self.wlan.connect(self.server_ssid, self.server_password)
            
            # Wait for connection with detailed status
            max_wait = 15
            while max_wait > 0:
                status = self.wlan.status()
                print(f"Status: {status} ", end="")
                
                if status == 0:
                    print("(LINK_DOWN)")
                elif status == 1:
                    print("(LINK_JOIN)")
                elif status == 2:
                    print("(LINK_NOIP)")
                elif status == 3:
                    print("(LINK_UP - Connected!)")
                    break
                elif status < 0:
                    print("(LINK_FAIL)")
                    break
                else:
                    print(f"(Unknown: {status})")
                
                max_wait -= 1
                utime.sleep(1)
            
            if self.wlan.status() != 3:
                status = self.wlan.status()
                if status == -1:
                    raise RuntimeError("Connection failed: LINK_FAIL (-1) - Wrong password?")
                elif status == -2:
                    raise RuntimeError("Connection failed: NO_AP_FOUND (-2) - Cannot find network")
                elif status == -3:
                    raise RuntimeError("Connection failed: LINK_BADAUTH (-3) - Authentication failed")
                else:
                    raise RuntimeError(f"Connection failed with status: {status}")
            
            print("\n✓ Connected successfully!")
            config = self.wlan.ifconfig()
            print(f"IP Address: {config[0]}")
            print(f"Netmask: {config[1]}")
            print(f"Gateway: {config[2]}")
            print(f"DNS: {config[3]}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Connection error: {e}")
            import sys
            sys.print_exception(e)
            return False
        
    def list_images(self):
        """Get list of available images from server"""
        print("\n=== Listing Images ===")
        try:
            print(f"Connecting to {self.server_ip}:{self.server_port}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((self.server_ip, self.server_port))
            print("Socket connected")
            
            # Send LIST request
            s.send(b"LIST")
            print("Sent: LIST")
            
            # Receive response
            header = s.recv(256).decode()
            print(f"Received header: {header}")
            
            if not header.startswith("OK|"):
                print(f"Error response: {header}")
                s.close()
                return []
            
            # Parse header: OK|size|
            parts = header.split("|")
            data_size = int(parts[1])
            print(f"Expecting {data_size} bytes of JSON")
            
            # Receive JSON data
            data = s.recv(data_size).decode()
            print(f"Received: {data}")
            s.close()
            
            files = ujson.loads(data)
            print(f"Parsed {len(files)} files")
            return files
            
        except Exception as e:
            print(f"List error: {e}")
            import sys
            sys.print_exception(e)
            return []
    
    def get_image(self, filename):
        """Download and decompress image from server"""
        print(f"\n=== Getting Image: {filename} ===")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            print(f"Connecting to {self.server_ip}:{self.server_port}")
            s.connect((self.server_ip, self.server_port))
            print("Connected")
            
            # Send GET request
            request = f"GET|{filename}"
            s.send(request.encode())
            print(f"Sent: {request}")
            
            # Receive header
            header = b""
            while b"|" not in header or header.count(b"|") < 3:
                chunk = s.recv(1)
                if not chunk:
                    break
                header += chunk
            
            header = header.decode()
            print(f"Header: {header}")
            
            if not header.startswith("OK|"):
                print(f"Error: {header}")
                s.close()
                return None
            
            # Parse header: OK|original_size|compressed_size|
            parts = header.split("|")
            original_size = int(parts[1])
            compressed_size = int(parts[2])
            
            print(f"Original: {original_size} bytes")
            print(f"Compressed: {compressed_size} bytes")
            print("Downloading...")
            
            # Receive compressed data
            compressed_data = bytearray()
            while len(compressed_data) < compressed_size:
                remaining = compressed_size - len(compressed_data)
                chunk = s.recv(min(1024, remaining))
                if not chunk:
                    print("Connection closed early!")
                    break
                compressed_data.extend(chunk)
                
                # Progress indicator
                progress = len(compressed_data) / compressed_size * 100
                if len(compressed_data) % 10240 == 0 or len(compressed_data) == compressed_size:
                    print(f"  {len(compressed_data)}/{compressed_size} bytes ({progress:.1f}%)")
            
            s.close()
            print("Download complete")
            
            print("Decompressing...")
            image_data = RLECompressor.decompress(bytes(compressed_data))
            print(f"Decompressed: {len(image_data)} bytes")
            
            return image_data
            
        except Exception as e:
            print(f"Download error: {e}")
            import sys
            sys.print_exception(e)
            return None


# ============= Main Client =============
def main():
    print("\n" + "="*40)
    print("IMAGE CLIENT STARTING")
    print("="*40)
    
    # Configuration
    SERVER_SSID = "PicoImages"
    SERVER_PASSWORD = "raspberry"
    SERVER_IP = "192.168.4.1"  # Default AP IP
    SERVER_PORT = 8080
    
    print(f"\nConfiguration:")
    print(f"  Server SSID: {SERVER_SSID}")
    print(f"  Server IP: {SERVER_IP}:{SERVER_PORT}")
    
    # Initialize display (optional)
    try:
        display = ImageDisplay()
    except Exception as e:
        print(f"Display init error: {e}")
        display = None
    
    # Connect to image server
    client = ImageClient(
        server_ssid=SERVER_SSID,
        server_password=SERVER_PASSWORD,
        server_ip=SERVER_IP,
        server_port=SERVER_PORT
    )
    
    try:
        if display:
            display.show_text("Connecting...", 10, 100)
        
        # Connect to WiFi
        if not client.connect_to_server():
            print("\n✗ Failed to connect to WiFi")
            if display:
                display.show_text("WiFi Failed", 10, 100)
            return
        
        if display:
            display.show_text("Connected!", 10, 100)
        
        utime.sleep(1)
        
        # List available images
        if display:
            display.show_text("Listing...", 10, 100)
        
        files = client.list_images()
        
        print(f"\nAvailable images ({len(files)}):")
        for f in files:
            print(f"  {f['name']} - {f['size']} bytes")
        
        # Download and display first image
        if files:
            filename = files[0]['name']
            print(f"\nDownloading: {filename}")
            
            if display:
                display.clear()
                display.show_text(f"Loading...", 10, 100)
            
            image_data = client.get_image(filename)
            
            if image_data:
                print("✓ Success!")
                if display:
                    display.clear()
                    display.display_image(image_data)
            else:
                print("✗ Download failed")
                if display:
                    display.show_text("Failed", 10, 100)
        else:
            print("\nNo images found on server")
            if display:
                display.show_text("No images", 10, 100)
        
        print("\n" + "="*40)
        print("CLIENT FINISHED")
        print("="*40)
            
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import sys
        sys.print_exception(e)
        if display:
            display.clear()
            display.show_text("Error!", 10, 100)

if __name__ == "__main__":
    main