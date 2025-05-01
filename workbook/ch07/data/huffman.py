import heapq
import os
from collections import defaultdict, Counter

# Node for Huffman Tree
class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

# Build Huffman Tree
def build_huffman_tree(freq_map):
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, parent)

    return heapq.heappop(heap) if heap else HuffmanNode()

# Build Huffman Codes
def build_huffman_codes(root, code="", code_map=None):
    if code_map is None:
        code_map = {}

    if root is not None:
        if root.char is not None:
            code_map[root.char] = code if code else "0"  # Handle single character case
        build_huffman_codes(root.left, code + "0", code_map)
        build_huffman_codes(root.right, code + "1", code_map)

    return code_map

# Encode the text using Huffman codes
def encode_text(text, code_map):
    encoded_bits = ""
    for char in text:
        encoded_bits += code_map[char]
    return encoded_bits

# Write bits to a file
def write_bits_to_file(encoded_bits, output_file, code_map):
    # First write the header with character frequencies
    # Format: [char_count][char1][freq1]...[charN][freqN][encoded_data]
    with open(output_file, "wb") as f:
        # Save the code map for reconstruction
        frequencies = {char: len(code) for char, code in code_map.items()}
        
        # Write the number of unique characters
        f.write(len(frequencies).to_bytes(4, byteorder='big'))
        
        # Write each character and its frequency
        for char, freq in frequencies.items():
            # Write character (as byte)
            f.write(ord(char).to_bytes(4, byteorder='big'))
            # Write frequency (as int)
            f.write(freq.to_bytes(4, byteorder='big'))
        
        # Write the length of encoded bits to handle padding
        f.write(len(encoded_bits).to_bytes(8, byteorder='big'))
        
        # Write the actual encoded data
        # Convert bit string to bytes
        byte_array = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte = encoded_bits[i:i+8]
            # Pad with zeros if needed
            byte = byte.ljust(8, '0')
            byte_array.append(int(byte, 2))
        
        f.write(byte_array)

# Read the header and encoded data from a file
def read_file_for_decompression(input_file):
    with open(input_file, "rb") as f:
        # Read the number of unique characters
        char_count = int.from_bytes(f.read(4), byteorder='big')
        
        # Read each character and its frequency
        freq_map = {}
        for _ in range(char_count):
            char_code = int.from_bytes(f.read(4), byteorder='big')
            char = chr(char_code)
            freq = int.from_bytes(f.read(4), byteorder='big')
            freq_map[char] = freq
        
        # Read the length of encoded bits
        bit_length = int.from_bytes(f.read(8), byteorder='big')
        
        # Read the rest as encoded data
        byte_array = f.read()
        
        # Convert to bit string
        bit_string = ""
        for byte in byte_array:
            bit_string += f"{byte:08b}"
        
        # Truncate to actual bit length
        bit_string = bit_string[:bit_length]
        
        return freq_map, bit_string

# Rebuild Huffman tree from frequency map
def rebuild_huffman_tree(freq_map):
    # Create a modified frequency map where all frequencies are valid (>0)
    mod_freq_map = {char: max(1, freq) for char, freq in freq_map.items()}
    return build_huffman_tree(mod_freq_map)

# Decode the text using Huffman tree
def decode_text(encoded_bits, root):
    if not root:
        return ""
    
    decoded_text = ""
    current = root
    
    for bit in encoded_bits:
        if bit == "0":
            current = current.left if current.left else root
        else:
            current = current.right if current.right else root

        if current and current.char is not None:
            decoded_text += current.char
            current = root

    return decoded_text

# Compress a file
def compress_file(input_file, output_file):
    # Read input file
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Calculate character frequencies
    freq_map = Counter(text)

    # Build Huffman tree and codes
    huffman_tree = build_huffman_tree(freq_map)
    code_map = build_huffman_codes(huffman_tree)

    # Encode the text
    encoded_bits = encode_text(text, code_map)

    # Write the encoded bits to the output file
    write_bits_to_file(encoded_bits, output_file, code_map)

    # Calculate compression ratio
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    
    print(f"File compressed successfully: {output_file}")
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {ratio:.2f}%")

# Decompress a file
def decompress_file(input_file, output_file):
    # Read the frequency map and encoded bits from the input file
    freq_map, encoded_bits = read_file_for_decompression(input_file)
    
    # Rebuild the Huffman tree
    huffman_tree = rebuild_huffman_tree(freq_map)
    
    # Decode the text
    decoded_text = decode_text(encoded_bits, huffman_tree)

    # Write the decoded text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(decoded_text)

    print(f"File decompressed successfully: {output_file}")

# Main function
def main():
    input_file = "input.txt"
    compressed_file = "compressed.bin"
    decompressed_file = "decompressed.txt"

    # Compress the input file
    compress_file(input_file, compressed_file)

    # Decompress the compressed file
    decompress_file(compressed_file, decompressed_file)

if __name__ == "__main__":
    main()