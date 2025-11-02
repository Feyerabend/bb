import network
import socket
import utime
import ujson
import gc

# Try to import display, but make it optional for testing
try:
    from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
    DISPLAY_AVAILABLE = True
    print("Display library loaded")
except ImportError as e:
    print(f"Display not available: {e}")
    DISPLAY_AVAILABLE = False

class RLECompressor:    
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
            print(f"Display initialised: {self.width}x{self.height}")
        except Exception as e:
            print(f"Display init failed: {e}")
            self.display = None
        
    def clear(self, color=(0, 0, 0)):
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
        print(f"Display: {text}")
        if not self.display:
            return
        try:
            self.display.set_pen(self.display.create_pen(255, 255, 255))
            self.display.text(text, x, y, scale=scale)
            self.display.update()
        except Exception as e:
            print(f"Show text failed: {e}")
        
    # raw RGB565 image data!
    def display_image(self, image_data):
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


class ImageClient:
    def __init__(self, server_ssid, server_ip, server_port=8080):
        self.server_ssid = server_ssid
        self.server_ip = server_ip
        self.server_port = server_port
        self.wlan = None
        self.led = None
        
        # Try to initialize LED
        try:
            from machine import Pin
            self.led = Pin(25, Pin.OUT)
        except:
            print("LED not available")
        
    def connect_to_network(self):
        print("\nInitializing WiFi...")
        
        # Make sure WiFi is off first
        try:
            self.wlan = network.WLAN(network.STA_IF)
            if self.wlan.active():
                print("Deactivating existing WiFi...")
                self.wlan.active(False)
                utime.sleep(1)
        except:
            pass
        
        # Now activate it fresh
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # Wait for WiFi to actually become active
        print("Activating WiFi interface...")
        max_wait = 10
        while max_wait > 0 and not self.wlan.active():
            print(".", end="")
            utime.sleep(0.5)
            max_wait -= 1
        
        if not self.wlan.active():
            print("\n✗ Failed to activate WiFi interface!")
            return False
        
        print("\n✓ WiFi interface active")
        utime.sleep(2)  # Give it time to stabilize
        
        print(f"\nScanning for networks...")
        utime.sleep(1)  # Additional time for scan
        
        # Try to scan for networks (but don't fail if scan doesn't work)
        try:
            networks = self.wlan.scan()
            if networks and len(networks) > 0:
                print(f"Found {len(networks)} networks:")
                found_target = False
                for net in networks:
                    ssid = net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0]
                    print(f"  - {ssid} (RSSI: {net[3]})")
                    if ssid == self.server_ssid:
                        found_target = True
                        print(f"    ^ Target network found!")
                
                if not found_target:
                    print(f"\nWARNING: '{self.server_ssid}' not found in scan!")
            else:
                print("Scan returned empty - this is OK, will try connecting anyway")
        except Exception as e:
            print(f"Scan not available (this is normal on some boards): {e}")
        
        print(f"\nAttempting to connect to '{self.server_ssid}'..")
        
        # Disconnect first if already connected
        if self.wlan.isconnected():
            print("Disconnecting from previous network...")
            self.wlan.disconnect()
            utime.sleep(1)
        
        # Try different connection methods for compatibility
        try:
            # Method 1: Connect with just SSID (for open networks)
            self.wlan.connect(self.server_ssid)
            print("Connection method: SSID only (open network)")
        except TypeError:
            try:
                # Method 2: Connect with empty password
                self.wlan.connect(self.server_ssid, '')
                print("Connection method: SSID + empty password")
            except Exception as e2:
                print(f"Connection error: {e2}")
                return False
        
        # Wait for connection with detailed status updates
        max_wait = 30  # Increased timeout
        while max_wait > 0:
            status = self.wlan.status()
            
            # Print status code for debugging
            status_msg = {
                0: "IDLE",
                1: "CONNECTING", 
                2: "WRONG_PASSWORD",
                3: "NO_AP_FOUND",
                -1: "FAILED",
                -2: "CONNECT_FAIL",
                -3: "GOT_IP"
            }
            
            if status in status_msg:
                if max_wait % 5 == 0:  # Print every 5 seconds
                    print(f"\nStatus: {status_msg.get(status, status)}")
            
            if self.wlan.isconnected():
                print("\n✓ Connected successfully!")
                config = self.wlan.ifconfig()
                print(f"Network configuration:")
                print(f"  IP: {config[0]}")
                print(f"  Netmask: {config[1]}")
                print(f"  Gateway: {config[2]}")
                print(f"  DNS: {config[3]}")
                if self.led:
                    self.led.value(1)  # Indicate successful connection
                return True
            
            # Check for error statuses
            if status < 0 and status != -3:  # -3 is actually success on some platforms
                print(f"\n✗ Connection failed with status: {status_msg.get(status, status)}")
                return False
            
            # Print progress indicator
            print(".", end="")
            utime.sleep(1)
            max_wait -= 1
        
        print(f"\n✗ Connection timeout - failed to connect to '{self.server_ssid}'")
        print(f"Final status: {self.wlan.status()}")
        return False
        
    def list_images(self):
        print("\n--- Listing Images ---")
        sock = None
        try:
            print(f"Connecting to {self.server_ip}:{self.server_port}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((self.server_ip, self.server_port))
            print("Socket connected")
            
            # Send LIST request
            sock.send(b"LIST\n")
            print("Sent: LIST")
            
            # Receive response header - read until we get the complete header
            header = b""
            while b"\n" not in header:
                chunk = sock.recv(1)
                if not chunk:
                    break
                header += chunk
            
            header = header.decode().strip()
            print(f"Received header: {header}")
            
            if not header.startswith("OK|"):
                print(f"Error response: {header}")
                return []
            
            # Parse header: OK|size|
            parts = header.split("|")
            if len(parts) < 2:
                print("Invalid header format")
                return []
            
            data_size = int(parts[1])
            print(f"Expecting {data_size} bytes of JSON")
            
            # Receive JSON data
            data = b""
            while len(data) < data_size:
                chunk = sock.recv(min(1024, data_size - len(data)))
                if not chunk:
                    break
                data += chunk
            
            data = data.decode()
            print(f"Received: {data}")
            
            files = ujson.loads(data)
            print(f"Parsed {len(files)} files")
            return files
            
        except Exception as e:
            print(f"List error: {e}")
            import sys
            sys.print_exception(e)
            return []
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    def get_image(self, filename):
        print(f"\n--- Getting Image: {filename} ---")
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30.0)
            print(f"Connecting to {self.server_ip}:{self.server_port}")
            sock.connect((self.server_ip, self.server_port))
            print("Connected")
            
            # Send GET request
            request = f"GET|{filename}\n"
            sock.send(request.encode())
            print(f"Sent: {request.strip()}")
            
            # Receive header - read until newline
            header = b""
            while b"\n" not in header:
                chunk = sock.recv(1)
                if not chunk:
                    print("Connection closed while reading header")
                    return None
                header += chunk
            
            header = header.decode().strip()
            print(f"Header: {header}")
            
            if not header.startswith("OK|"):
                print(f"Error: {header}")
                return None
            
            # Parse header: OK|original_size|compressed_size|
            parts = header.split("|")
            if len(parts) < 3:
                print("Invalid header format")
                return None
                
            original_size = int(parts[1])
            compressed_size = int(parts[2])
            
            print(f"Original: {original_size} bytes")
            print(f"Compressed: {compressed_size} bytes")
            print("Downloading..")
            
            # Receive compressed data
            compressed_data = bytearray()
            while len(compressed_data) < compressed_size:
                remaining = compressed_size - len(compressed_data)
                chunk = sock.recv(min(1024, remaining))
                if not chunk:
                    print("Connection closed early!")
                    break
                compressed_data.extend(chunk)
                
                # Progress indicator
                progress = len(compressed_data) / compressed_size * 100
                if len(compressed_data) % 10240 == 0 or len(compressed_data) == compressed_size:
                    print(f"  {len(compressed_data)}/{compressed_size} bytes ({progress:.1f}%)")
            
            print("Download complete")
            
            # Verify we got all data
            if len(compressed_data) != compressed_size:
                print(f"Warning: Expected {compressed_size} bytes, got {len(compressed_data)}")
            
            print("Decompressing..")
            image_data = RLECompressor.decompress(bytes(compressed_data))
            print(f"Decompressed: {len(image_data)} bytes")
            
            # Verify decompressed size
            if len(image_data) != original_size:
                print(f"Warning: Expected {original_size} bytes, got {len(image_data)}")
            
            return image_data
            
        except Exception as e:
            print(f"Download error: {e}")
            import sys
            sys.print_exception(e)
            return None
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    def cleanup(self):
        if self.led:
            self.led.value(0)
        print("Client cleanup completed")



def main():
    print("\n" + "-"*50)
    print("IMAGE CLIENT STARTING")
    print("-"*50)
    
    # Check system info
    try:
        import sys
        print(f"\nSystem info:")
        print(f"  Platform: {sys.platform}")
        print(f"  Version: {sys.version}")
    except:
        pass
    
    # Configuration
    SERVER_SSID = "PicoImages"
    SERVER_IP = "192.168.4.1"  # Default AP IP
    SERVER_PORT = 8080
    
    print(f"\nConfiguration:")
    print(f"  Server SSID: {SERVER_SSID}")
    print(f"  Server IP: {SERVER_IP}:{SERVER_PORT}")
    
    # Initialise display (optional)
    display = None
    try:
        display = ImageDisplay()
    except Exception as e:
        print(f"Display init error: {e}")
    
    # Create client
    client = ImageClient(
        server_ssid=SERVER_SSID,
        server_ip=SERVER_IP,
        server_port=SERVER_PORT
    )
    
    try:
        if display:
            display.show_text("Connecting..", 10, 100)
        
        # Connect to WiFi
        if not client.connect_to_network():
            print("\n✗ Failed to connect to WiFi")
            if display:
                display.show_text("WiFi Failed", 10, 100)
            return
        
        if display:
            display.show_text("Connected!", 10, 100)
        
        utime.sleep(1)
        
        # List available images
        if display:
            display.show_text("Listing..", 10, 100)
        
        files = client.list_images()
        
        print(f"\nAvailable images ({len(files)}):")
        for f in files:
            print(f"  {f['name']} - {f['size']} bytes")
        
        # Download and display first image!
        if files:
            filename = files[0]['name']
            print(f"\nDownloading: {filename}")
            
            if display:
                display.clear()
                display.show_text(f"Loading..", 10, 100)
            
            image_data = client.get_image(filename)
            
            if image_data:
                print("Success!")
                if display:
                    display.clear()
                    display.display_image(image_data)
                print("\nImage displayed successfully!")
            else:
                print("Download failed")
                if display:
                    display.show_text("Failed", 10, 100)
        else:
            print("\nNo images found on server")
            if display:
                display.show_text("No images", 10, 100)
        
        print("\n" + "-"*50)
        print("CLIENT FINISHED")
        print("-"*50)
        
        # Clean up memory
        gc.collect()
            
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import sys
        sys.print_exception(e)
        if display:
            display.clear()
            display.show_text("Error!", 10, 100)
    finally:
        client.cleanup()

if __name__ == "__main__":
    main()