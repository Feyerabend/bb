# PPM3 Image Utilities for Raspberry Pi Pico W!
# Handles PPM3 format reading, writing, and basic operations

class PPM3Image:
    def __init__(self, width=0, height=0, max_val=255):
        self.width = width
        self.height = height
        self.max_val = max_val
        self.pixels = []  # List of (r, g, b) tuples
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                # Read header
                magic = f.readline().strip()
                if magic != 'P3':
                    raise ValueError("Not a PPM3 file")
                
                # Skip comments
                line = f.readline().strip()
                while line.startswith('#'):
                    line = f.readline().strip()
                
                # Parse dimensions
                self.width, self.height = map(int, line.split())
                self.max_val = int(f.readline().strip())
                
                # Read pixel data
                self.pixels = []
                pixel_data = f.read().split()
                
                for i in range(0, len(pixel_data), 3):
                    r = int(pixel_data[i])
                    g = int(pixel_data[i + 1])
                    b = int(pixel_data[i + 2])
                    self.pixels.append((r, g, b))
                
                print(f"Loaded {self.width}x{self.height} PPM3 image")
                return True
                
        except Exception as e:
            print(f"Error loading PPM3: {e}")
            return False
    
    def save_to_file(self, filename):
        try:
            with open(filename, 'w') as f:
                # Write header
                f.write(f"P3\n")
                f.write(f"# Generated PPM3 image\n")
                f.write(f"{self.width} {self.height}\n")
                f.write(f"{self.max_val}\n")
                
                # Write pixel data
                for i, (r, g, b) in enumerate(self.pixels):
                    f.write(f"{r} {g} {b}")
                    if (i + 1) % self.width == 0:
                        f.write("\n")  # New line after each row
                    else:
                        f.write(" ")
                        
            return True
            
        except Exception as e:
            print(f"Error saving PPM3: {e}")
            return False
    
    def create_gradient(self, width, height):
        self.width = width
        self.height = height
        self.max_val = 255
        self.pixels = []
        
        for y in range(height):
            for x in range(width):
                # Create a nice gradient
                r = int(255 * x / width)
                g = int(255 * y / height)
                b = int(255 * (x + y) / (width + height))
                self.pixels.append((r, g, b))
    
    def create_test_pattern(self, width, height):
        self.width = width
        self.height = height
        self.max_val = 255
        self.pixels = []
        
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 255, 255),# White
            (0, 0, 0),      # Black
        ]
        
        block_width = width // 4
        block_height = height // 2
        
        for y in range(height):
            for x in range(width):
                block_x = x // block_width
                block_y = y // block_height
                color_index = (block_y * 4 + block_x) % len(colors)
                self.pixels.append(colors[color_index])
    
    def to_rgb565(self): # display pack
        rgb565_data = []
        for r, g, b in self.pixels:
            # Convert 8-bit RGB to 5-6-5 format
            r5 = (r >> 3) & 0x1F
            g6 = (g >> 2) & 0x3F
            b5 = (b >> 3) & 0x1F
            rgb565 = (r5 << 11) | (g6 << 5) | b5
            rgb565_data.append(rgb565)
        return rgb565_data
    
    def get_size_bytes(self):
        return len(self.pixels) * 3  # 3 bytes per pixel
    
    def print_stats(self):
        print(f"Image: {self.width}x{self.height}")
        print(f"Pixels: {len(self.pixels)}")
        print(f"Size: ~{self.get_size_bytes()} bytes")



# Example usage and test functions
def create_test_images():
    
    # Create gradient test image
    img = PPM3Image()
    img.create_gradient(240, 135)  # Display Pack resolution
    img.save_to_file("test_gradient.ppm")
    
    # Create block pattern test image
    img2 = PPM3Image()
    img2.create_test_pattern(240, 135)
    img2.save_to_file("test_pattern.ppm")
    
    print("Created test images: test_gradient.ppm, test_pattern.ppm")

def test_load_save():
    img = PPM3Image()
    if img.load_from_file("test_gradient.ppm"):
        img.print_stats()
        img.save_to_file("test_copy.ppm")
        print("Successfully loaded and saved copy")

if __name__ == "__main__":
    create_test_images()
    test_load_save()


