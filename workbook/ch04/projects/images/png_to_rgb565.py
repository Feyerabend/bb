#!/usr/bin/env python3
"""
PNG to RGB565 Converter for Pimoroni DisplayPack 2.0
Converts PNG images to raw RGB565 format (320x240)
"""

from PIL import Image
import struct
import sys
import os

class PNG2RGB565:
    def __init__(self, target_width=320, target_height=240):
        self.target_width = target_width
        self.target_height = target_height
    
    def rgb888_to_rgb565(self, r, g, b):
        """
        Convert 24-bit RGB (8-8-8) to 16-bit RGB565
        RGB565 format: RRRRR GGGGGG BBBBB
        """
        # Pack into RGB565: 5 bits red, 6 bits green, 5 bits blue
        r5 = (r >> 3) & 0x1F  # 5 bits
        g6 = (g >> 2) & 0x3F  # 6 bits
        b5 = (b >> 3) & 0x1F  # 5 bits
        
        # Combine into 16-bit value
        rgb565 = (r5 << 11) | (g6 << 5) | b5
        return rgb565
    
    def convert(self, input_path, output_path, resize_mode='fit', dither=False):
        """
        Convert PNG to RGB565 raw binary file
        
        Args:
            input_path: Path to input PNG file
            output_path: Path to output .img file
            resize_mode: 'fit' (maintain aspect), 'stretch' (fill), 'crop' (center crop)
            dither: Apply dithering to reduce color banding
        """
        try:
            # Open and convert to RGB
            img = Image.open(input_path)
            img = img.convert('RGB')
            
            original_size = img.size
            print(f"Original image: {original_size[0]}x{original_size[1]}")
            
            # Resize image based on mode
            if resize_mode == 'fit':
                # Maintain aspect ratio, fit within target
                img.thumbnail((self.target_width, self.target_height), Image.Resampling.LANCZOS)
                
                # Create black background
                background = Image.new('RGB', (self.target_width, self.target_height), (0, 0, 0))
                
                # Center the resized image
                offset_x = (self.target_width - img.width) // 2
                offset_y = (self.target_height - img.height) // 2
                background.paste(img, (offset_x, offset_y))
                img = background
                
            elif resize_mode == 'stretch':
                # Stretch to fill target dimensions
                img = img.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)
                
            elif resize_mode == 'crop':
                # Center crop to target dimensions
                aspect_target = self.target_width / self.target_height
                aspect_img = img.width / img.height
                
                if aspect_img > aspect_target:
                    # Image is wider, crop width
                    new_width = int(img.height * aspect_target)
                    offset = (img.width - new_width) // 2
                    img = img.crop((offset, 0, offset + new_width, img.height))
                else:
                    # Image is taller, crop height
                    new_height = int(img.width / aspect_target)
                    offset = (img.height - new_height) // 2
                    img = img.crop((0, offset, img.width, offset + new_height))
                
                img = img.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)
            
            print(f"Resized to: {img.width}x{img.height} (mode: {resize_mode})")
            
            # Apply dithering if requested
            if dither:
                img = img.convert('P', dither=Image.Dither.FLOYDSTEINBERG, palette=Image.Palette.ADAPTIVE, colors=256)
                img = img.convert('RGB')
                print("Applied Floyd-Steinberg dithering")
            
            # Convert to RGB565 and write to file
            rgb565_data = bytearray()
            
            for y in range(self.target_height):
                for x in range(self.target_width):
                    r, g, b = img.getpixel((x, y))
                    rgb565 = self.rgb888_to_rgb565(r, g, b)
                    
                    # Pack as big-endian 16-bit value
                    rgb565_data.extend(struct.pack('>H', rgb565))
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(rgb565_data)
            
            file_size = len(rgb565_data)
            print(f"Saved: {output_path} ({file_size:,} bytes)")
            print(f"Expected size: {self.target_width * self.target_height * 2:,} bytes")
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def batch_convert(self, input_dir, output_dir, resize_mode='fit', dither=False):
        """Convert all PNG files in a directory"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
        
        print(f"\nFound {len(png_files)} PNG files")
        print(f"Output directory: {output_dir}\n")
        
        for i, filename in enumerate(png_files, 1):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.img'
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"[{i}/{len(png_files)}] Converting {filename}...")
            self.convert(input_path, output_path, resize_mode, dither)
            print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert PNG images to RGB565 format for Pimoroni DisplayPack 2.0'
    )
    parser.add_argument('input', help='Input PNG file or directory')
    parser.add_argument('output', help='Output .img file or directory')
    parser.add_argument('-m', '--mode', 
                       choices=['fit', 'stretch', 'crop'],
                       default='fit',
                       help='Resize mode (default: fit)')
    parser.add_argument('-d', '--dither',
                       action='store_true',
                       help='Apply dithering to reduce color banding')
    parser.add_argument('-w', '--width',
                       type=int,
                       default=320,
                       help='Target width (default: 320)')
    parser.add_argument('-H', '--height',
                       type=int,
                       default=240,
                       help='Target height (default: 240)')
    
    args = parser.parse_args()
    
    converter = PNG2RGB565(target_width=args.width, target_height=args.height)
    
    # Check if input is directory or file
    if os.path.isdir(args.input):
        # Batch convert
        converter.batch_convert(args.input, args.output, args.mode, args.dither)
    else:
        # Single file convert
        converter.convert(args.input, args.output, args.mode, args.dither)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Interactive mode if no arguments
        print("=== PNG to RGB565 Converter ===\n")
        input_path = input("Input PNG file: ").strip()
        output_path = input("Output .img file: ").strip()
        
        if not output_path:
            output_path = os.path.splitext(input_path)[0] + '.img'
        
        print("\nResize modes:")
        print("  1. Fit (maintain aspect ratio, letterbox)")
        print("  2. Stretch (fill screen)")
        print("  3. Crop (center crop)")
        mode_choice = input("Choose mode (1-3, default 1): ").strip()
        
        mode_map = {'1': 'fit', '2': 'stretch', '3': 'crop', '': 'fit'}
        resize_mode = mode_map.get(mode_choice, 'fit')
        
        dither_choice = input("Apply dithering? (y/n, default n): ").strip().lower()
        dither = dither_choice == 'y'
        
        print()
        converter = PNG2RGB565()
        converter.convert(input_path, output_path, resize_mode, dither)
    else:
        main()
