#!/usr/bin/env python3
"""
PNG to PPM P6 Converter
Converts PNG images to PPM P6 format
for use with MicroPython displays
"""

from PIL import Image
import sys
import os

def png_to_ppm(input_path, output_path=None, max_width=320, max_height=240):
    """
    Convert PNG to PPM P6 format
    
    Args:
        input_path: Path to input PNG file
        output_path: Path to output PPM file (optional, defaults to same name with .ppm)
        max_width: Maximum width for resizing (default 320 for Display Pack 2.0)
        max_height: Maximum height for resizing (default 240 for Display Pack 2.0)
    """
    # Open the PNG image
    try:
        img = Image.open(input_path)
        print(f"Loaded: {input_path}")
        print(f"Original size: {img.size[0]}x{img.size[1]}")
        print(f"Mode: {img.mode}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return False
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        print(f"Converting from {img.mode} to RGB...")
        img = img.convert('RGB')
    
    # Resize if larger than display
    if img.size[0] > max_width or img.size[1] > max_height:
        # Calculate aspect ratio preserving resize
        ratio = min(max_width / img.size[0], max_height / img.size[1])
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        print(f"Resizing to: {new_size[0]}x{new_size[1]}")
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Generate output path if not provided
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + '.ppm'
    
    # Write PPM P6 format
    width, height = img.size
    
    try:
        with open(output_path, 'wb') as f:
            # Write PPM P6 header
            header = f"P6\n{width} {height}\n255\n"
            f.write(header.encode('ascii'))
            
            # Write pixel data (raw RGB bytes)
            pixels = img.tobytes()
            f.write(pixels)
        
        print(f"Saved: {output_path}")
        print(f"Final size: {width}x{height}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
        return True
        
    except Exception as e:
        print(f"Error writing PPM: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python converter.py input.png [output.ppm] [width] [height]")
        print("\nExamples:")
        print("  python converter.py image.png")
        print("  python converter.py image.png output.ppm")
        print("  python converter.py image.png output.ppm 320 240")
        print("\nDefault size is 320x240 (Pimoroni Display Pack 2.0)")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    max_width = int(sys.argv[3]) if len(sys.argv) > 3 else 320
    max_height = int(sys.argv[4]) if len(sys.argv) > 4 else 240
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)
    
    success = png_to_ppm(input_path, output_path, max_width, max_height)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
