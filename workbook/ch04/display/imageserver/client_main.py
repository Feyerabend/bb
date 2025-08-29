# Main Client Application for Raspberry Pi Pico W with Display Pack
# Receives and displays compressed PPM3 images

import time
import network
from machine import Pin
from display_pack_driver import DisplayPackManager, display_from_server
from image_protocol import ImageClient

class ImageClientApp:
    """Complete image client application with display"""
    
    def __init__(self, wifi_ssid, wifi_password, server_ip, server_port=8080):
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.server_ip = server_ip
        self.server_port = server_port
        self.display_manager = None
        self.wlan = None
        
        # Button setup (Display Pack has buttons A, B, X, Y)
        self.button_a = Pin(12, Pin.IN, Pin.PULL_UP)
        self.button_b = Pin(13, Pin.IN, Pin.PULL_UP)
        self.button_x = Pin(14, Pin.IN, Pin.PULL_UP)
        self.button_y = Pin(15, Pin.IN, Pin.PULL_UP)
        
        # Image playlist
        self.image_playlist = [
            "test_pattern",
            "test_gradient", 
            "red_screen",
            "green_screen",
            "blue_screen",
            "checkerboard",
        ]
        self.current_image_index = 0
        self.auto_mode = True
        self.last_button_time = 0
    
    def connect_wifi(self):
        """Connect to WiFi network"""
        print("Connecting to WiFi...")
        
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(self.wifi_ssid, self.wifi_password)
        
        # Wait for connection with progress indicator
        timeout = 15
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
            print(f"\nWiFi connected! Client IP: {ip_addr}")
            return True
    
    def init_display(self):
        """Initialize the display"""
        print("Initializing display...")
        self.display_manager = DisplayPackManager()
        self.display_manager.clear_screen(0x001F)  # Dark blue
        return True
    
    def check_buttons(self):
        """Check button states and handle input"""
        current_time = time.ticks_ms()
        
        # Debounce buttons (200ms)
        if time.ticks_diff(current_time, self.last_button_time) < 200:
            return None
        
        # Check each button (buttons are active low)
        if not self.button_a.value():
            self.last_button_time = current_time
            return 'A'
        elif not self.button_b.value():
            self.last_button_time = current_time
            return 'B'
        elif not self.button_x.value():
            self.last_button_time = current_time
            return 'X'
        elif not self.button_y.value():
            self.last_button_time = current_time
            return 'Y'
        
        return None
    
    def handle_button_press(self, button):
        """Handle button press events"""
        print(f"Button {button} pressed")
        
        if button == 'A':
            # Next image
            self.current_image_index = (self.current_image_index + 1) % len(self.image_playlist)
            self.request_and_display_current_image()
            
        elif button == 'B':
            # Previous image
            self.current_image_index = (self.current_image_index - 1) % len(self.image_playlist)
            self.request_and_display_current_image()
            
        elif button == 'X':
            # Toggle auto mode
            self.auto_mode = not self.auto_mode
            print(f"Auto mode: {'ON' if self.auto_mode else 'OFF'}")
            
        elif button == 'Y':
            # Refresh current image
            self.request_and_display_current_image()
    
    def request_and_display_current_image(self):
        """Request and display the current image from playlist"""
        image_id = self.image_playlist[self.current_image_index]
        
        print(f"Requesting image: {image_id} ({self.current_image_index + 1}/{len(self.image_playlist)})")
        
        # Show loading screen
        self.display_manager.show_loading_screen(f"Loading {image_id}...")
        
        # Request image from server
        client = ImageClient(self.server_ip, self.server_port)
        compressed_data = client.request_image(image_id)
        
        if compressed_data:
            self.display_manager.show_loading_screen("Decompressing...")
            
            if self.display_manager.display_compressed_image(compressed_data):
                print(f"Successfully displayed {image_id}")
                return True
            else:
                print(f"Failed to display {image_id}")
                self.display_manager.show_error_screen("Display Error")
                return False
        else:
            print(f"Failed to receive {image_id}")
            self.display_manager.show_error_screen("Network Error")
            return False
    
    def show_startup_screen(self):
        """Show startup information"""
        self.display_manager.show_loading_screen("Starting...")
        time.sleep(1)
        
        # Could add text overlay here if you have a font library
        print("Startup screen displayed")
    
    def show_status_info(self):
        """Print current status information"""
        current_image = self.image_playlist[self.current_image_index]
        print(f"\nStatus:")
        print(f"  Current image: {current_image} ({self.current_image_index + 1}/{len(self.image_playlist)})")
        print(f"  Auto mode: {'ON' if self.auto_mode else 'OFF'}")
        print(f"  Server: {self.server_ip}:{self.server_port}")
        if self.wlan:
            print(f"  WiFi status: {self.wlan.status()}")
    
    def run_client(self):
        """Main client loop"""
        print("Starting image client...")
        
        # Show startup screen
        self.show_startup_screen()
        
        # Initial image load
        success = self.request_and_display_current_image()
        if not success:
            print("Failed to load initial image")
        
        print("\nClient ready! Controls:")
        print("  Button A: Next image")
        print("  Button B: Previous image") 
        print("  Button X: Toggle auto mode")
        print("  Button Y: Refresh current image")
        
        last_auto_time = time.ticks_ms()
        auto_interval = 10000  # 10 seconds in auto mode
        
        try:
            while True:
                # Check for button presses
                button = self.check_buttons()
                if button:
                    self.handle_button_press(button)
                    last_auto_time = time.ticks_ms()  # Reset auto timer
                
                # Auto mode: advance images automatically
                if self.auto_mode:
                    current_time = time.ticks_ms()
                    if time.ticks_diff(current_time, last_auto_time) > auto_interval:
                        self.current_image_index = (self.current_image_index + 1) % len(self.image_playlist)
                        self.request_and_display_current_image()
                        last_auto_time = current_time
                
                # Print status occasionally
                if time.ticks_ms() % 30000 < 100:  # Every ~30 seconds
                    self.show_status_info()
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
        except KeyboardInterrupt:
            print("\nClient shutting down...")
            self.display_manager.clear_screen()
        except Exception as e:
            print(f"Client error: {e}")
            self.display_manager.show_error_screen("System Error")

class SimpleImageViewer:
    """Simplified image viewer for testing"""
    
    def __init__(self, server_ip, server_port=8080):
        self.server_ip = server_ip
        self.server_port = server_port
        self.display_manager = DisplayPackManager()
    
    def view_image(self, image_id):
        """View a single image"""
        print(f"Viewing image: {image_id}")
        
        self.display_manager.show_loading_screen(f"Loading {image_id}...")
        
        client = ImageClient(self.server_ip, self.server_port)
        compressed_data = client.request_image(image_id)
        
        if compressed_data:
            if self.display_manager.display_compressed_image(compressed_data):
                print(f"Successfully displayed {image_id}")
                return True
        
        self.display_manager.show_error_screen()
        return False
    
    def slideshow(self, image_list, delay=5):
        """Simple slideshow"""
        for image_id in image_list:
            if self.view_image(image_id):
                time.sleep(delay)
            else:
                print(f"Skipping {image_id}")
                time.sleep(1)

# Configuration - MODIFY THESE VALUES
WIFI_SSID = "YourWiFiNetwork"           # Your WiFi network name
WIFI_PASSWORD = "YourWiFiPassword"       # Your WiFi password  
SERVER_IP = "192.168.1.100"             # IP address of the server Pico W
SERVER_PORT = 8080                      # Server port (should match server)

def main():
    """Main entry point for the client"""
    print("Starting Pico W Image Display Client...")
    print("="*45)
    
    # Create client app
    app = ImageClientApp(WIFI_SSID, WIFI_PASSWORD, SERVER_IP, SERVER_PORT)
    
    # Connect to WiFi
    if not app.connect_wifi():
        print("Failed to connect to WiFi. Check credentials.")
        return
    
    # Initialize display
    if not app.init_display():
        print("Failed to initialize display.")
        return
    
    # Run the client
    app.run_client()

def test_display_only():
    """Test display without network"""
    print("Testing display only...")
    
    display_manager = DisplayPackManager()
    
    # Test sequence
    display_manager.clear_screen(0xF800)  # Red
    time.sleep(2)
    
    display_manager.clear_screen(0x07E0)  # Green  
    time.sleep(2)
    
    display_manager.clear_screen(0x001F)  # Blue
    time.sleep(2)
    
    display_manager.show_test_pattern()
    time.sleep(3)
    
    print("Display test completed!")

def simple_viewer_test():
    """Simple viewer test"""
    print("Testing simple image viewer...")
    
    viewer = SimpleImageViewer(SERVER_IP, SERVER_PORT)
    
    # Test single image
    viewer.view_image("test_pattern")
    time.sleep(3)
    
    # Test slideshow
    images = ["red_screen", "green_screen", "blue_screen"]
    viewer.slideshow(images, delay=2)

def network_test():
    """Test network connectivity only"""
    print("Testing network connectivity...")
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 10
    while timeout > 0 and wlan.status() != 3:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    
    if wlan.status() == 3:
        print(f"\nNetwork OK! IP: {wlan.ifconfig()[0]}")
        
        # Test server connection
        try:
            client = ImageClient(SERVER_IP, SERVER_PORT)
            result = client.request_image("test_pattern")
            if result:
                print(f"Server connection OK! Received {len(result)} bytes")
            else:
                print("Server connection failed!")
        except Exception as e:
            print(f"Server test error: {e}")
    else:
        print(f"\nNetwork failed! Status: {wlan.status()}")

if __name__ == "__main__":
    # Uncomment the function you want to run:
    main()                    # Run the full client
    # test_display_only()     # Test display hardware only
    # simple_viewer_test()    # Test simple image viewing
    # network_test()          # Test network connectivity only