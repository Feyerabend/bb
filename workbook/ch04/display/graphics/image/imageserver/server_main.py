# Main Server Application for Raspberry Pi Pico W
# Serves compressed PPM3 images over custom protocol

import os
import time
import network
from image_protocol import ImageServer
from ppm_utils import PPM3Image
from rle_compression import RLECompressor

class ImageServerApp:
    """Complete image server application"""
    
    def __init__(self, wifi_ssid, wifi_password, port=8080):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.port = port
        self.server = None
        self.wlan = None
    
    def connect_wifi(self):
        """Connect to WiFi network"""
        print("Connecting to WiFi...")
        
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(self.wifi_ssid, self.wifi_password)
        
        # Wait for connection
        timeout = 10
        while timeout > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            timeout -= 1
            time.sleep(1)
            print(".", end="")
        
        if self.wlan.status() != 3:
            print(f"\nWiFi connection failed! Status: {self.wlan.status()}")
            return False
        else:
            ip_addr = self.wlan.ifconfig()[0]
            print(f"\nWiFi connected! IP address: {ip_addr}")
            return True
    
    def setup_images(self):
        """Set up and compress images for serving"""
        print("Setting up images...")
        
        self.server = ImageServer(self.port)
        
        # Create some test images if they don't exist
        self.create_test_images()
        
        # Load and compress images
        image_files = {
            "test_pattern": "test_pattern.ppm",
            "test_gradient": "test_gradient.ppm",
            "red_screen": None,  # Will be generated
            "green_screen": None,  # Will be generated
            "blue_screen": None,  # Will be generated
        }
        
        for image_id, filename in image_files.items():
            if filename and self.file_exists(filename):
                self.compress_and_load_image(filename, image_id)
            elif filename is None:
                # Generate solid color screens
                self.create_and_load_solid_color(image_id)
        
        print(f"Server ready with {len(self.server.images)} images")
    
    def create_test_images(self):
        """Create test PPM3 images if they don't exist"""
        
        # Create test pattern
        if not self.file_exists("test_pattern.ppm"):
            print("Creating test pattern image...")
            img = PPM3Image()
            img.create_test_pattern(240, 135)
            img.save_to_file("test_pattern.ppm")
        
        # Create gradient
        if not self.file_exists("test_gradient.ppm"):
            print("Creating gradient image...")
            img = PPM3Image()
            img.create_gradient(240, 135)
            img.save_to_file("test_gradient.ppm")
    
    def create_and_load_solid_color(self, image_id):
        """Create and load a solid color image"""
        color_map = {
            "red_screen": (255, 0, 0),
            "green_screen": (0, 255, 0),
            "blue_screen": (0, 0, 255),
        }
        
        if image_id in color_map:
            color = color_map[image_id]
            
            # Create solid color image
            img = PPM3Image(240, 135)
            img.pixels = [color] * (240 * 135)
            
            # Compress and load
            compressed_data = RLECompressor.compress_with_header(
                img.width, img.height, img.pixels
            )
            
            # Save compressed data to memory (not file)
            self.server.images[image_id] = compressed_data
            
            print(f"Generated {image_id}: {len(compressed_data)} bytes")
    
    def compress_and_load_image(self, filename, image_id):
        """Compress a PPM image and load it into the server"""
        try:
            # Load PPM image
            img = PPM3Image()
            if not img.load_from_file(filename):
                print(f"Failed to load {filename}")
                return False
            
            # Analyze compression potential
            print(f"\nProcessing {filename}:")
            img.print_stats()
            
            # Compress
            compressed_data = RLECompressor.compress_with_header(
                img.width, img.height, img.pixels
            )
            
            # Calculate compression ratio
            original_size = img.get_size_bytes()
            compression_ratio = RLECompressor.calculate_compression_ratio(
                original_size, len(compressed_data)
            )
            
            print(f"Compressed: {original_size} -> {len(compressed_data)} bytes")
            print(f"Compression ratio: {compression_ratio:.1f}%")
            
            # Save compressed version to file
            compressed_filename = f"{image_id}_compressed.img"
            with open(compressed_filename, 'wb') as f:
                f.write(compressed_data)
            
            # Load into server
            self.server.load_compressed_image(compressed_filename, image_id)
            
            return True
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            return False
    
    def file_exists(self, filename):
        """Check if file exists (MicroPython compatible)"""
        try:
            with open(filename, 'r'):
                pass
            return True
        except:
            return False
    
    def print_server_info(self):
        """Print server information"""
        if self.wlan and self.wlan.status() == 3:
            ip_addr = self.wlan.ifconfig()[0]
            print("\n" + "="*50)
            print("IMAGE SERVER READY")
            print("="*50)
            print(f"Server IP: {ip_addr}")
            print(f"Port: {self.port}")
            print(f"Available images:")
            for image_id in self.server.images.keys():
                size = len(self.server.images[image_id])
                print(f"  - {image_id} ({size} bytes)")
            print("\nConnect your display client to:")
            print(f"  {ip_addr}:{self.port}")
            print("="*50)
    
    def run_server(self):
        """Run the main server loop"""
        if not self.server.start_server():
            print("Failed to start server!")
            return
        
        self.print_server_info()
        
        try:
            while True:
                print(f"\n[{time.time():.0f}] Waiting for client...")
                client_socket, addr = self.server.socket.accept()
                print(f"Client connected from {addr}")
                
                start_time = time.time()
                success = self.server.handle_client(client_socket)
                end_time = time.time()
                
                client_socket.close()
                
                if success:
                    print(f"Transfer completed in {end_time - start_time:.2f}s")
                else:
                    print("Transfer failed")
                
                print("Client disconnected")
                
        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.server.socket:
                self.server.socket.close()
            print("Server stopped")

# Configuration
WIFI_SSID = "YourWiFiNetwork"      # Replace with your WiFi SSID
WIFI_PASSWORD = "YourWiFiPassword"  # Replace with your WiFi password
SERVER_PORT = 8080

def main():
    """Main entry point for the server"""
    print("Starting Pico W Image Server...")
    print("="*40)
    
    # Create and configure server app
    app = ImageServerApp(WIFI_SSID, WIFI_PASSWORD, SERVER_PORT)
    
    # Connect to WiFi
    if not app.connect_wifi():
        print("Failed to connect to WiFi. Check credentials.")
        return
    
    # Set up images
    app.setup_images()
    
    # Run the server
    app.run_server()

def test_local():
    """Test server locally (without WiFi)"""
    print("Testing server locally...")
    
    # Create test images
    app = ImageServerApp("dummy", "dummy")
    app.create_test_images()
    
    # Test compression
    app.compress_and_load_image("test_pattern.ppm", "test_pattern")
    app.compress_and_load_image("test_gradient.ppm", "test_gradient")
    
    print("Local test completed!")

def create_sample_images():
    """Create a variety of sample images for testing"""
    print("Creating sample images...")
    
    # Solid colors
    colors = [
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("white", (255, 255, 255)),
        ("black", (0, 0, 0)),
        ("yellow", (255, 255, 0)),
        ("cyan", (0, 255, 255)),
        ("magenta", (255, 0, 255)),
    ]
    
    for color_name, rgb in colors:
        img = PPM3Image(240, 135)
        img.pixels = [rgb] * (240 * 135)
        filename = f"{color_name}_screen.ppm"
        img.save_to_file(filename)
        print(f"Created {filename}")
    
    # Checkerboard pattern
    img = PPM3Image(240, 135)
    for y in range(135):
        for x in range(240):
            if (x // 20 + y // 20) % 2 == 0:
                img.pixels.append((255, 255, 255))  # White
            else:
                img.pixels.append((0, 0, 0))        # Black
    
    img.save_to_file("checkerboard.ppm")
    print("Created checkerboard.ppm")
    
    print(f"Created {len(colors) + 2} sample images")

if __name__ == "__main__":
    # Uncomment the function you want to run:
    main()                    # Run the full server
    # test_local()            # Test locally without WiFi
    # create_sample_images()  # Create sample images