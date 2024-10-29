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

    # Draw a quadratic Bezier curve
    rasterizer.beziercurve((20, 30), (50, 10), (80, 30), (0, 255, 0))  # Green curve

    # Draw a cubic Bezier curve
    rasterizer.beziercurve((10, 90), (30, 60), (70, 60), (90, 90), (0, 0, 255))  # Blue curve

    # Save to PPM
    rasterizer.save('output.ppm')

if __name__ == "__main__":
    main()