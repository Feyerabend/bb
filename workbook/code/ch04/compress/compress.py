
def rle_encode_pairs(pixel_data):
    encoded = bytearray()
    marker = b'\xFF\xFF' # special
    i = 0

    while i < len(pixel_data) - 1:
        pair = pixel_data[i:i+2]

        count = 1
        while i + 2 * count < len(pixel_data) and pixel_data[i + 2 * count:i + 2 * (count + 1)] == pair and count < 255:
            count += 1

        if count > 1:
            encoded.extend(marker)
            encoded.append(count)
            encoded.extend(pair)
            i += 2 * count
        else:
            encoded.extend(pair)
            i += 2

    # handle last byte if pixel data length is odd
    if i < len(pixel_data):
        encoded.append(pixel_data[i])

    return encoded


def rle_decode_pairs(encoded_data):
    decoded = bytearray()
    i = 0
    marker = b'\xFF\xFF' # special again

    while i < len(encoded_data):
        # if we have a marker for a repeated pair
        if encoded_data[i:i+2] == marker:
            count = encoded_data[i + 2]
            pair = encoded_data[i + 3:i + 5]
            decoded.extend(pair * count)  # repeat the pair `count` times
            i += 5  # move past the marker, count, and pair
        else:
            # pair without repetition
            decoded.extend(encoded_data[i:i+2])
            i += 2

    return decoded


def compress_ppm(ppm_data):
    lines = ppm_data.split(b'\n')
    header = b'\n'.join(lines[:3]) + b'\n'
    pixel_data = bytearray(b'\n'.join(lines[3:]))
    encoded_data = rle_encode_pairs(pixel_data)
    
    return header + encoded_data


def decompress_ppm(compressed_data):
    header_end = compressed_data.find(b'\n', compressed_data.find(b'\n', compressed_data.find(b'\n') + 1) + 1) + 1
    header = compressed_data[:header_end]
    encoded_data = compressed_data[header_end:]
    
    decoded_data = rle_decode_pairs(encoded_data)
    
    return header + decoded_data


def compare_images(original, decompressed):
    if len(original) != len(decompressed):
        print("Warning: The images have different lengths.")
        return False

    differences = []
    for index in range(len(original)):
        if original[index] != decompressed[index]:
            differences.append((index, original[index], decompressed[index]))

    if differences:
        print("Differences found:")
        for index, orig_byte, decomp_byte in differences:
            print("Index {}: Original: {} (ASCII: {}) Decompressed: {} (ASCII: {})".format(
                index, orig_byte, orig_byte, decomp_byte, decomp_byte))
        return False

    return True


def main():

    with open("input.ppm", "rb") as input_file:
        ppm_data = input_file.read()

    compressed_data = compress_ppm(ppm_data)

    with open("compressed.rle", "wb") as compressed_file:
        compressed_file.write(compressed_data)

    decompressed_data = decompress_ppm(compressed_data)

    with open("output.ppm", "wb") as decompressed_file:
        decompressed_file.write(decompressed_data)

    # Compare the original and decompressed images
    # if compare_images(ppm_data, decompressed_data):
    #    print("Success: The original and decompressed images are identical.")
    # else:
    #    print("Warning: The original and decompressed images do not match.")

if __name__ == "__main__":
    main()