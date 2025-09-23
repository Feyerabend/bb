# Pimoroni Display Pack Driver for Raspberry Pi Pico W
# Should handle ST7789 display and displays PPM3 images

import machine
import time
from machine import Pin, SPI

# Simple ST7789 driver for Pimoroni Display Pack
class ST7789:
    
    # Display constants
    WIDTH = 240
    HEIGHT = 135
    ROTATION = 0
    
    # ST7789 Commands
    ST7789_SWRESET = 0x01
    ST7789_SLPOUT = 0x11
    ST7789_COLMOD = 0x3A
    ST7789_MADCTL = 0x36
    ST7789_CASET = 0x2A
    ST7789_RASET = 0x2B
    ST7789_RAMWR = 0x2C
    ST7789_DISPON = 0x29
    
    def __init__(self, spi_id=0, dc_pin=16, cs_pin=17, rst_pin=21, bl_pin=20):
        # Setup SPI
        self.spi = SPI(spi_id, baudrate=62500000, sck=Pin(18), mosi=Pin(19))
        
        # Setup control pins
        self.dc = Pin(dc_pin, Pin.OUT)
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.rst = Pin(rst_pin, Pin.OUT, value=1)
        self.bl = Pin(bl_pin, Pin.OUT, value=1)  # Backlight on
        
        # Initialize display
        self.init_display()
        
        print(f"ST7789 display init ({self.WIDTH}x{self.HEIGHT})")
    
    def init_display(self):
        # Reset sequence
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(10)
        
        # Init sequence
        self.write_cmd(self.ST7789_SWRESET)
        time.sleep_ms(150)
        
        self.write_cmd(self.ST7789_SLPOUT)
        time.sleep_ms(10)
        
        # Colour mode - 16 bit RGB565
        self.write_cmd(self.ST7789_COLMOD)
        self.write_data(0x55)  # 16 bit
        
        # Memory access control
        self.write_cmd(self.ST7789_MADCTL)
        self.write_data(0x00)
        
        # Display on
        self.write_cmd(self.ST7789_DISPON)
        time.sleep_ms(10)
        
        # Set display window to full screen
        self.set_window(0, 0, self.WIDTH - 1, self.HEIGHT - 1)
    
    def write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)  # Command mode
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
    
    def write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)  # Data mode
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
    
    def set_window(self, x0, y0, x1, y1):
        # Column address
        self.write_cmd(self.ST7789_CASET)
        self.write_data(bytearray([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        
        # Row address
        self.write_cmd(self.ST7789_RASET)
        self.write_data(bytearray([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        
        # Start RAM write
        self.write_cmd(self.ST7789_RAMWR)
    
    def fill_screen(self, color):
        self.set_window(0, 0, self.WIDTH - 1, self.HEIGHT - 1)
        
        # Convert color to bytes
        color_bytes = bytearray([color >> 8, color & 0xFF])
        pixel_data = color_bytes * (self.WIDTH * self.HEIGHT)
        
        self.write_data(pixel_data)
    
    # test otherwise pen?
    def draw_pixel(self, x, y, color):
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            self.set_window(x, y, x, y)
            self.write_data(bytearray([color >> 8, color & 0xFF]))
    
    def draw_image_rgb565(self, rgb565_data, x=0, y=0, width=None, height=None):
        if width is None:
            width = self.WIDTH
        if height is None:
            height = self.HEIGHT
        
        # Ensure we don't draw outside screen bounds
        draw_width = min(width, self.WIDTH - x)
        draw_height = min(height, self.HEIGHT - y)
        
        if draw_width <= 0 or draw_height <= 0:
            return
        
        # Set drawing window
        self.set_window(x, y, x + draw_width - 1, y + draw_height - 1)
        
        # Convert RGB565 data to bytes and send
        pixel_bytes = bytearray()
        for i in range(draw_width * draw_height):
            if i < len(rgb565_data):
                color = rgb565_data[i]
                pixel_bytes.extend([color >> 8, color & 0xFF])
            else:
                pixel_bytes.extend([0, 0])  # Black for missing pixels
        
        self.write_data(pixel_bytes)
    
    def backlight(self, state):
        self.bl.value(1 if state else 0)

class DisplayPackManager:
    def __init__(self):
        self.display = ST7789()
        self.current_image = None
    
    def clear_screen(self, color=0x0000):  # Black
        self.display.fill_screen(color)
        print("Screen cleared")
    
    def show_test_pattern(self):
        print("Showing test pattern ..")
        
        # Create test pattern data
        rgb565_data = []
        
        for y in range(self.display.HEIGHT):
            for x in range(self.display.WIDTH):
                # Create a simple gradient pattern
                if y < self.display.HEIGHT // 3:
                    # Red section
                    color = ((x * 31) // self.display.WIDTH) << 11
                elif y < (2 * self.display.HEIGHT) // 3:
                    # Green section
                    color = ((x * 63) // self.display.WIDTH) << 5
                else:
                    # Blue section
                    color = (x * 31) // self.display.WIDTH
                
                rgb565_data.append(color)
        
        self.display.draw_image_rgb565(rgb565_data)
        print("Test pattern displayed")
    
    # PPM3
    def display_ppm_image(self, ppm_image):
        from ppm_utils import PPM3Image
        
        if not isinstance(ppm_image, PPM3Image):
            print("Invalid image object")
            return False
        
        print(f"Displaying PPM image: {ppm_image.width}x{ppm_image.height}")
        
        # Convert to RGB565
        rgb565_data = ppm_image.to_rgb565()
        
        # Display the image
        self.display.draw_image_rgb565(
            rgb565_data, 
            width=ppm_image.width, 
            height=ppm_image.height
        )
        
        self.current_image = ppm_image
        return True
    
    def display_compressed_image(self, compressed_data):
        from rle_compression import RLECompressor
        from ppm_utils import PPM3Image
        
        try:
            # Decompress the image
            width, height, pixels = RLECompressor.decompress_with_header(compressed_data)
            
            if width is None:
                print("Failed to decompress image")
                return False
            
            # Create PPM image object
            ppm_image = PPM3Image(width, height)
            ppm_image.pixels = pixels
            
            # Display it
            return self.display_ppm_image(ppm_image)
            
        except Exception as e:
            print(f"Error displaying compressed image: {e}")
            return False
    
    def show_loading_screen(self, message="Loading .."):
        # Clear to dark blue
        self.display.fill_screen(0x001F)  # Blue
        
        # You could add text here
        # require font.. custom 
        print(f"Loading screen: {message}")
    
    def show_error_screen(self, message="Error"):
        # Clear to red
        self.display.fill_screen(0xF800)  # Red
        
        print(f"Error screen: {message}")
    
    def set_brightness(self, on=True):
        self.display.backlight(on)


# Image display functions for the complete system
def display_from_server(server_host, image_id):
    from image_protocol import ImageClient
    
    # Init display
    display_manager = DisplayPackManager()
    display_manager.show_loading_screen("Connecting...")
    
    # Create client and request image
    client = ImageClient(server_host)
    
    print(f"Requesting image '{image_id}' from {server_host}")
    compressed_data = client.request_image(image_id)
    
    if compressed_data:
        display_manager.show_loading_screen("Decompressing...")
        
        if display_manager.display_compressed_image(compressed_data):
            print("Image displayed successfully!")
            return True
        else:
            display_manager.show_error_screen("Display Error")
            return False
    else:
        display_manager.show_error_screen("Network Error")
        return False

# Test functions
def test_display():
    print("Testing Pimoroni Display Pack ..")
    
    display_manager = DisplayPackManager()
    
    # Test 1: Clear screen
    display_manager.clear_screen(0x07E0)  # Green
    time.sleep(2)
    
    # Test 2: Test pattern
    display_manager.show_test_pattern()
    time.sleep(3)
    
    # Test 3: Create and display a simple PPM image
    from ppm_utils import PPM3Image
    
    print("Creating test PPM image ..")
    test_image = PPM3Image()
    test_image.create_test_pattern(240, 135)
    
    display_manager.display_ppm_image(test_image)
    time.sleep(3)
    
    # Test 4: Test with compressed image
    from rle_compression import RLECompressor
    
    print("Testing with compressed image ..")
    compressed_data = RLECompressor.compress_with_header(
        test_image.width, test_image.height, test_image.pixels
    )
    
    display_manager.display_compressed_image(compressed_data)
    
    print("Display tests completed!")

def main_client_loop():
    SERVER_IP = "192.168.1.100"  # Replace with server's IP :4?
    
    display_manager = DisplayPackManager()
    display_manager.clear_screen()
    
    # List of images to cycle through
    image_list = ["test_pattern", "test_gradient", "custom_image"]
    current_index = 0
    
    while True:
        try:
            image_id = image_list[current_index]
            
            if display_from_server(SERVER_IP, image_id):
                print(f"Displayed {image_id}")
                time.sleep(5)  # Show image for 5 seconds
            else:
                print(f"Failed to display {image_id}")
                time.sleep(2)
            
            # Move to next image
            current_index = (current_index + 1) % len(image_list)
            
        except KeyboardInterrupt:
            print("Client shutting down ..")
            display_manager.clear_screen()
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            display_manager.show_error_screen()
            time.sleep(5)

if __name__ == "__main__":
    test_display()


