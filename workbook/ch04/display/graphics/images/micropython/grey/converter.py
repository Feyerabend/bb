from PIL import Image
import sys

def convert_png_to_ppm(input_path, output_path, max_width=320, max_height=240):
    try:
        img = Image.open(input_path).convert('L')
        if img.mode != 'L':
            raise ValueError(f"Image mode is {img.mode}, expected 'L'")
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        width, height = img.size
        print(f"Output image size: {width}x{height}")
        pixels = list(img.getdata())
        with open(output_path, 'wb') as f:
            f.write(b'P5\n%d %d\n255\n' % (width, height))
            f.write(bytearray(pixels))
        print(f"Successfully wrote P5 PPM to {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert.py input.png output.ppm")
        sys.exit(1)
    convert_png_to_ppm(sys.argv[1], sys.argv[2])
