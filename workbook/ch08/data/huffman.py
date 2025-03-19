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

    return heapq.heappop(heap)

# Build Huffman Codes
def build_huffman_codes(root, code="", code_map=None):
    if code_map is None:
        code_map = {}

    if root is not None:
        if root.char is not None:
            code_map[root.char] = code
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
def write_bits_to_file(encoded_bits, output_file):
    with open(output_file, "wb") as f:
        byte_array = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte = encoded_bits[i:i+8]
            byte_array.append(int(byte, 2))
        f.write(byte_array)

# Read bits from a file
def read_bits_from_file(input_file):
    with open(input_file, "rb") as f:
        byte_array = f.read()
        bits = "".join(f"{byte:08b}" for byte in byte_array)
    return bits

# Decode the text using Huffman tree
def decode_text(encoded_bits, root):
    decoded_text = ""
    current = root
    for bit in encoded_bits:
        if bit == "0":
            current = current.left
        else:
            current = current.right

        if current.char is not None:
            decoded_text += current.char
            current = root

    return decoded_text

# Compress a file
def compress_file(input_file, output_file):
    # Read input file
    with open(input_file, "r") as f:
        text = f.read()

    # Calculate character frequencies
    freq_map = Counter(text)

    # Build Huffman tree and codes
    huffman_tree = build_huffman_tree(freq_map)
    code_map = build_huffman_codes(huffman_tree)

    # Encode the text
    encoded_bits = encode_text(text, code_map)

    # Write the encoded bits to the output file
    write_bits_to_file(encoded_bits, output_file)

    # Save the Huffman codes for decompression
    with open("huffman_codes.txt", "w") as f:
        for char, code in code_map.items():
            f.write(f"{char}:{code}\n")

    print(f"File compressed successfully: {output_file}")

# Decompress a file
def decompress_file(input_file, output_file):
    # Read the Huffman codes
    code_map = {}
    with open("huffman_codes.txt", "r") as f:
        for line in f:
            char, code = line.strip().split(":")
            code_map[char] = code

    # Rebuild the Huffman tree
    heap = [HuffmanNode(char=char, freq=0) for char in code_map.keys()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(freq=0, left=left, right=right)
        heapq.heappush(heap, parent)

    huffman_tree = heapq.heappop(heap)

    # Read the encoded bits from the input file
    encoded_bits = read_bits_from_file(input_file)

    # Decode the text
    decoded_text = decode_text(encoded_bits, huffman_tree)

    # Write the decoded text to the output file
    with open(output_file, "w") as f:
        f.write(decoded_text)

    print(f"File decompressed successfully: {output_file}")

# Main function
def main():
    input_file = "input.txt" # aaaaabbbbbcccccdddddeeeeefffffggggghhhhhiiiiijjjjj
    compressed_file = "compressed.bin"
    decompressed_file = "decompressed.txt"

    # Compress the input file
    compress_file(input_file, compressed_file)

    # Decompress the compressed file
    decompress_file(compressed_file, decompressed_file)

if __name__ == "__main__":
    main()
