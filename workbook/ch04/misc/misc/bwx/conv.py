#!/usr/bin/env python3
"""
BMP to C Header Converter for displaybw.c
Converts a black & white BMP file (1-bit or 24-bit) to a C header file
compatible with display_blit_full_bw()
"""

import sys
import struct
from pathlib import Path

def read_bmp_header(f):
    """Read and parse BMP file header"""
    # Read BMP file header (14 bytes)
    bfType = f.read(2)
    if bfType != b'BM':
        raise ValueError("Not a valid BMP file")
    
    bfSize = struct.unpack('<I', f.read(4))[0]
    bfReserved1 = struct.unpack('<H', f.read(2))[0]
    bfReserved2 = struct.unpack('<H', f.read(2))[0]
    bfOffBits = struct.unpack('<I', f.read(4))[0]
    
    # Read DIB header (at least 40 bytes for BITMAPINFOHEADER)
    biSize = struct.unpack('<I', f.read(4))[0]
    biWidth = struct.unpack('<i', f.read(4))[0]
    biHeight = struct.unpack('<i', f.read(4))[0]
    biPlanes = struct.unpack('<H', f.read(2))[0]
    biBitCount = struct.unpack('<H', f.read(2))[0]
    biCompression = struct.unpack('<I', f.read(4))[0]
    
    return {
        'width': biWidth,
        'height': abs(biHeight),
        'bit_count': biBitCount,
        'compression': biCompression,
        'data_offset': bfOffBits,
        'height_sign': 1 if biHeight > 0 else -1  # Positive = bottom-up
    }

def convert_24bit_to_1bit(pixel_data, width, height):
    """Convert 24-bit RGB data to 1-bit black/white"""
    bytes_per_row = (width + 7) // 8
    bit_data = bytearray(bytes_per_row * height)
    
    row_size_24 = ((width * 3 + 3) // 4) * 4  # 24-bit row size with padding
    
    for y in range(height):
        for x in range(width):
            # Get RGB values
            pixel_offset = y * row_size_24 + x * 3
            b = pixel_data[pixel_offset]
            g = pixel_data[pixel_offset + 1]
            r = pixel_data[pixel_offset + 2]
            
            # Convert to grayscale and threshold
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            is_white = gray > 127
            
            # Set bit in output (MSB first)
            byte_idx = y * bytes_per_row + x // 8
            bit_idx = 7 - (x % 8)
            if is_white:
                bit_data[byte_idx] |= (1 << bit_idx)
    
    return bit_data

def convert_1bit_to_packed(pixel_data, width, height, row_size):
    """Convert 1-bit BMP data to packed format (MSB first)"""
    bytes_per_row = (width + 7) // 8
    bit_data = bytearray(bytes_per_row * height)
    
    for y in range(height):
        src_offset = y * row_size
        dst_offset = y * bytes_per_row
        
        for x in range(bytes_per_row):
            if src_offset + x < len(pixel_data):
                # BMP is typically LSB first, we need MSB first
                byte_val = pixel_data[src_offset + x]
                # Reverse bits in byte
                reversed_byte = int('{:08b}'.format(byte_val)[::-1], 2)
                bit_data[dst_offset + x] = reversed_byte
    
    return bit_data

def bmp_to_c_header(input_file, output_file=None, array_name=None):
    """Convert BMP file to C header file"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found")
        return False
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.stem + '.h'
    
    # Generate array name if not provided
    if array_name is None:
        array_name = input_path.stem.replace('-', '_').replace(' ', '_')
    
    try:
        with open(input_file, 'rb') as f:
            # Read BMP header
            header = read_bmp_header(f)
            width = header['width']
            height = header['height']
            bit_count = header['bit_count']
            
            print(f"BMP Info: {width}x{height}, {bit_count}-bit")
            
            # Check dimensions
            if width != 320 or height != 240:
                print(f"Warning: Image is {width}x{height}, but display is 320x240")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    return False
            
            # Seek to pixel data
            f.seek(header['data_offset'])
            
            # Read all pixel data
            pixel_data = f.read()
            
            # Convert to 1-bit format
            if bit_count == 1:
                row_size = ((width + 31) // 32) * 4  # 1-bit row size with padding
                bit_buffer = convert_1bit_to_packed(pixel_data, width, height, row_size)
            elif bit_count == 24:
                bit_buffer = convert_24bit_to_1bit(pixel_data, width, height)
            else:
                print(f"Error: Unsupported bit depth: {bit_count}-bit")
                print("Only 1-bit and 24-bit BMPs are supported")
                return False
        
        # Generate C header file
        with open(output_file, 'w') as f:
            guard_name = f"{array_name.upper()}_H"
            
            f.write(f"// Auto-generated from {input_path.name}\n")
            f.write(f"// Image size: {width}x{height}\n")
            f.write(f"// Format: 1-bit black & white (MSB first, bottom-up)\n\n")
            
            f.write(f"#ifndef {guard_name}\n")
            f.write(f"#define {guard_name}\n\n")
            
            f.write("#include <stdint.h>\n\n")
            
            # Write array declaration
            f.write(f"const uint8_t {array_name}_data[] = {{\n")
            
            # Write data in rows of 16 bytes
            for i in range(0, len(bit_buffer), 16):
                chunk = bit_buffer[i:i+16]
                hex_values = ', '.join(f'0x{b:02X}' for b in chunk)
                f.write(f"    {hex_values},\n")
            
            f.write("};\n\n")
            
            # Write size constants
            f.write(f"#define {array_name.upper()}_WIDTH {width}\n")
            f.write(f"#define {array_name.upper()}_HEIGHT {height}\n")
            f.write(f"#define {array_name.upper()}_SIZE {len(bit_buffer)}\n\n")
            
            f.write(f"#endif // {guard_name}\n")
        
        print(f"\nSuccess! Generated '{output_file}'")
        print(f"Array name: {array_name}_data")
        print(f"Size: {len(bit_buffer)} bytes")
        print(f"\nUsage in C code:")
        print(f'  #include "{output_file}"')
        print(f'  display_blit_full_bw({array_name}_data);')
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("BMP to C Header Converter for displaybw.c")
        print("\nUsage:")
        print(f"  {sys.argv[0]} <input.bmp> [output.h] [array_name]")
        print("\nExample:")
        print(f"  {sys.argv[0]} image.bmp image.h my_image")
        print("\nSupported formats:")
        print("  - 1-bit black & white BMP")
        print("  - 24-bit RGB BMP (will be converted to B&W)")
        print("\nRecommended image size: 320x240 pixels")
        return 1
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    array_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = bmp_to_c_header(input_file, output_file, array_name)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
