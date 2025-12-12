
## A Problem: No Conventional File System on a RPI Pico

Traditional computers like an ordinary Raspberry Pi, or your laptop computer have a full operating system (Linux, Windows, etc.). They use file systems (ext4, FAT32, NTFS) that organize files in folders, and can easily open, read, and stream large files from storage. We also there often have access to e.g. SD cards or very large flash storage (gigabytes). For Python we can use standard libraries like PIL/Pillow to load images.

But the *Raspberry Pi Pico* runs *bare-metal MicroPython* (no OS). It has in the original configuration only *2MB of flash memory* total, and images may take up much memory. There is no traditional file system browsing. Files are stored in a simple *LittleFS* file system, and from the start it had very limited RAM (~264KB usable), to store both image and program.


### Specific Image-Related Problems

#### *1. File Access Limitations*
```python
# This works on a regular Raspberry Pi:
from PIL import Image
img = Image.open("photo.png")  # Reads PNG, decompresses, easy!

# On Pico: PIL/Pillow doesn't exist!
# You'd need to manually parse PNG format, handle decompression...
```

The Pico uses something like LittleFS for its internal flash storage, which is much
simpler than desktop file systems. You can store files, but many standard Python
libraries don't work.


#### Memory Constraints

A 320×240 (as in the case of Pimoroni DisplayPack 2.0) image requires:
- *RGB888 (24-bit)*: 320 × 240 × 3 = *230,400 bytes* (~225 KB)
- *RGB565 (16-bit)*: 320 × 240 × 2 = *153,600 bytes* (~150 KB)

*The problem:* The original Pico only has ~264 KB of RAM total.
Loading a PNG file means:
1. PNG compressed data in memory
2. Decompression buffer
3. Decoded image data
4. Display buffer
5. Your program code and variables

This quickly exceeds available RAM.


#### No Image Decoding Libraries

PNG/JPEG files are *compressed*. On a desktop:
- Libraries handle decompression automatically
- Hardware acceleration helps

On Pico:
- No PIL, no OpenCV, no image libraries
- Would need to implement PNG/JPEG decoders in Python
  (slow and eats up memory)
- Or use C libraries (can become complex to integrate
  with other features written in Python e.g.)


### Transfer and Storage Issues

*Getting images onto the Pico:*
- Can't just drag-and-drop like a USB drive (so it requires
  special tools: do experiment with using these!)
- Limited 2MB flash (other configurations can have more)
  means you can only store a few images
- Uploading via Thonny or similar IDEs is slow

*Runtime loading:*
- Reading files from flash is relatively slow
- No streaming--must load entire file into RAM
- Can't easily swap images on-the-fly


### Converting ..

By *pre-converting* images to Python data files,
we solve these problems:

1. *No decoding needed* - Image is already in raw RGB565 format
2. *Direct memory access* - Data is immediately usable by display
3. *Predictable size* - Exactly 153,600 bytes for 320×240
4. *No file I/O overhead* - Import like any Python module
5. *Simple transfer* - Just upload `.py` files via your IDE


#### The Trade-off

*Disadvantage:*
The `.py` file is larger (~450 KB) than a compressed
PNG (~50-100 KB) because:
- Image data is stored as hex text: `0xFF, 0xA3, 0x2B...`
- No compression
- PNG decoder has to be used

*Advantage:*
No complex libraries,
no runtime decompression,
no memory surprises.


### Alternative Approaches

1. *Store raw binary files* - Would need custom file reading code, still uses lots of RAM
2. *Use external SD card* - Requires extra hardware, more complex wiring (see storage)
3. *Stream from PC via USB* - Adds latency, requires PC to be connected
4. *Use external flash* - More hardware, more complexity

