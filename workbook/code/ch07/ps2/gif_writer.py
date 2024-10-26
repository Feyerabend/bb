# gif_writer.py

import struct

def write_gif(filename, width, height, image):
    # GIF header
    header = b'GIF89a'
    header += struct.pack('<HHB', width, height, 0b10001111)  # Width, Height, GCT Flag
    header += b'\x00'  # Background Color Index
    header += b'\x00'  # Pixel Aspect Ratio

    # Create a color palette (up to 256 colors)
    color_map = {}
    index = 0
    color_table = bytearray()

    for row in image:
        for r, g, b in row:
            color = (r, g, b)
            if color not in color_map:
                if index < 256:  # Limit to 256 colors
                    color_map[color] = index
                    color_table.extend((r, g, b))  # RGB values
                    index += 1

    # Add the color table to the header
    header += color_table

    # Image Descriptor
    header += b'\x2C'  # Image Separator
    header += struct.pack('<HHHHB', 0, 0, width, height, 0)  # Image Descriptor

    # LZW Minimum Code Size
    header += b'\x08'  # Minimum LZW Code Size

    # Image data - naive implementation with uncompressed data
    lzw_data = bytearray()
    
    # Map the image data to indices
    for row in image:
        for r, g, b in row:
            index = color_map[(r, g, b)]
            lzw_data.append(index)

    # End of Image Data
    lzw_data.append(0x00)  # Terminator

    # Combine header and image data
    gif_data = header + lzw_data

    # Write the GIF file
    with open(filename, 'wb') as f:
        f.write(gif_data)

    # GIF Trailer
    with open(filename, 'ab') as f:
        f.write(b'\x3B')  # GIF file terminator