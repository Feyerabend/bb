# main.py

from interpreter import SimpleRasterizer

def main():
    width, height = 100, 100
    rasterizer = SimpleRasterizer(width, height)

    # Draw a line
    rasterizer.moveto(10, 10)
    rasterizer.lineto(80, 80)

    # Draw a Bezier curve
#   rasterizer.bezier((10, 80), (50, 10), (80, 80))

    rasterizer.bezier((0, 40), (10, 60), (20, 76.37))  # First segment
    rasterizer.bezier((20, 76.37), (30, 56), (40, 9.728))  # Second segment
    rasterizer.bezier((40, 9.728), (50, 18), (60, 28.824))  # Third segment
    rasterizer.bezier((60, 28.824), (70, 50), (80, 79.576))  # Fourth segment
    rasterizer.bezier((80, 79.576), (90, 40), (100, 18.24))  # Fifth segment

    # Save to PPM
    rasterizer.save('output.ppm')

if __name__ == "__main__":
    main()