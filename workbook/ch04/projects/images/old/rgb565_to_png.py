#!/usr/bin/env python3
"""
RGB565 to PNG Converter
Converts raw RGB565 files back to PNG for verification
"""

from PIL import Image
import struct
import sys
import os

class RGB565ToPNG:
    def __init__(self, width=320, height=240):
        self.width = width
        self.height = height
    
    def rgb565_to_rgb888(self, rgb565):
        """
        Convert 16-bit RGB565 to 24-bit RGB888
        RGB565 format: RRRRR GGGGGG BBBBB
        """
        # Extract 5-bit red, 6-bit green, 5-bit blue
        r5 = (rgb565 >> 11) & 0x1F
        g6 = (rgb565 >> 5) & 0x3F
        b5 = rgb565 & 0x1F
        
        # Scale to 8-bit with bit replication for better accuracy
        # This matches what the display code should do
        r = (r5 << 3) | (r5 >> 2)
        g = (g6 << 2) | (g6 >> 4)
        b = (b5 << 3) | (b5 >> 2)
        
        return (r, g, b)
    
    def convert(self, input_path, output_path, endian='big'):
        """
        Convert RGB565 raw binary file to PNG
        
        Args:
            input_path: Path to input .img file
            output_path: Path to output PNG file
            endian: 'big' or 'little' - byte order of RGB565 data
        """
        try:
            # Read the raw RGB565 data
            with open(input_path, 'rb') as f:
                rgb565_data = f.read()
            
            expected_size = self.width * self.height * 2
            actual_size = len(rgb565_data)
            
            print(f"File: {input_path}")
            print(f"Expected size: {expected_size:,} bytes ({self.width}x{self.height})")
            print(f"Actual size: {actual_size:,} bytes")
            
            if actual_size != expected_size:
                print(f"WARNING: Size mismatch!")
                # Try to determine dimensions
                pixels = actual_size // 2
                print(f"File contains {pixels} pixels")
            
            # Create new image
            img = Image.new('RGB', (self.width, self.height))
            
            # Unpack format based on endianness
            unpack_fmt = '>H' if endian == 'big' else '<H'
            
            # Debug: Show first 10 pixels
            print(f"\nFirst 10 pixels (endian={endian}):")
            for i in range(min(10, len(rgb565_data) // 2)):
                idx = i * 2
                rgb565 = struct.unpack_from(unpack_fmt, rgb565_data, idx)[0]
                r, g, b = self.rgb565_to_rgb888(rgb565)
                print(f"  Pixel {i}: RGB565=0x{rgb565:04X} -> RGB888=({r:3d}, {g:3d}, {b:3d})")
            
            # Convert all pixels
            pixel_count = 0
            non_black_count = 0
            
            for y in range(self.height):
                for x in range(self.width):
                    idx = (y * self.width + x) * 2
                    
                    if idx + 1 < len(rgb565_data):
                        # Unpack RGB565 value
                        rgb565 = struct.unpack_from(unpack_fmt, rgb565_data, idx)[0]
                        
                        # Convert to RGB888
                        r, g, b = self.rgb565_to_rgb888(rgb565)
                        
                        # Set pixel
                        img.putpixel((x, y), (r, g, b))
                        
                        pixel_count += 1
                        if rgb565 != 0:
                            non_black_count += 1
            
            # Save PNG
            img.save(output_path)
            
            print(f"\nConversion complete!")
            print(f"Total pixels: {pixel_count}")
            print(f"Non-black pixels: {non_black_count} ({non_black_count/pixel_count*100:.1f}%)")
            print(f"Saved: {output_path}")
            
            if non_black_count == 0:
                print("\n⚠️  WARNING: All pixels are black (0x0000)!")
                print("This suggests the .img file might be corrupted or incorrectly generated.")
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_both_endians(self, input_path, output_base):
        """
        Convert using both big and little endian to see which looks correct
        """
        base, ext = os.path.splitext(output_base)
        
        print("="*60)
        print("CONVERTING WITH BIG ENDIAN")
        print("="*60)
        big_endian_output = f"{base}_big_endian{ext}"
        self.convert(input_path, big_endian_output, endian='big')
        
        print("\n" + "="*60)
        print("CONVERTING WITH LITTLE ENDIAN")
        print("="*60)
        little_endian_output = f"{base}_little_endian{ext}"
        self.convert(input_path, little_endian_output, endian='little')
        
        print("\n" + "="*60)
        print("COMPARISON")
        print("="*60)
        print(f"Created two files to compare:")
        print(f"  1. {big_endian_output} (big endian)")
        print(f"  2. {little_endian_output} (little endian)")
        print(f"\nOpen both and see which one looks correct!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert RGB565 raw files back to PNG for verification'
    )
    parser.add_argument('input', help='Input .img file')
    parser.add_argument('output', nargs='?', help='Output PNG file (optional)')
    parser.add_argument('-e', '--endian',
                       choices=['big', 'little', 'both'],
                       default='big',
                       help='Byte order: big, little, or both (default: big)')
    parser.add_argument('-w', '--width',
                       type=int,
                       default=320,
                       help='Image width (default: 320)')
    parser.add_argument('-H', '--height',
                       type=int,
                       default=240,
                       help='Image height (default: 240)')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        base = os.path.splitext(args.input)[0]
        args.output = f"{base}_decoded.png"
    
    converter = RGB565ToPNG(width=args.width, height=args.height)
    
    if args.endian == 'both':
        converter.convert_both_endians(args.input, args.output)
    else:
        converter.convert(args.input, args.output, endian=args.endian)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Interactive mode
        print("=== RGB565 to PNG Converter ===\n")
        input_path = input("Input .img file: ").strip()
        
        if not os.path.exists(input_path):
            print(f"Error: File '{input_path}' not found!")
            sys.exit(1)
        
        output_path = input("Output PNG file (press Enter for auto): ").strip()
        if not output_path:
            base = os.path.splitext(input_path)[0]
            output_path = f"{base}_decoded.png"
        
        print("\nByte order:")
        print("  1. Big endian (default)")
        print("  2. Little endian")
        print("  3. Both (create two files to compare)")
        endian_choice = input("Choose (1-3, default 1): ").strip()
        
        endian_map = {'1': 'big', '2': 'little', '3': 'both', '': 'big'}
        endian = endian_map.get(endian_choice, 'big')
        
        print()
        converter = RGB565ToPNG()
        
        if endian == 'both':
            converter.convert_both_endians(input_path, output_path)
        else:
            converter.convert(input_path, output_path, endian=endian)
    else:
        main()
