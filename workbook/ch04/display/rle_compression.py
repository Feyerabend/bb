# Custom RLE (Run-Length Encoding) Compression
# Optimised for PPM3 images and embedded systems

import struct

# Compress list of (r,g,b) tuples using RLE
# Format: [count(1 byte), r(1 byte), g(1 byte), b(1 byte)] repeated
# Max run length: 255 pixels

class RLECompressor:    
    @staticmethod
    def compress(pixels):
        if not pixels:
            return b''
        
        compressed = bytearray()
        current_pixel = pixels[0]
        count = 1
        
        for i in range(1, len(pixels)):
            if pixels[i] == current_pixel and count < 255:
                count += 1
            else:
                # Write current run
                r, g, b = current_pixel
                compressed.extend([count, r, g, b])
                
                # Start new run
                current_pixel = pixels[i]
                count = 1
        
        # Write final run
        r, g, b = current_pixel
        compressed.extend([count, r, g, b])
        
        return bytes(compressed)

    # Decompress RLE data back to list of (r,g,b) tuples
    @staticmethod
    def decompress(compressed_data):
        if not compressed_data:
            return []
        
        pixels = []
        i = 0
        
        while i < len(compressed_data):
            if i + 3 >= len(compressed_data):
                break
                
            count = compressed_data[i]
            r = compressed_data[i + 1]
            g = compressed_data[i + 2]
            b = compressed_data[i + 3]
            
            # Add 'count' number of this pixel
            for _ in range(count):
                pixels.append((r, g, b))
            
            i += 4
        
        return pixels

    # Compress with width/height header for complete image data
    # Format: width(2 bytes), height(2 bytes), compressed_data
    @staticmethod
    def compress_with_header(width, height, pixels):
        compressed_pixels = RLECompressor.compress(pixels)
        
        # Pack header (little-endian)
        header = struct.pack('<HH', width, height)
        
        return header + compressed_pixels


    # Decompress data that includes width/height header
    # Returns: (width, height, pixels)
    @staticmethod
    def decompress_with_header(data):
        if len(data) < 4:
            return None, None, []
        
        # Unpack header
        width, height = struct.unpack('<HH', data[:4])
        
        # Decompress pixel data
        pixels = RLECompressor.decompress(data[4:])
        
        return width, height, pixels
    
    @staticmethod
    def calculate_compression_ratio(original_size, compressed_size):
        if original_size == 0:
            return 0
        return (1 - compressed_size / original_size) * 100

class RLEAnalyzer:    
    @staticmethod
    def analyze_runs(pixels):
        if not pixels:
            return {}
        
        runs = []
        current_pixel = pixels[0]
        count = 1
        
        for i in range(1, len(pixels)):
            if pixels[i] == current_pixel:
                count += 1
            else:
                runs.append(count)
                current_pixel = pixels[i]
                count = 1
        
        runs.append(count)  # Don't forget last run
        
        return {
            'total_runs': len(runs),
            'avg_run_length': sum(runs) / len(runs),
            'max_run_length': max(runs),
            'min_run_length': min(runs),
            'runs_over_10': sum(1 for r in runs if r > 10),
            'efficiency_estimate': sum(runs) / len(runs) * 4  # 4 bytes per run
        }
    
    @staticmethod
    def print_analysis(pixels):
        analysis = RLEAnalyzer.analyze_runs(pixels)
        
        print("RLE Compression Analysis:")
        print(f"  Total pixel runs: {analysis['total_runs']}")
        print(f"  Average run length: {analysis['avg_run_length']:.2f}")
        print(f"  Max run length: {analysis['max_run_length']}")
        print(f"  Min run length: {analysis['min_run_length']}")
        print(f"  Runs over 10 pixels: {analysis['runs_over_10']}")
        print(f"  Estimated bytes per pixel: {analysis['efficiency_estimate'] / len(pixels):.2f}")



# Test and demo
def test_rle_compression():
    
    # Test 1: Solid color (best case)
    print("Test 1: Solid red image (100 pixels)")
    solid_pixels = [(255, 0, 0)] * 100
    compressed = RLECompressor.compress(solid_pixels)
    decompressed = RLECompressor.decompress(compressed)
    
    print(f"  Original: {len(solid_pixels) * 3} bytes")
    print(f"  Compressed: {len(compressed)} bytes")
    print(f"  Compression: {RLECompressor.calculate_compression_ratio(len(solid_pixels) * 3, len(compressed)):.1f}%")
    print(f"  Correct: {solid_pixels == decompressed}")
    
    # Test 2: Alternating pattern (worst case)
    print("\nTest 2: Alternating colors (100 pixels)")
    alt_pixels = [(255, 0, 0) if i % 2 == 0 else (0, 255, 0) for i in range(100)]
    compressed = RLECompressor.compress(alt_pixels)
    decompressed = RLECompressor.decompress(compressed)
    
    print(f"  Original: {len(alt_pixels) * 3} bytes")
    print(f"  Compressed: {len(compressed)} bytes")
    print(f"  Compression: {RLECompressor.calculate_compression_ratio(len(alt_pixels) * 3, len(compressed)):.1f}%")
    print(f"  Correct: {alt_pixels == decompressed}")
    
    # Test 3: Gradient with analysis
    print("\nTest 3: Simple gradient")
    gradient_pixels = [(i, i, i) for i in range(256)]
    RLEAnalyzer.print_analysis(gradient_pixels)
    
    compressed = RLECompressor.compress(gradient_pixels)
    print(f"  Original: {len(gradient_pixels) * 3} bytes")
    print(f"  Compressed: {len(compressed)} bytes")
    print(f"  Compression: {RLECompressor.calculate_compression_ratio(len(gradient_pixels) * 3, len(compressed)):.1f}%")

def compress_ppm_file(input_filename, output_filename):
    from ppm_utils import PPM3Image
    
    # Load image
    img = PPM3Image()
    if not img.load_from_file(input_filename):
        print(f"Failed to load {input_filename}")
        return False
    
    # Analyze before compression
    print(f"\nAnalyzing {input_filename}:")
    RLEAnalyzer.print_analysis(img.pixels)
    
    # Compress with header
    compressed_data = RLECompressor.compress_with_header(
        img.width, img.height, img.pixels
    )
    
    # Save compressed data
    try:
        with open(output_filename, 'wb') as f:
            f.write(compressed_data)
        
        original_size = img.get_size_bytes()
        compressed_size = len(compressed_data)
        
        print(f"\nCompression Results:")
        print(f"  Original size: {original_size} bytes")
        print(f"  Compressed size: {compressed_size} bytes")
        print(f"  Compression ratio: {RLECompressor.calculate_compression_ratio(original_size, compressed_size):.1f}%")
        print(f"  Saved to: {output_filename}")
        
        return True
        
    except Exception as e:
        print(f"Error saving compressed file: {e}")
        return False

def decompress_to_ppm(input_filename, output_filename):
    from ppm_utils import PPM3Image
    
    try:
        # Load compressed data
        with open(input_filename, 'rb') as f:
            compressed_data = f.read()
        
        # Decompress
        width, height, pixels = RLECompressor.decompress_with_header(compressed_data)
        
        if width is None:
            print("Failed to decompress data")
            return False
        
        # Create and save PPM image
        img = PPM3Image(width, height)
        img.pixels = pixels
        
        if img.save_to_file(output_filename):
            print(f"Decompressed to {output_filename}")
            return True
        else:
            print("Failed to save decompressed image")
            return False
            
    except Exception as e:
        print(f"Error decompressing: {e}")
        return False

if __name__ == "__main__":
    test_rle_compression()
