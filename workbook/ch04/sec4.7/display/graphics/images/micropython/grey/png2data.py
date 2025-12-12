#!/usr/bin/env python3
from PIL import Image
import sys
import os

# to do: grayscale conversion ..
def rgb_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def convert_png_to_py(input_png, output_py):
    try:
        # Open and resize image if needed
        img = Image.open(input_png)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to 320x240 if different
        if img.size != (320, 240):
            print(f"Resizing from {img.size} to (320, 240)")
            img = img.resize((320, 240), Image.Resampling.LANCZOS)
        
        width, height = img.size
        
        # Convert to RGB565 format
        print(f"Converting {width}x{height} image to RGB565 format ..")
        pixels = []
        
        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                rgb565 = rgb_to_rgb565(r, g, b)
                pixels.append(rgb565)
        
        # Write to Python file
        print(f"Writing to {output_py} ..")
        with open(output_py, 'w') as f:
            f.write("# Auto-generated image data file\n")
            f.write("# Image size: 320x240 pixels\n")
            f.write("# Format: RGB565 (16-bit color)\n\n")
            
            f.write("WIDTH = 320\n")
            f.write("HEIGHT = 240\n\n")
            
            f.write("# Image data as RGB565 values\n")
            f.write("IMAGE_DATA = bytes([\n")
            
            # Write data in chunks of 12 values per line for readability
            for i in range(0, len(pixels), 12):
                chunk = pixels[i:i+12]
                # Convert each 16-bit value to 2 bytes (big-endian)
                byte_values = []
                for val in chunk:
                    byte_values.append((val >> 8) & 0xFF)  # High byte
                    byte_values.append(val & 0xFF)          # Low byte
                
                line = "    " + ", ".join(f"0x{b:02X}" for b in byte_values)
                if i + 12 < len(pixels):
                    line += ","
                f.write(line + "\n")
            
            f.write("])\n\n")
            
            f.write("def get_pixel(x, y):\n")
            f.write("    \"\"\"Get RGB565 value for pixel at (x, y)\"\"\"\n")
            f.write("    if 0 <= x < WIDTH and 0 <= y < HEIGHT:\n")
            f.write("        idx = (y * WIDTH + x) * 2\n")
            f.write("        return (IMAGE_DATA[idx] << 8) | IMAGE_DATA[idx + 1]\n")
            f.write("    return 0\n")
        
        print(f"Converted:")
        print(f"  Output file: {output_py}")
        print(f"  File size: {os.path.getsize(output_py) / 1024:.1f} KB")
        print(f"  Image data size: {len(pixels) * 2} bytes")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_png}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python png2data.py <input.png> [output.py]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Generate output filename if not provided ..
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_data.py"
    
    convert_png_to_py(input_file, output_file)
