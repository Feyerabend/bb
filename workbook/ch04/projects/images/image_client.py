import network
import socket
import utime
import ujson
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2

#  Compression 
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


#  Network Client 
class ImageClient:
    def __init__(self, server_ssid, server_password, server_ip, server_port=8080):
        self.server_ssid = server_ssid
        self.server_password = server_password
        self.server_ip = server_ip
        self.server_port = server_port
        self.wlan = None
        
    def connect_to_server(self):
        """Connect to server's WiFi AP"""
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        print(f"Connecting to {self.server_ssid}...")
        self.wlan.connect(self.server_ssid, self.server_password)
        
        # Wait for connection
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print("Waiting for connection...")
            utime.sleep(1)
        
        if self.wlan.status() != 3:
            raise RuntimeError("Network connection failed")
        
        print("Connected!")
        print(f"IP: {self.wlan.ifconfig()[0]}")
        
    def list_images(self):
        """Get list of available images from server"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.server_ip, self.server_port))
            
            # Send LIST request
            s.send(b"LIST")
            
            # Receive response
            header = s.recv(256).decode()
            if not header.startswith("OK|"):
                print(f"Error: {header}")
                s.close()
                return []
            
            # Parse header: OK|size|
            parts = header.split("|")
            data_size = int(parts[1])
            
            # Receive JSON data
            data = s.recv(data_size).decode()
            s.close()
            
            files = ujson.loads(data)
            return files
            
        except Exception as e:
            print(f"List error: {e}")
            return []
    
    def get_image(self, filename):
        """Download and decompress image from server"""
        try:
            print(f"\nRequesting: {filename}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.server_ip, self.server_port))
            
            # Send GET request
            request = f"GET|{filename}"
            s.send(request.encode())
            
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
            
            print(f"Downloading {compressed_size} bytes...")
            
            # Receive compressed data
            compressed_data = bytearray()
            while len(compressed_data) < compressed_size:
                chunk = s.recv(min(1024, compressed_size - len(compressed_data)))
                if not chunk:
                    break
                compressed_data.extend(chunk)
                
                # Progress indicator
                progress = len(compressed_data) / compressed_size * 100
                print(f"Progress: {progress:.1f}%")
            
            s.close()
            
            print("Decompressing...")
            image_data = RLECompressor.decompress(bytes(compressed_data))
            print(f"Decompressed to {len(image_data)} bytes")
            
            return image_data
            
        except Exception as e:
            print(f"Download error: {e}")
            return None


#  Display Handler 
class ImageDisplay:
    def __init__(self):
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
        self.width = self.display.get_bounds()[0]
        self.height = self.display.get_bounds()[1]
        print(f"Display: {self.width}x{self.height}")
        
    def clear(self, color=(0, 0, 0)):
        """Clear display"""
        pen = self.display.create_pen(*color)
        self.display.set_pen(pen)
        self.display.clear()
        self.display.update()
        
    def show_text(self, text, x=10, y=10, scale=2):
        """Display text"""
        self.display.set_pen(self.display.create_pen(255, 255, 255))
        self.display.text(text, x, y, scale=scale)
        self.display.update()
        
    def display_image(self, image_data):
        """Display raw RGB565 image data"""
        # For RGB565: 2 bytes per pixel
        # Assumes image_data is in correct format for display size
        
        if len(image_data) != self.width * self.height * 2:
            print(f"Warning: Image size mismatch!")
            print(f"Expected: {self.width * self.height * 2}, Got: {len(image_data)}")
        
        # This is simplified - you'll need to convert RGB565 to display format
        # The actual implementation depends on your image format
        
        # For now, create a test pattern from the data
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


#  Main Client 
def main():
    # Initialize display
    display = ImageDisplay()
    display.clear()
    display.show_text("Starting...", 10, 100)
    
    # Connect to image server
    client = ImageClient(
        server_ssid="PicoImages",
        server_password="raspberry",
        server_ip="192.168.4.1",  # Default AP IP
        server_port=8080
    )
    
    try:
        display.show_text("Connecting...", 10, 100)
        client.connect_to_server()
        
        display.show_text("Connected!", 10, 100)
        utime.sleep(1)
        
        # List available images
        display.show_text("Listing images", 10, 100)
        files = client.list_images()
        
        print("\nAvailable images:")
        for f in files:
            print(f"  {f['name']} ({f['size']} bytes)")
        
        # Download and display first image
        if files:
            filename = files[0]['name']
            display.clear()
            display.show_text(f"Loading {filename}", 10, 100)
            
            image_data = client.get_image(filename)
            
            if image_data:
                display.clear()
                display.display_image(image_data)
                print("Success!")
            else:
                display.show_text("Download failed", 10, 100)
        else:
            display.show_text("No images found", 10, 100)
            
    except Exception as e:
        print(f"Error: {e}")
        display.clear()
        display.show_text(f"Error: {str(e)}", 10, 100)

if __name__ == "__main__":
    main()
