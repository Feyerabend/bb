#!/usr/bin/env python3
"""
PNG to PPM3 Converter using Pillow
Converts PNG images to ASCII PPM3 format for use with the JPEG compressor
"""

from PIL import Image
import sys
import os
import argparse

def png_to_ppm3(input_path, output_path=None):
    """
    Convert PNG image to PPM3 (ASCII) format
    
    Args:
        input_path (str): Path to input PNG file
        output_path (str): Path for output PPM file (optional)
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    try:
        # Open and load the PNG image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if img.mode != 'RGB':
                print(f"Converting from {img.mode} to RGB mode...")
                img = img.convert('RGB')
            
            # Get image dimensions
            width, height = img.size
            print(f"Image size: {width}x{height} pixels")
            
            # Generate output filename if not provided
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = f"{base_name}.ppm"
            
            # Write PPM3 format
            with open(output_path, 'w') as f:
                # PPM3 header
                f.write("P3\n")
                f.write(f"# Converted from {input_path}\n")
                f.write(f"{width} {height}\n")
                f.write("255\n")
                
                # Write pixel data
                pixels = img.load()
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        f.write(f"{r} {g} {b}\n")
            
            print(f"Successfully converted {input_path} to {output_path}")
            return True
            
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found")
        return False
    except Image.UnidentifiedImageError:
        print(f"Error: '{input_path}' is not a valid image file")
        return False
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

def batch_convert(input_dir, output_dir=None):
    """
    Convert all PNG files in a directory to PPM3 format
    
    Args:
        input_dir (str): Directory containing PNG files
        output_dir (str): Output directory (optional)
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
    
    if not png_files:
        print(f"No PNG files found in {input_dir}")
        return
    
    print(f"Found {len(png_files)} PNG file(s)")
    
    for png_file in png_files:
        input_path = os.path.join(input_dir, png_file)
        base_name = os.path.splitext(png_file)[0]
        
        if output_dir:
            output_path = os.path.join(output_dir, f"{base_name}.ppm")
        else:
            output_path = os.path.join(input_dir, f"{base_name}.ppm")
        
        png_to_ppm3(input_path, output_path)

def create_test_image(filename="test_image.png", size=(64, 64)):
    """
    Create a test PNG image with gradient pattern
    """
    img = Image.new('RGB', size)
    pixels = img.load()
    
    for y in range(size[1]):
        for x in range(size[0]):
            # Create a colorful gradient pattern
            r = int(255 * x / size[0])
            g = int(255 * y / size[1])
            b = int(255 * (x + y) / (size[0] + size[1]))
            pixels[x, y] = (r, g, b)
    
    img.save(filename)
    print(f"Created test image: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Convert PNG images to PPM3 format')
    parser.add_argument('input', nargs='?', help='Input PNG file or directory')
    parser.add_argument('-o', '--output', help='Output PPM file or directory')
    parser.add_argument('-b', '--batch', action='store_true', 
                       help='Batch convert all PNG files in input directory')
    parser.add_argument('--create-test', action='store_true',
                       help='Create a test PNG image')
    parser.add_argument('--size', nargs=2, type=int, default=[64, 64],
                       metavar=('WIDTH', 'HEIGHT'),
                       help='Size for test image (default: 64 64)')
    
    args = parser.parse_args()
    
    # Create test image if requested
    if args.create_test:
        create_test_image("test_image.png", tuple(args.size))
        if not args.input:
            # Convert the test image we just created
            png_to_ppm3("test_image.png")
            return
    
    # Check if input is provided
    if not args.input:
        print("Error: No input file or directory specified")
        print("Use --help for usage information")
        return
    
    # Check if input exists
    if not os.path.exists(args.input):
        print(f"Error: '{args.input}' does not exist")
        return
    
    # Batch conversion
    if args.batch or os.path.isdir(args.input):
        if not os.path.isdir(args.input):
            print("Error: Input must be a directory for batch conversion")
            return
        batch_convert(args.input, args.output)
    else:
        # Single file conversion
        if os.path.isdir(args.input):
            print("Error: Input is a directory. Use --batch flag for batch conversion")
            return
        png_to_ppm3(args.input, args.output)

if __name__ == "__main__":
    # Quick usage examples
    if len(sys.argv) == 1:
        print("PNG to PPM3 Converter")
        print("=" * 20)
        print()
        print("Usage examples:")
        print("  python png_to_ppm.py image.png              # Convert single file")
        print("  python png_to_ppm.py image.png -o out.ppm   # Specify output name")
        print("  python png_to_ppm.py images/ --batch        # Convert all PNGs in directory")
        print("  python png_to_ppm.py --create-test          # Create and convert test image")
        print("  python png_to_ppm.py --create-test --size 128 128  # Custom test size")
        print()
        print("Use --help for full options")
        print()
        
        # Offer to create a test image
        response = input("Create a test image now? (y/n): ").lower().strip()
        if response == 'y' or response == 'yes':
            create_test_image()
            png_to_ppm3("test_image.png")
    else:
        main()

