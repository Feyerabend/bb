import network
import socket
import utime
import ujson
import gc

# Try to import display, but make it optional
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
        # Ensure we have a bytes-like object we can index
        if isinstance(data, (bytes, bytearray)):
            decompressed = bytearray()
            i = 0
            while i < len(data) - 1:
                count = data[i]
                value = data[i + 1]
                # Use bytes() instead of list to satisfy buffer protocol
                decompressed.extend(bytes([value]) * count)
                i += 2
            return bytes(decompressed)
        else:
            raise TypeError(f"Expected bytes or bytearray, got {type(data)}")


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
        
    def display_image(self, image_data):
        if not self.display:
            print(f"Would display {len(image_data)} bytes")
            return
            
        if len(image_data) != self.width * self.height * 2:
            print(f"Warning: Image size mismatch!")
            print(f"Expected: {self.width * self.height * 2}, Got: {len(image_data)}")
        
        # DEBUG: Check first few pixels
        print("\nDEBUG: First 10 pixels:")
        for i in range(min(10, len(image_data) // 2)):
            idx = i * 2
            pixel = (image_data[idx] << 8) | image_data[idx + 1]
            r5 = (pixel >> 11) & 0x1F
            g6 = (pixel >> 5) & 0x3F
            b5 = pixel & 0x1F
            print(f"  Pixel {i}: raw=0x{pixel:04X}, r5={r5}, g6={g6}, b5={b5}")
        
        try:
            for y in range(min(self.height, len(image_data) // (self.width * 2))):
                for x in range(self.width):
                    idx = (y * self.width + x) * 2
                    if idx + 1 < len(image_data):
                        # Read as big-endian 16-bit value
                        pixel = (image_data[idx] << 8) | image_data[idx + 1]
                        
                        # Extract RGB565 components
                        r5 = (pixel >> 11) & 0x1F  # 5 bits red
                        g6 = (pixel >> 5) & 0x3F   # 6 bits green
                        b5 = pixel & 0x1F          # 5 bits blue
                        
                        # Scale to 8-bit (0-255) with bit replication for better accuracy
                        r = (r5 << 3) | (r5 >> 2)
                        g = (g6 << 2) | (g6 >> 4)
                        b = (b5 << 3) | (b5 >> 2)
                        
                        pen = self.display.create_pen(r, g, b)
                        self.display.set_pen(pen)
                        self.display.pixel(x, y)
            
            self.display.update()
            print("Image displayed")
        except Exception as e:
            print(f"Display image failed: {e}")
            import sys
            sys.print_exception(e)

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
            print("DEBUG: LED initialized")
        except Exception as e:
            print(f"DEBUG: LED not available: {e}")
        
    def connect_to_network(self):
        print("\n" + "="*50)
        print("INITIALIZING WIFI CLIENT")
        print("="*50)
        
        # First, make sure AP interface is OFF
        print("\nDEBUG: Checking AP interface...")
        try:
            ap = network.WLAN(network.AP_IF)
            if ap.active():
                print("DEBUG: AP interface is active, deactivating...")
                ap.active(False)
                utime.sleep(2)
                print("DEBUG: AP interface deactivated")
            else:
                print("DEBUG: AP interface already inactive")
        except Exception as e:
            print(f"DEBUG: AP interface check error: {e}")
        
        # Make sure STA WiFi is off first
        print("\nDEBUG: Resetting STA interface...")
        try:
            self.wlan = network.WLAN(network.STA_IF)
            if self.wlan.active():
                print("DEBUG: STA was active, deactivating...")
                self.wlan.active(False)
                utime.sleep(2)
                print("DEBUG: STA deactivated")
        except Exception as e:
            print(f"DEBUG: Error during reset: {e}")
        
        # Now activate it fresh
        print("\nDEBUG: Activating STA interface...")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # Wait for WiFi to actually become active
        print("DEBUG: Waiting for interface to become active...")
        max_wait = 15
        wait_count = 0
        while wait_count < max_wait and not self.wlan.active():
            print(".", end="")
            utime.sleep(0.5)
            wait_count += 1
        
        if not self.wlan.active():
            print("\nERROR: Failed to activate WiFi interface!")
            return False
        
        print(f"\nSUCCESS: WiFi interface active (took {wait_count * 0.5:.1f}s)")
        
        # Extra stabilization time
        print("DEBUG: Allowing interface to stabilize...")
        utime.sleep(3)
        
        # Try to get interface info
        try:
            mac = self.wlan.config('mac')
            mac_str = ':'.join(['%02X' % b for b in mac])
            print(f"DEBUG: MAC Address: {mac_str}")
        except Exception as e:
            print(f"DEBUG: Could not get MAC: {e}")
        
        # Scan for networks
        print(f"\nDEBUG: Scanning for networks (this may take 5-10 seconds)...")
        utime.sleep(2)
        
        try:
            networks = self.wlan.scan()
            print(f"\nDEBUG: Scan complete, found {len(networks)} networks")
            
            if networks and len(networks) > 0:
                print("\nAvailable networks:")
                found_target = False
                for net in networks:
                    try:
                        ssid = net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0]
                        rssi = net[3]
                        channel = net[2] if len(net) > 2 else '?'
                        security = net[4] if len(net) > 4 else '?'
                        
                        marker = " <-- TARGET" if ssid == self.server_ssid else ""
                        print(f"  - '{ssid}' (RSSI: {rssi}dBm, Ch: {channel}, Sec: {security}){marker}")
                        
                        if ssid == self.server_ssid:
                            found_target = True
                    except Exception as e:
                        print(f"  - <parsing error: {e}>")
                
                if found_target:
                    print(f"\nSUCCESS: Target network '{self.server_ssid}' found in scan!")
                else:
                    print(f"\nWARNING: Target network '{self.server_ssid}' NOT found in scan!")
                    print("This might be OK - will try connecting anyway...")
            else:
                print("WARNING: Scan returned empty results")
                
        except Exception as e:
            print(f"DEBUG: Scan failed: {e}")
            print("This is OK on some boards - will try connecting anyway...")
            import sys
            sys.print_exception(e)
        
        # Disconnect if already connected
        print(f"\nDEBUG: Checking current connection status...")
        if self.wlan.isconnected():
            print("DEBUG: Already connected to a network, disconnecting...")
            self.wlan.disconnect()
            utime.sleep(2)
            print("DEBUG: Disconnected")
        
        # Try to connect
        print(f"\n" + "="*50)
        print(f"CONNECTING TO: '{self.server_ssid}'")
        print("="*50)
        
        connection_success = False
        
        # Try Method 1: Empty string password (most compatible for open networks)
        try:
            print("\nDEBUG: Method 1 - Trying connect(ssid, '')...")
            self.wlan.connect(self.server_ssid, '')
            connection_success = True
            print("DEBUG: Connection request accepted")
        except Exception as e1:
            print(f"DEBUG: Method 1 failed: {e1}")
            
            # Try Method 2: SSID only
            try:
                print("\nDEBUG: Method 2 - Trying connect(ssid)...")
                self.wlan.connect(self.server_ssid)
                connection_success = True
                print("DEBUG: Connection request accepted")
            except Exception as e2:
                print(f"DEBUG: Method 2 failed: {e2}")
                
                # Try Method 3: None as password
                try:
                    print("\nDEBUG: Method 3 - Trying connect(ssid, None)...")
                    self.wlan.connect(self.server_ssid, None)
                    connection_success = True
                    print("DEBUG: Connection request accepted")
                except Exception as e3:
                    print(f"DEBUG: Method 3 failed: {e3}")
        
        if not connection_success:
            print("\nERROR: All connection methods failed!")
            return False
        
        # Wait for connection with detailed status updates
        print("\nDEBUG: Waiting for connection...")
        print("LED: Blinking = Connecting, Steady = Connected\n")
        max_wait = 40  # Longer timeout
        wait_count = 0
        last_status = None
        
        status_names = {
            0: "STAT_IDLE",
            1: "STAT_CONNECTING", 
            2: "STAT_WRONG_PASSWORD",
            3: "STAT_NO_AP_FOUND",
            -1: "STAT_CONNECT_FAIL",
            -2: "STAT_CONNECT_FAIL",
            -3: "STAT_GOT_IP"
        }
        
        while wait_count < max_wait:
            # Blink LED while connecting
            if self.led and wait_count % 2 == 0:
                self.led.value(1 if (wait_count // 2) % 2 == 0 else 0)
            status = self.wlan.status()
            
            # Print status changes
            if status != last_status:
                status_str = status_names.get(status, f"UNKNOWN({status})")
                print(f"\nDEBUG: Status changed to: {status_str}")
                last_status = status
            
            # Check if connected
            if self.wlan.isconnected():
                print(f"\n{'='*50}")
                print("CONNECTION SUCCESSFUL!")
                print("="*50)
                
                try:
                    config = self.wlan.ifconfig()
                    print(f"\nNetwork Configuration:")
                    print(f"  IP Address: {config[0]}")
                    print(f"  Netmask: {config[1]}")
                    print(f"  Gateway: {config[2]}")
                    print(f"  DNS Server: {config[3]}")
                    print(f"\nConnection time: {wait_count}s")
                except Exception as e:
                    print(f"DEBUG: Could not get config: {e}")
                
                if self.led:
                    self.led.value(1)
                    print("DEBUG: LED turned on")
                
                return True
            
            # Check for definitive error statuses
            if status in [2, 3, -1, -2]:  # Error states
                status_str = status_names.get(status, f"UNKNOWN({status})")
                print(f"\nERROR: Connection failed with status: {status_str}")
                print("\nPossible causes:")
                print("  - Server AP not running")
                print("  - SSID mismatch")
                print("  - Channel conflict")
                print("  - Too far away (weak signal)")
                return False
            
            # Progress indicator
            if wait_count % 2 == 0:
                print(".", end="")
            
            utime.sleep(1)
            wait_count += 1
        
        # Timeout
        final_status = self.wlan.status()
        final_status_str = status_names.get(final_status, f"UNKNOWN({final_status})")
        print(f"\n\nERROR: Connection timeout after {max_wait}s")
        print(f"Final status: {final_status_str}")
        print(f"Connected: {self.wlan.isconnected()}")
        
        return False
        
    def list_images(self):
        print("\n" + "="*50)
        print("LISTING IMAGES")
        print("="*50)
        sock = None
        try:
            print(f"\nDEBUG: Creating socket...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            print(f"DEBUG: Socket created, timeout=10s")
            
            print(f"DEBUG: Connecting to {self.server_ip}:{self.server_port}...")
            sock.connect((self.server_ip, self.server_port))
            print("SUCCESS: Socket connected")
            
            # Send LIST request
            print("DEBUG: Sending 'LIST' command...")
            sock.send(b"LIST\n")
            print("DEBUG: Command sent")
            
            # Receive response header
            print("DEBUG: Waiting for response header...")
            header = b""
            timeout_count = 0
            while b"\n" not in header and timeout_count < 100:
                try:
                    chunk = sock.recv(1)
                    if not chunk:
                        print("DEBUG: Connection closed by server")
                        break
                    header += chunk
                except:
                    timeout_count += 1
                    utime.sleep(0.1)
            
            if not header:
                print("ERROR: No response from server")
                return []
            
            header = header.decode().strip()
            print(f"DEBUG: Received header: '{header}'")
            
            if not header.startswith("OK|"):
                print(f"ERROR: Server returned: {header}")
                return []
            
            # Parse header
            parts = header.split("|")
            if len(parts) < 2:
                print("ERROR: Invalid header format")
                return []
            
            data_size = int(parts[1])
            print(f"DEBUG: Expecting {data_size} bytes of JSON data")
            
            # Receive JSON data
            print("DEBUG: Receiving data...")
            data = b""
            while len(data) < data_size:
                remaining = data_size - len(data)
                chunk = sock.recv(min(512, remaining))
                if not chunk:
                    print("DEBUG: Connection closed early")
                    break
                data += chunk
                if len(data) % 512 == 0:
                    print(f"DEBUG: Received {len(data)}/{data_size} bytes")
            
            print(f"DEBUG: Received {len(data)} bytes total")
            data_str = data.decode()
            print(f"DEBUG: JSON data: {data_str}")
            
            files = ujson.loads(data_str)
            print(f"\nSUCCESS: Parsed {len(files)} file(s)")
            return files
            
        except Exception as e:
            print(f"ERROR: List failed: {e}")
            import sys
            sys.print_exception(e)
            return []
        finally:
            if sock:
                try:
                    sock.close()
                    print("DEBUG: Socket closed")
                except:
                    pass
    
    def get_image(self, filename):
        print(f"\n" + "="*50)
        print(f"DOWNLOADING: {filename}")
        print("="*50)
        sock = None
        try:
            print("\nDEBUG: Creating socket...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30.0)
            print("DEBUG: Socket created, timeout=30s")
            
            print(f"DEBUG: Connecting to {self.server_ip}:{self.server_port}...")
            sock.connect((self.server_ip, self.server_port))
            print("SUCCESS: Connected")
            
            # Send GET request
            request = f"GET|{filename}\n"
            print(f"DEBUG: Sending request: {request.strip()}")
            sock.send(request.encode())
            print("DEBUG: Request sent")
            
            # Receive header
            print("DEBUG: Waiting for response header...")
            header = b""
            while b"\n" not in header:
                chunk = sock.recv(1)
                if not chunk:
                    print("ERROR: Connection closed while reading header")
                    return None
                header += chunk
            
            header = header.decode().strip()
            print(f"DEBUG: Received header: '{header}'")
            
            if not header.startswith("OK|"):
                print(f"ERROR: Server responded: {header}")
                return None
            
            # Parse header
            parts = header.split("|")
            if len(parts) < 3:
                print("ERROR: Invalid header format")
                return None
                
            original_size = int(parts[1])
            compressed_size = int(parts[2])
            
            print(f"\nFile Info:")
            print(f"  Original size: {original_size} bytes")
            print(f"  Compressed size: {compressed_size} bytes")
            print(f"  Compression ratio: {compressed_size/original_size*100:.1f}%")
            
            # Receive compressed data
            print("\nDEBUG: Downloading compressed data...")
            compressed_data = bytearray()
            last_print = 0
            
            while len(compressed_data) < compressed_size:
                remaining = compressed_size - len(compressed_data)
                chunk = sock.recv(min(1024, remaining))
                if not chunk:
                    print("\nERROR: Connection closed early!")
                    break
                compressed_data.extend(chunk)
                
                # Progress indicator
                if len(compressed_data) - last_print >= 5120 or len(compressed_data) == compressed_size:
                    progress = len(compressed_data) / compressed_size * 100
                    print(f"  Progress: {len(compressed_data)}/{compressed_size} bytes ({progress:.1f}%)")
                    last_print = len(compressed_data)
            
            if len(compressed_data) != compressed_size:
                print(f"\nWARNING: Size mismatch!")
                print(f"  Expected: {compressed_size} bytes")
                print(f"  Received: {len(compressed_data)} bytes")
            else:
                print(f"\nSUCCESS: Download complete")
            
            # Decompress - ensure we pass bytes or bytearray
            print("\nDEBUG: Decompressing...")
            print(f"DEBUG: Compressed data type: {type(compressed_data)}, length: {len(compressed_data)}")
            
            # Pass the bytearray directly - the decompress method now handles it
            image_data = RLECompressor.decompress(compressed_data)
            print(f"DEBUG: Decompressed to {len(image_data)} bytes")
            
            if len(image_data) != original_size:
                print(f"WARNING: Decompressed size mismatch!")
                print(f"  Expected: {original_size} bytes")
                print(f"  Got: {len(image_data)} bytes")
            else:
                print(f"SUCCESS: Decompression successful")
            
            return image_data
            
        except Exception as e:
            print(f"\nERROR: Download failed: {e}")
            import sys
            sys.print_exception(e)
            return None
        finally:
            if sock:
                try:
                    sock.close()
                    print("DEBUG: Socket closed")
                except:
                    pass
    
    def cleanup(self):
        print("\nDEBUG: Cleaning up client...")
        if self.led:
            self.led.value(0)
            print("DEBUG: LED turned off")
        print("Client cleanup completed")


def main():
    print("\n" + "="*70)
    print(" "*22 + "IMAGE CLIENT STARTING")
    print("="*70)
    
    # System info
    try:
        import sys
        print(f"\nSystem Information:")
        print(f"  Platform: {sys.platform}")
        print(f"  Version: {sys.version}")
        print(f"  Implementation: {sys.implementation}")
        print(f"  Free memory: {gc.mem_free()} bytes")
    except Exception as e:
        print(f"Could not get system info: {e}")
    
    # Configuration
    SERVER_SSID = "PicoImages"
    SERVER_IP = "192.168.4.1"
    SERVER_PORT = 8080
    
    print(f"\nConfiguration:")
    print(f"  Server SSID: '{SERVER_SSID}'")
    print(f"  Server IP: {SERVER_IP}")
    print(f"  Server Port: {SERVER_PORT}")
    
    # Initialize display (optional)
    print("\n" + "-"*50)
    display = None
    try:
        display = ImageDisplay()
    except Exception as e:
        print(f"Display init error: {e}")
    
    # Create client
    print("-"*50)
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
            print("\n" + "="*50)
            print("WIFI CONNECTION FAILED")
            print("="*50)
            print("\nTroubleshooting steps:")
            print("1. Make sure the SERVER Pico is running first")
            print("2. Check that SERVER shows 'SERVER READY' message")
            print("3. Try scanning for WiFi on your phone/laptop")
            print("4. Make sure both Picos have good power supply")
            print("5. Try moving them closer together")
            if display:
                display.show_text("WiFi Failed", 10, 100)
            return
        
        if display:
            display.show_text("Connected!", 10, 100)
        
        print("\nDEBUG: Waiting 2 seconds before requesting data...")
        utime.sleep(2)
        
        # List available images
        if display:
            display.show_text("Listing..", 10, 100)
        
        files = client.list_images()
        
        if files:
            print(f"\n" + "-"*50)
            print(f"Available Images: {len(files)}")
            print("-"*50)
            for f in files:
                print(f"  - {f['name']} ({f['size']} bytes)")
            
            # Download first image
            filename = files[0]['name']
            
            if display:
                display.clear()
                display.show_text(f"Loading..", 10, 100)
            
            image_data = client.get_image(filename)
            
            if image_data:
                print("\n" + "="*50)
                print("SUCCESS - IMAGE READY")
                print("="*50)
                if display:
                    display.clear()
                    display.display_image(image_data)
                    print("\nImage displayed on screen!")
            else:
                print("\n" + "="*50)
                print("DOWNLOAD FAILED")
                print("="*50)
                if display:
                    display.show_text("Failed", 10, 100)
        else:
            print("\n" + "="*50)
            print("NO IMAGES FOUND")
            print("="*50)
            if display:
                display.show_text("No images", 10, 100)
        
        print("\n" + "="*70)
        print(" "*24 + "CLIENT FINISHED")
        print("="*70)
        
        gc.collect()
        print(f"\nFinal free memory: {gc.mem_free()} bytes")
            
    except Exception as e:
        print(f"\n" + "="*50)
        print("FATAL ERROR")
        print("="*50)
        print(f"Error: {e}")
        import sys
        sys.print_exception(e)
        if display:
            display.clear()
            display.show_text("Error!", 10, 100)
    finally:
        client.cleanup()

if __name__ == "__main__":
    main()
