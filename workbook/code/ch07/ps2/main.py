# main.py
from interpreter import SimpleRasterizer

def main():
    width, height = 100, 100
    rasterizer = SimpleRasterizer(width, height)

    # Draw a line
    rasterizer.moveto(10, 10)
    rasterizer.lineto(80, 80)

    # Draw a Bezier curve
    rasterizer.bezier((10, 80), (50, 10), (80, 80))

    # Save to PPM
    rasterizer.save('output.ppm')

if __name__ == "__main__":
    main()